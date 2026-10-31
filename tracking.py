import pandas as pd
import sqlite3
import os
import datetime
import numpy as np

DB_FILE = "cardiolens.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT, created_at TEXT)''')
    # Scans table
    c.execute('''CREATE TABLE IF NOT EXISTS scans
                 (timestamp TEXT, scan_type TEXT, username TEXT, hr REAL, hrv REAL, 
                  stress_score REAL, health_score REAL, risk_level TEXT)''')
    conn.commit()
    conn.close()

def register_user(username, password):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    if c.fetchone():
        conn.close()
        return False
    c.execute("INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)",
              (username, password, datetime.datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()
    return True

def authenticate_user(username, password):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    res = c.fetchone()
    conn.close()
    return res is not None

def save_session(hr, hrv, stress_level, health_score, risk_level, scan_type="entry", username="guest"):
    init_db()
    stress_map = {"Low": 20, "Medium": 50, "High": 80}
    
    if isinstance(stress_level, str):
        stress_score = stress_map.get(stress_level, 50)
    else:
        stress_score = stress_level
        
    hrv_val = hrv.get("rmssd", 0) if isinstance(hrv, dict) else hrv
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''INSERT INTO scans (timestamp, scan_type, username, hr, hrv, stress_score, health_score, risk_level) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (timestamp, scan_type, username, hr, hrv_val, stress_score, health_score, risk_level))
    conn.commit()
    conn.close()

def load_data():
    init_db()
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM scans", conn)
    conn.close()
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def get_user_baseline(username="guest"):
    """
    Returns the user's historical baseline (average) for HR and HRV.
    Provides None if there are fewer than 3 historical scans.
    """
    df = load_data()
    if df.empty or 'username' not in df.columns:
        return None
    df = df[df['username'] == username]
    # Only use entry scans for baseline to get true resting states
    if "scan_type" in df.columns:
        df = df[df['scan_type'] == 'entry']
        
    if len(df) < 3:
        return None
        
    # Get recent 20 days of data to form baseline
    recent = df.sort_values(by="timestamp").tail(20) 
    
    baseline = {
        "hr_mean": recent["hr"].mean(),
        "hr_std": recent["hr"].std() if len(recent) > 1 else 5,
        "hrv_mean": recent["hrv"].mean(),
        "hrv_std": recent["hrv"].std() if len(recent) > 1 else 10,
        "health_score_mean": recent["health_score"].mean() if "health_score" in recent.columns else None
    }
    return baseline

def get_todays_entry_scan(username="guest"):
    """
    Returns the latest entry scan for today, used for comparing against an exit scan.
    """
    df = load_data()
    if df.empty or 'username' not in df.columns:
        return None
        
    df = df[df['username'] == username]
        
    today = datetime.datetime.now().date()
    # Filter by today and 'entry'
    df['date'] = df['timestamp'].dt.date
    today_entries = df[(df['date'] == today) & (df['scan_type'] == 'entry')]
    
    if today_entries.empty:
        return None
        
    # Get the latest entry
    latest_entry = today_entries.sort_values(by="timestamp", ascending=False).iloc[0]
    return latest_entry.to_dict()

def compare_to_baseline(current_hr, current_hrv, username="guest"):
    """
    Analyzes how current vitals compare to the user's personal baseline.
    """
    baseline = get_user_baseline(username)
    if baseline is None:
        return "Insight: Keep scanning over the next few days to establish your personalized true baseline."
        
    hr_diff = current_hr - baseline["hr_mean"]
    hrv_diff = current_hrv - baseline["hrv_mean"]
    
    msg = ""
    # Analyze HR
    if current_hr > baseline["hr_mean"] + (1.5 * baseline["hr_std"]):
        msg += f"⚠️ Your Heart Rate is elevated by {int(hr_diff)} BPM compared to your normal baseline. "
    elif current_hr < baseline["hr_mean"] - (1.5 * baseline["hr_std"]):
        msg += f"⚠️ Your resting Heart Rate is notably lower ({int(abs(hr_diff))} BPM drop) than your historical norm. "
    else:
        msg += "✅ Your Heart Rate is aligned with your personal baseline. "
        
    # Analyze HRV
    if current_hrv < baseline["hrv_mean"] - (1.5 * baseline["hrv_std"]):
        msg += f"Your HRV has experienced a sudden drop ({int(abs(hrv_diff))} ms), strongly indicating acute physiological stress or poor recovery."
    elif current_hrv > baseline["hrv_mean"] + (1.5 * baseline["hrv_std"]):
        msg += "Your HRV is higher than your norm, indicating excellent cardiovascular recovery today!"
    return msg

def get_weekly_data(username="guest"):
    """
    Returns aggregated average metrics for the last 7 days.
    """
    df = load_data()
    if df.empty or 'username' not in df.columns:
        return pd.DataFrame()
        
    df = df[df['username'] == username]
        
    df['date'] = df['timestamp'].dt.date
    # Group by date
    daily_avg = df.groupby('date').agg({
        'hr': 'mean',
        'hrv': 'mean',
        'stress_score': 'mean',
        'health_score': 'mean'
    }).reset_index()
    
    # Sort by date descending and get last 7
    daily_avg = daily_avg.sort_values(by='date', ascending=False).head(7)
    daily_avg['date_str'] = daily_avg['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
    daily_avg['day_name'] = daily_avg['date'].apply(lambda x: x.strftime('%A'))
    # Return sorted by date ascending for charts
    return daily_avg.sort_values(by='date', ascending=True)

def get_daily_details(target_date_str, username="guest"):
    """
    Returns aggregated records for a specific date string (YYYY-MM-DD),
    grouping by minute to prevent noisy repeating timestamps in the UI table.
    """
    df = load_data()
    if df.empty or 'username' not in df.columns:
        return pd.DataFrame()
        
    df = df[df['username'] == username]
        
    df['date_str'] = df['timestamp'].dt.strftime('%Y-%m-%d')
    daily_df = df[df['date_str'] == target_date_str].copy()
    
    if daily_df.empty:
        return pd.DataFrame()
        
    # Round to nearest minute
    daily_df['timestamp'] = daily_df['timestamp'].dt.floor('min')
    
    # Group by the rounded minute and take the mean
    agg_df = daily_df.groupby('timestamp').agg({
        'hr': 'mean',
        'hrv': 'mean',
        'stress_score': 'mean',
        'health_score': 'mean'
    }).reset_index()
    
    agg_df['time_str'] = agg_df['timestamp'].dt.strftime('%H:%M')
    return agg_df.sort_values(by='timestamp', ascending=False)

def get_comparison_insights(current_hr, current_hrv, current_stress_level, username="guest"):
    """
    Provides intelligent comparison insights against the 7-day baseline.
    Returns a dictionary with formatted insight strings.
    """
    df_weekly = get_weekly_data(username)
    if df_weekly.empty or len(df_weekly) < 2:
        return {
            "hr": "Need more daily data to establish HR trends.",
            "hrv": "Need more daily data to establish HRV trends.",
            "stress": "Need more daily data to establish Stress trends."
        }
        
    stress_map = {"Low": 20, "Medium": 50, "High": 80}
    if isinstance(current_stress_level, str):
        current_stress_score = stress_map.get(current_stress_level, 50)
    else:
        current_stress_score = current_stress_level
        
    past_avg_hr = df_weekly['hr'].mean()
    past_avg_hrv = df_weekly['hrv'].mean()
    past_avg_stress = df_weekly['stress_score'].mean()
    
    insights = {}
    
    # HR Insight
    hr_diff_pct = ((current_hr - past_avg_hr) / past_avg_hr) * 100 if past_avg_hr > 0 else 0
    if hr_diff_pct < -5:
        insights['hr'] = f"Your HR improved by {abs(hr_diff_pct):.1f}% compared to your weekly average."
        insights['hr_trend'] = "improving"
    elif hr_diff_pct > 5:
        insights['hr'] = f"Your HR increased by {abs(hr_diff_pct):.1f}% compared to your weekly average."
        insights['hr_trend'] = "declining"
    else:
        insights['hr'] = "Your HR is perfectly stable with your weekly average."
        insights['hr_trend'] = "stable"
        
    # HRV Insight
    hrv_diff_pct = ((current_hrv - past_avg_hrv) / past_avg_hrv) * 100 if past_avg_hrv > 0 else 0
    if hrv_diff_pct > 5:
        insights['hrv'] = f"Excellent! HRV improved by {abs(hrv_diff_pct):.1f}% showing strong recovery."
        insights['hrv_trend'] = "improving"
    elif hrv_diff_pct < -5:
        insights['hrv'] = f"HRV dropped by {abs(hrv_diff_pct):.1f}% – consider resting."
        insights['hrv_trend'] = "declining"
    else:
        insights['hrv'] = "Your HRV remains stable within normal parameters."
        insights['hrv_trend'] = "stable"
        
    # Stress Insight
    stress_diff_pct = ((current_stress_score - past_avg_stress) / past_avg_stress) * 100 if past_avg_stress > 0 else 0
    if stress_diff_pct < -5:
        insights['stress'] = f"Stress levels improved (dropped {abs(stress_diff_pct):.1f}%) over the past days."
        insights['stress_trend'] = "improving"
    elif stress_diff_pct > 5:
        insights['stress'] = f"Stress levels increased slightly (up {abs(stress_diff_pct):.1f}%) compared to baseline."
        insights['stress_trend'] = "declining"
    else:
        insights['stress'] = "Stress parameters are stable."
        insights['stress_trend'] = "stable"
        
    return insights

def get_user_streak(username="guest"):
    """
    Calculates the user's current consecutive day login/scan streak.
    """
    df = load_data()
    if df.empty or 'username' not in df.columns:
        return 0
        
    df = df[df['username'] == username]
        
    # Get unique dates sorted descending
    df['date'] = df['timestamp'].dt.date
    unique_dates = df['date'].unique()
    unique_dates.sort()
    unique_dates = unique_dates[::-1] # latest first
    
    if len(unique_dates) == 0:
        return 0
        
    today = datetime.datetime.now().date()
    yesterday = today - datetime.timedelta(days=1)
    
    # If the user hasn't scanned today or yesterday, streak is broken
    if unique_dates[0] != today and unique_dates[0] != yesterday:
        return 0

    current_check_date = unique_dates[0]
    streak = 1
    
    for i in range(1, len(unique_dates)):
        diff = (current_check_date - unique_dates[i]).days
        if diff == 1:
            streak += 1
            current_check_date = unique_dates[i]
        else:
            break
            
    return streak

def get_gamification_badges(username="guest"):
    """
    Returns a list of HTML badges unlocked based on the user's streak and scanning history.
    """
    streak = get_user_streak(username)
    df = load_data()
    if not df.empty and 'username' in df.columns:
        df = df[df['username'] == username]
    total_scans = len(df)
    
    badges = []
    
    # Streak Badges
    if streak >= 3:
        badges.append({"name": "🔥 3-Day Streak", "desc": "Warming up!", "color": "#f97316"})
    if streak >= 7:
        badges.append({"name": "🔥 7-Day Master", "desc": "A full week of consistency", "color": "#ea580c"})
    if streak >= 30:
        badges.append({"name": "🔥 30-Day Legend", "desc": "Unstoppable dedication", "color": "#dc2626"})
        
    # Volume Badges
    if total_scans >= 5:
        badges.append({"name": "⭐ Consistent Scanner", "desc": "Completed 5+ scans", "color": "#8b5cf6"})
    if total_scans >= 50:
        badges.append({"name": "💎 Golden Heart", "desc": "Dedicated health tracking", "color": "#eab308"})
        
    if not badges:
        badges.append({"name": "🌱 Beginner", "desc": "Complete your first few scans", "color": "#22c55e"})
        
    return badges

def get_gym_duration(username="guest"):
    """
    Calculates the gym duration on the current day by looking for the latest
    entry scan and the latest exit scan. If both exist for today, calculates the timedelta.
    Returns a string duration or None.
    """
    df = load_data()
    if df.empty or 'username' not in df.columns or 'scan_type' not in df.columns:
        return None
        
    df = df[df['username'] == username]
    today = datetime.datetime.now().date()
    df['date'] = df['timestamp'].dt.date
    
    today_records = df[df['date'] == today]
    entry_scans = today_records[today_records['scan_type'] == 'entry']
    exit_scans = today_records[today_records['scan_type'] == 'exit']
    
    if entry_scans.empty or exit_scans.empty:
        return None
        
    # Get latest entry before latest exit
    lat_exit = exit_scans.sort_values(by="timestamp", ascending=False).iloc[0]
    lat_exit_time = lat_exit['timestamp']
    
    valid_entries = entry_scans[entry_scans['timestamp'] < lat_exit_time]
    if valid_entries.empty:
        return None
        
    lat_entry = valid_entries.sort_values(by="timestamp", ascending=False).iloc[0]
    lat_entry_time = lat_entry['timestamp']
    
    delta = lat_exit_time - lat_entry_time
    total_seconds = int(delta.total_seconds())
    
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"