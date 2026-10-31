import math

def calculate_pseudoprobability(hr, hrv, baseline_hr, baseline_hrv, age=35):
    """
    Computes a simulated Machine Learning risk probability score (0.0 to 1.0)
    using a logistic-style function based on deviations from personal baselines
    and demographic inputs.
    """
    # Use generic healthy baselines if historical baselines are not available
    if baseline_hr is None or baseline_hrv is None:
        baseline_hr = 70.0
        baseline_hrv = 45.0
        
    # Calculate Z-score equivalents (deviation from baseline)
    # Assuming standard deviations for healthy individuals
    hr_z = (hr - baseline_hr) / 10.0
    hrv_z = (baseline_hrv - hrv) / 15.0  # inverse because lower HRV is worse
    
    # Age factor: risk slightly increases with age fundamentally
    age_factor = (age - 30) * 0.015
    
    # Logistic function weights
    # w_0 + w_1*hr_z + w_2*hrv_z + w_3*interaction + age_factor
    logit = -3.5 + (1.2 * hr_z) + (1.5 * hrv_z) + (0.8 * hr_z * hrv_z) + age_factor
    
    # Sigmoid to get probability bounds between 0 and 1
    probability = 1.0 / (1.0 + math.exp(-max(min(logit, 10), -10)))
    return probability

def evaluate_stress(hr, hrv, baseline_hr=None, baseline_hrv=None):
    """
    Evaluates stress level contextually based on personal baselines.
    """
    rmssd = hrv.get("rmssd", 0) if isinstance(hrv, dict) else hrv
    
    if hr == 0 or rmssd == 0:
        return "Unknown"
        
    b_hr = baseline_hr if baseline_hr else 75
    b_hrv = baseline_hrv if baseline_hrv else 40

    if rmssd < b_hrv * 0.6 and hr > b_hr * 1.15:
        return "High"
    elif rmssd < b_hrv * 0.85 and hr > b_hr * 1.05:
        return "Medium"
    elif rmssd >= b_hrv * 0.85 and hr <= b_hr * 1.05:
        return "Low"
    else:
        return "Medium"

def evaluate_cardiac_risk(hr, hrv, stress_level, baseline_hr=None, baseline_hrv=None, age=35):
    """
    Computes a cardiac risk level contextually and provides a probability-based reason.
    """
    rmssd = hrv.get("rmssd", 0) if isinstance(hrv, dict) else hrv
    
    if hr == 0:
        return "Unknown", "Insufficient data to calculate risk."
        
    prob = calculate_pseudoprobability(hr, rmssd, baseline_hr, baseline_hrv, age)
    
    if prob > 0.75:
        return "High", f"Critical warning: The probabilistic model estimates a {prob*100:.1f}% risk signature for elevated cardiovascular strain. Severe deviation from your physiological baseline."
    elif prob > 0.40:
        return "Moderate", f"Elevated warning: The model detected a {prob*100:.1f}% risk score indicating fatigue, physiological stress, or acute suppression of parasympathetic activity."
    else:
        return "Low", f"Optimal vitals. The probabilistic risk score is very low ({prob*100:.1f}%), indicating your heart rate and variability are aligned with healthy resting baselines."

def calculate_health_score(hr, hrv, stress_level, sqi, baseline_hr=None, baseline_hrv=None):
    """
    Computes an overall out-of-100 health score dynamically based on baselines.
    Uses continuous bounded formulas to avoid random or unstable fluctuations.
    """
    rmssd = hrv.get("rmssd", 0) if isinstance(hrv, dict) else hrv
    if hr == 0:
        return 0
        
    score = 100.0
    
    b_hr = baseline_hr if baseline_hr else 72.0
    b_hrv = baseline_hrv if baseline_hrv else 45.0
    
    # 1. HR Component (Continuous penalty for elevated or dangerously low HR)
    hr_ratio = hr / b_hr
    if hr_ratio > 1.0:
        hr_penalty = 35 * (1.0 - 1.0 / (1.0 + math.exp(5 * (hr_ratio - 1.15))))
        score -= max(0, hr_penalty)
    elif hr_ratio < 0.65:
        hr_penalty = 25 * (1.0 - 1.0 / (1.0 + math.exp(-10 * (hr_ratio - 0.55))))
        score -= max(0, hr_penalty)

    # 2. HRV Component (Continuous penalty for suppressed variability)
    if b_hrv > 0 and rmssd < b_hrv:
        hrv_ratio = rmssd / b_hrv
        # Linear degradation for lower HRV
        hrv_penalty = 35 * (1.0 - hrv_ratio)
        score -= hrv_penalty
        
    # 3. Stress Component (Fixed but smaller bounds)
    if stress_level == "High":
        score -= 15
    elif stress_level == "Medium":
        score -= 5
        
    # 4. Signal quality scaling (Smooth degradation instead of hard cap)
    if sqi < 70:
        quality_factor = 0.8 + (0.2 * (sqi / 70.0))
        score *= quality_factor
        
    return int(max(0, min(score, 100)))

def generate_risk_flags(entry_vitals, exit_vitals, historical_baseline=None):
    """
    Compares Entry vs Exit vitals and returns explicit Risk Classification: High, Medium, Low.
    entry_vitals, exit_vitals = dicts containing: {'hr': float, 'hrv': float, 'stress': float}
    """
    hr_increase = exit_vitals['hr'] - entry_vitals['hr']
    hrv_drop = entry_vitals['hrv'] - exit_vitals['hrv']
    
    if hr_increase > 20 and hrv_drop > 15:
        return [{'status': 'HIGH RISK', 'class': 'badge-critical', 'desc': 'High cardiac stress detected'}]
    elif hr_increase > 10 or hrv_drop > 5:
        return [{'status': 'MEDIUM RISK', 'class': 'badge-warning', 'desc': 'Moderate change detected'}]
    else:
        return [{'status': 'LOW RISK', 'class': 'badge-optimal', 'desc': 'Optimal recovery. Stay hydrated.'}]
