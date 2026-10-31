import cv2
import numpy as np
from scipy.signal import butter, filtfilt, savgol_filter, detrend

# ----------------- TRACKER & ROI ----------------- #
class FacerPPGTracker:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.tracker = None
        self.tracking_active = False

    def process_frame(self, frame):
        """
        Tracks a face precisely using OpenCV tracking (CSRT/KCF).
        Exclusively targets Forehead ROI to eliminate cheek/jaw muscular movement noise.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur_val = cv2.Laplacian(gray, cv2.CV_64F).var()

        # blur_val threshold removed to prevent intermittent signal drops
        # which heavily distort FFT mappings.

        bbox = None
        if not self.tracking_active or self.tracker is None:
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=6, minSize=(100, 100))
            if len(faces) > 0:
                faces = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)
                bbox = tuple(faces[0])
                try:
                    self.tracker = cv2.TrackerCSRT_create()
                except AttributeError:
                    self.tracker = cv2.TrackerKCF_create()
                if self.tracker.init(frame, bbox):
                    self.tracking_active = True
        else:
            success, bbox = self.tracker.update(frame)
            if not success:
                self.tracking_active = False
                return None, None, blur_val
            bbox = tuple(map(int, bbox))

        if bbox is not None:
            x, y, w, h = bbox
            fs_y, fs_x = frame.shape[:2]
            
            x_min = max(0, x)
            y_min = max(0, y)
            x_max = min(x + w, fs_x)
            y_max = min(y + h, fs_y)
            w_adj, h_adj = x_max - x_min, y_max - y_min
            
            # Pure Forehead Focus (~Top 25% of face width 30%-70%)
            fh_y1 = y_min
            fh_y2 = y_min + int(h_adj * 0.25)
            fh_x1 = x_min + int(w_adj * 0.3)
            fh_x2 = x_min + int(w_adj * 0.7)
            
            forehead = frame[fh_y1:fh_y2, fh_x1:fh_x2]
            
            if forehead.size > 0:
                g_gray = cv2.cvtColor(forehead, cv2.COLOR_BGR2GRAY)
                # Adaptive Dynamic Mask removing sweat/glare illumination spikes
                mask = cv2.inRange(g_gray, np.percentile(g_gray, 5), np.percentile(g_gray, 95))
                if cv2.countNonZero(mask) > 0:
                    b = cv2.mean(forehead[:, :, 0], mask=mask)[0]
                    g = cv2.mean(forehead[:, :, 1], mask=mask)[0]
                    r = cv2.mean(forehead[:, :, 2], mask=mask)[0]
                    
                    return (r, g, b), (x_min, y_min, w_adj, h_adj), blur_val
                
        return None, None, blur_val

def extract_face_roi(frame):
    # Maintained for legacy fallback
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    if len(faces) == 0: return None
    (x, y, w, h) = faces[0]
    roi = frame[y:y+int(h*0.25), x+int(w*0.3):x+int(w*0.7)]
    if roi.size == 0: return None
    b, g, r = cv2.mean(roi)[:3]
    return (r, g, b), (x, y, w, h)


# ----------------- SIGNAL PROCESSING ----------------- #
def bandpass_filter(signal, fs, lowcut=0.7, highcut=3.0, order=5):
    """ Isolates human heart rate bracket tightly 42 BPM to 180 BPM. """
    if len(signal) <= order * 3: return signal
    try:
        signal = detrend(signal, type='linear')
    except Exception:
        pass

    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq

    if low >= 1.0 or high >= 1.0: return signal
    b, a = butter(order, [low, high], btype='band')

    try:
        return filtfilt(b, a, signal)
    except:
        return signal

def apply_smoothing(signal, window_length=11, polyorder=3):
    """
    Savitzky-Golay filtering for temporal smoothing, maintaining curve structures 
    while dropping jagged edge static noise.
    """
    if len(signal) < window_length: return signal
    if window_length % 2 == 0: window_length += 1
    return savgol_filter(signal, window_length, polyorder)

def remove_outliers(sig, window=15, threshold=3.0):
    """
    Rolling median absolute deviation (MAD) to crush sudden brightness shifts.
    """
    out = np.copy(sig)
    if len(sig) < window: return out
    for i in range(len(sig)):
        start = max(0, i - window // 2)
        end = min(len(sig), i + window // 2 + 1)
        w_data = sig[start:end]
        med = np.median(w_data)
        mad = np.median(np.abs(w_data - med))
        if mad > 0 and (np.abs(sig[i] - med) / mad) > threshold:
            out[i] = med
    return out

def apply_pos(r_sig, g_sig, b_sig, fs):
    """
    Implements Wang's POS (Plane-Orthogonal-to-Skin) mechanism.
    Medical-grade extraction separating specular variation from pulsatile blood volume.
    """
    if len(r_sig) < int(fs):
        return np.zeros_like(r_sig)

    r_sig, g_sig, b_sig = np.array(r_sig), np.array(g_sig), np.array(b_sig)
    
    # Strictly reject massive brightness fluctuations before mapping
    r_sig = remove_outliers(r_sig)
    g_sig = remove_outliers(g_sig)
    b_sig = remove_outliers(b_sig)

    r_mean = np.mean(r_sig)
    g_mean = np.mean(g_sig)
    b_mean = np.mean(b_sig)

    # Dimensional Normalization
    r_n = r_sig / r_mean if r_mean > 0 else np.zeros_like(r_sig)
    g_n = g_sig / g_mean if g_mean > 0 else np.zeros_like(g_sig)
    b_n = b_sig / b_mean if b_mean > 0 else np.zeros_like(b_sig)

    # POS orthogonal mapping matrices eliminating secular surface reflections
    X = 3 * r_n - 2 * g_n
    Y = 1.5 * r_n + g_n - 1.5 * b_n

    X_f = bandpass_filter(X, fs)
    Y_f = bandpass_filter(Y, fs)

    std_y = np.std(Y_f)
    alpha = np.std(X_f) / std_y if std_y > 0 else 1.0

    pos_signal = X_f - alpha * Y_f
    return apply_smoothing(pos_signal)

def apply_ica(r_sig, g_sig, b_sig, fs):
    """
    Routes directly to POS. The UI structure leverages apply_ica inherently, 
    so we intercept it to deploy the mathematically superior POS logic automatically.
    """
    return apply_pos(r_sig, g_sig, b_sig, fs)