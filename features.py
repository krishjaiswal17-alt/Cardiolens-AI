import numpy as np
from scipy.signal import find_peaks

def detect_peaks(signal, fs):
    """
    Identifies pulse crest peaks from the POS rPPG signal purely for HRV mappings.
    Maintains adaptive median absolute deviation (MAD) filtering for outlier rejection.
    """
    distance = int(0.3 * fs) # Allow mapping up to 200 BPM for intense exit-scans
    prominence = 0.25 * np.std(signal) # More robust threshold for noisy signals
    
    peaks, _ = find_peaks(signal, distance=distance, prominence=prominence)
    
    if len(peaks) < 3:
        return peaks
        
    intervals = np.diff(peaks)
    median_int = np.median(intervals)
    mad = np.median(np.abs(intervals - median_int))
    
    threshold = 3 * mad
    valid_peaks = [peaks[0]]
    
    for i in range(1, len(peaks)):
        current_interval = peaks[i] - valid_peaks[-1]
        if abs(current_interval - median_int) > threshold:
            continue
        valid_peaks.append(peaks[i])
        
    return np.array(valid_peaks)

def calculate_hr(signal, fs, last_bpm=None):
    """
    Transforms pulse estimation mathematically to Spectral Fast Fourier Transforms.
    Integrates an aggressive Exponential Moving Average (EMA) to prevent mathematical instability
    from registering as physical jitter.
    """
    if len(signal) < fs * 3:
        return None
        
    sig = signal - np.mean(signal)
    
    # Compute FFT
    fft_vals = np.abs(np.fft.rfft(sig))
    fft_freqs = np.fft.rfftfreq(len(sig), 1.0/fs)
    
    # Target biological human pulse band (0.83 Hz to 3.0 Hz = 50 BPM to 180 BPM)
    hr_band = (fft_freqs >= 0.83) & (fft_freqs <= 3.0)
    
    if not np.any(hr_band):
        return int(last_bpm) if last_bpm else 72
        
    valid_freqs = fft_freqs[hr_band]
    raw_vals = fft_vals[hr_band]
    
    # Run a mathematical 3-point smoothing convolution neutralizing sharp artifact noise peaks!
    valid_vals = np.convolve(raw_vals, [0.33, 0.34, 0.33], mode='same')
    
    # Identify harmonics vs fundamental gracefully
    from scipy.signal import find_peaks
    ft_peaks, _ = find_peaks(valid_vals)
    if len(ft_peaks) > 0:
        sorted_peaks = sorted(ft_peaks, key=lambda i: valid_vals[i], reverse=True)
        dom_idx = sorted_peaks[0]
        max_power = valid_vals[dom_idx]
        
        # If any lower frequency peak holds at least 60% of the max power, it is the true fundamental
        # and the max is merely a harmonic!
        lowest_valid_idx = dom_idx
        for idx in sorted_peaks:
            if valid_freqs[idx] < valid_freqs[lowest_valid_idx] and valid_vals[idx] > max_power * 0.6:
                lowest_valid_idx = idx
                
        dom_freq = valid_freqs[lowest_valid_idx]
    else:
        dom_freq = valid_freqs[np.argmax(valid_vals)]
    
    raw_hr = int(dom_freq * 60)
    
    # --- EXPONENTIAL MOVING AVERAGE (EMA) & HARD CAP ---
    if last_bpm is not None and last_bpm > 0:
        if abs(raw_hr - last_bpm) > 15:
            capped_raw = last_bpm + 15 if raw_hr > last_bpm else last_bpm - 15
            hr = (capped_raw * 0.1) + (last_bpm * 0.9)
        else:
            hr = (raw_hr * 0.3) + (last_bpm * 0.7)
    else:
        hr = raw_hr

    # Extreme biological clamps strictly bound between 50 and 160
    return int(np.clip(hr, 50, 160))

def compute_hrv(peaks, fs, last_hrv=None):
    """
    Time-domain R-R interval analysis for Heart Rate Variability (HRV).
    Applies EMA dampening matching the HR arrays.
    """
    if len(peaks) < 3:
        return {"rmssd": 35, "sdnn": 45}
        
    rr_intervals_ms = (np.diff(peaks) / float(fs)) * 1000.0 
    
    # Ectopic Beat Interpolation (replace massive gaps with rolling median)
    med_rr = np.median(rr_intervals_ms)
    for i in range(len(rr_intervals_ms)):
        if np.abs(rr_intervals_ms[i] - med_rr) > 250.0:  # artifact bound
            rr_intervals_ms[i] = med_rr
            
    valid_rr = rr_intervals_ms[(rr_intervals_ms >= 330.0) & (rr_intervals_ms <= 1500.0)]
    if len(valid_rr) < 2:
        return {"rmssd": 35, "sdnn": 45}
    
    successive_differences = np.diff(valid_rr)
    valid_diffs = successive_differences[np.abs(successive_differences) < 150.0]
    
    if len(valid_diffs) == 0:
        raw_rmssd = 0
    else:
        raw_rmssd = np.sqrt(np.mean(valid_diffs**2))
    
    sdnn = np.std(valid_rr)
    
    # EMA Integration mapped across
    if last_hrv is not None and last_hrv > 0:
        rmssd = (raw_rmssd * 0.2) + (last_hrv * 0.8)
    else:
        rmssd = raw_rmssd
        
    return {
        "rmssd": int(max(15, min(rmssd, 120))),
        "sdnn": int(max(20, min(sdnn, 150)))
    }

def calculate_sqi(signal, fs, peaks=None):
    """
    Signal Quality Index combining Spectral SNR mapping.
    """
    if len(signal) < fs * 2:
        return 0
        
    signal = signal - np.mean(signal)
    fft_vals = np.abs(np.fft.rfft(signal))
    fft_freqs = np.fft.rfftfreq(len(signal), 1.0/fs)
    
    hr_band = (fft_freqs >= 0.7) & (fft_freqs <= 3.0)
    if not np.any(hr_band):
        return 45
        
    power_hr = np.sum(fft_vals[hr_band]**2)
    
    # Calculate total power strictly within the biological variance band
    bio_band = (fft_freqs >= 0.5) & (fft_freqs <= 4.0)
    power_total = np.sum(fft_vals[bio_band]**2)
    
    if power_total == 0:
        return 50
        
    snr = power_hr / power_total
    confidence = min(max((snr - 0.30) * 150, 0), 100)
            
    return int(confidence)


def compute_breathing_rate(signal, fs):
    if len(signal) < fs * 3: return 0
    signal = signal - np.mean(signal)
    fft_vals = np.abs(np.fft.rfft(signal))
    fft_freqs = np.fft.rfftfreq(len(signal), 1.0/fs)
    resp_band = (fft_freqs >= 0.1) & (fft_freqs <= 0.4)
    if not np.any(resp_band): return 0
    valid_freqs = fft_freqs[resp_band]
    valid_vals = fft_vals[resp_band]
    dom_freq = valid_freqs[np.argmax(valid_vals)]
    breathing_rate = int(dom_freq * 60)
    return max(6, min(breathing_rate, 30))

def compute_blood_perfusion(ac_signal, raw_dc_mean):
    if raw_dc_mean == 0 or len(ac_signal) == 0: return 0.0
    ac_amp = np.std(ac_signal)
    bpi = (ac_amp / raw_dc_mean) * 100.0
    return round(float(bpi), 2)
