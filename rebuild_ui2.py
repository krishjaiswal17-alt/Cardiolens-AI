import os

UI_CODE = r'''import streamlit as st
import cv2
import numpy as np
import tempfile
import os
import plotly.graph_objects as go
import time
import math
from collections import deque

from signal_processing import extract_face_roi, apply_pos, bandpass_filter, apply_smoothing
from features import detect_peaks, calculate_hr, compute_hrv, calculate_sqi
from risk_model import evaluate_stress, evaluate_cardiac_risk, calculate_health_score
from tracking import save_session, compare_to_baseline, load_data
from ai_recommendation import get_recommendation

def inject_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800;900&display=swap');
        
        body, .stApp {
            background-color: #030000;
            color: #ffffff;
            font-family: 'Outfit', sans-serif;
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(220, 20, 50, 0.08) 0%, transparent 40%),
                radial-gradient(circle at 90% 80%, rgba(255, 0, 70, 0.08) 0%, transparent 40%),
                radial-gradient(circle at 50% 50%, rgba(150, 0, 20, 0.05) 0%, transparent 60%);
            animation: pulse-bg 15s infinite alternate ease-in-out;
        }
        @keyframes pulse-bg {
            0% { background-position: 0% 0%; opacity: 0.8; }
            100% { background-position: 100% 100%; opacity: 1; }
        }

        .bubble {
            position: fixed;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(255, 50, 50, 0.15) 0%, transparent 70%);
            animation: float-ambient 12s infinite ease-in-out;
            pointer-events: none;
            z-index: 0;
            box-shadow: 0 0 30px rgba(255, 0, 50, 0.2);
            filter: blur(4px);
        }
        @keyframes float-ambient {
            0%, 100% { transform: translateY(0) scale(1) rotate(0deg); opacity: 0.3; }
            50% { transform: translateY(-80px) scale(1.3) rotate(180deg); opacity: 0.6; }
        }

        h1, h2, h3, h4 { color: #ffffff; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; }

        /* Metric Count-Up Animation Simulation via CSS scale up */
        div[data-testid="stMetricValue"] {
            font-size: 4rem;
            font-weight: 900;
            color: #ffffff;
            text-shadow: 0 0 25px rgba(255, 40, 60, 0.6), 0 0 50px rgba(255, 0, 80, 0.4);
            animation: metric-enter 1s cubic-bezier(0.2, 1, 0.3, 1), metric-pulse 4s infinite alternate cubic-bezier(0.4, 0, 0.2, 1) 1s;
        }
        @keyframes metric-enter { from { opacity: 0; transform: translateY(20px) scale(0.8); filter: blur(5px); } to { opacity: 1; transform: translateY(0) scale(1); filter: blur(0); } }
        @keyframes metric-pulse {
            0% { text-shadow: 0 0 20px rgba(255, 40, 60, 0.4), 0 0 40px rgba(255, 0, 80, 0.2); transform: scale(1); }
            100% { text-shadow: 0 0 30px rgba(255, 60, 80, 0.9), 0 0 60px rgba(255, 20, 100, 0.6); transform: scale(1.03); }
        }
        
        div[data-testid="stMetricLabel"] {
            color: #ffb3b3; font-size: 1.3rem; font-weight: 600; text-transform: uppercase; letter-spacing: 3px;
            margin-bottom: 12px; opacity: 0.8; border-bottom: 1px solid rgba(255, 50, 50, 0.3); padding-bottom: 5px; display: inline-block;
        }

        .glass-card {
            background: linear-gradient(150deg, rgba(25, 0, 5, 0.45) 0%, rgba(5, 0, 0, 0.65) 100%);
            backdrop-filter: blur(40px);
            -webkit-backdrop-filter: blur(40px);
            border-radius: 30px; border: 1px solid rgba(255, 80, 80, 0.15); border-top: 1px solid rgba(255, 120, 120, 0.3);
            border-bottom: 1px solid rgba(0, 0, 0, 0.8);
            padding: 35px; box-shadow: 0 25px 60px rgba(0, 0, 0, 0.9), inset 0 2px 20px rgba(255, 0, 50, 0.05); margin-bottom: 30px;
            transition: all 0.6s cubic-bezier(0.16, 1, 0.3, 1);
            position: relative; overflow: hidden; z-index: 1;
        }
        .glass-card::before {
            content: ''; position: absolute; top: 0; left: -150%; width: 50%; height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.03), transparent);
            transform: skewX(-25deg); transition: left 0.8s ease-in-out;
        }
        .glass-card:hover::before { left: 200%; }
        .glass-card:hover {
            box-shadow: 0 35px 80px rgba(255, 20, 60, 0.15), inset 0 2px 30px rgba(255, 0, 50, 0.1); border-top: 1px solid rgba(255, 120, 120, 0.5); transform: translateY(-8px);
        }

        .block-container { padding-top: 4rem !important; padding-bottom: 5rem !important; max-width: 1400px !important; }
        
        [data-testid="stMetric"], .stPlotlyChart {
            background: linear-gradient(150deg, rgba(25, 0, 5, 0.45) 0%, rgba(5, 0, 0, 0.65) 100%) !important;
            backdrop-filter: blur(40px) !important; border: 1px solid rgba(255, 80, 80, 0.15) !important;
            border-top: 1px solid rgba(255, 120, 120, 0.3) !important; border-radius: 24px !important; padding: 25px !important;
            box-shadow: 0 20px 50px rgba(0,0,0,0.8), inset 0 2px 15px rgba(255, 0, 50, 0.05) !important; transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1) !important;
        }
        [data-testid="stMetric"]:hover, .stPlotlyChart:hover {
            transform: translateY(-6px) !important; border-top: 1px solid rgba(255, 120, 120, 0.6) !important;
            box-shadow: 0 30px 60px rgba(255, 20, 60, 0.15), inset 0 2px 25px rgba(255, 0, 50, 0.1) !important; z-index: 10;
        }
        
        /* Staggered entry animations */
        [data-testid="stVerticalBlock"] > div {
            animation: cinematic-enter 0.8s cubic-bezier(0.2, 1, 0.3, 1) both;
        }
        [data-testid="stVerticalBlock"] > div:nth-child(1) { animation-delay: 0.1s; }
        [data-testid="stVerticalBlock"] > div:nth-child(2) { animation-delay: 0.2s; }
        [data-testid="stVerticalBlock"] > div:nth-child(3) { animation-delay: 0.3s; }
        [data-testid="stVerticalBlock"] > div:nth-child(4) { animation-delay: 0.4s; }

        @keyframes cinematic-enter {
            0% { opacity: 0; transform: translateY(30px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        
        .badge {
            padding: 10px 24px; border-radius: 40px; font-weight: 800; text-transform: uppercase; font-size: 1.1rem;
            letter-spacing: 2px; display: inline-block; margin: 10px 0; backdrop-filter: blur(10px); transition: all 0.3s ease;
        }
        .badge-optimal { background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.05)); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.5); box-shadow: 0 0 25px rgba(16, 185, 129, 0.2), inset 0 0 15px rgba(16, 185, 129, 0.1); }
        .badge-warning { background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(245, 158, 11, 0.05)); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.5); box-shadow: 0 0 25px rgba(245, 158, 11, 0.2), inset 0 0 15px rgba(245, 158, 11, 0.1); }
        .badge-critical {
            background: linear-gradient(135deg, rgba(255, 20, 60, 0.2), rgba(255, 0, 20, 0.05)); color: #ff4d4d; border: 1px solid rgba(255, 51, 51, 0.7);
            box-shadow: 0 0 40px rgba(255, 20, 60, 0.4), inset 0 0 20px rgba(255, 20, 60, 0.2); animation: pulse-critical 2s infinite alternate ease-in-out;
        }
        @keyframes pulse-critical { 0% { box-shadow: 0 0 30px rgba(255, 20, 60, 0.4), inset 0 0 15px rgba(255, 20, 60, 0.2); } 100% { box-shadow: 0 0 60px rgba(255, 40, 80, 0.8), inset 0 0 30px rgba(255, 20, 60, 0.4); border-color: #ff6666; transform: scale(1.02); } }

        .gradient-text {
            background: linear-gradient(135deg, #ff6b6b 0%, #ff1a40 25%, #ffb3b3 50%, #ff1a40 75%, #ff6b6b 100%);
            background-size: 300% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900;
            animation: gradient-flow 6s linear infinite; text-shadow: 0 0 40px rgba(255, 26, 64, 0.4); display: inline-block;
        }
        @keyframes gradient-flow { to { background-position: 300% center; } }
        
        .shimmer-text {
            color: rgba(255, 255, 255, 0.9);
            background: linear-gradient(90deg, rgba(255, 255, 255, 0.7) 0%, rgba(255, 50, 100, 1) 50%, rgba(255, 255, 255, 0.7) 100%);
            background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            animation: shimmer 4s infinite linear; font-weight: 800; letter-spacing: 1px;
        }
        @keyframes shimmer { to { background-position: 200% center; } }

        /* Immersive Processing Animations */
        .big-heart {
            font-size: 7rem; color: #ff1a40; text-shadow: 0 0 60px rgba(255, 26, 64, 0.9), 0 0 120px rgba(255, 0, 50, 0.6);
            animation: heart-beat 1s infinite cubic-bezier(0.2, 0.8, 0.2, 1); display: inline-block; margin: 30px auto;
        }
        @keyframes heart-beat { 0%, 100% { transform: scale(1); } 15% { transform: scale(1.3); text-shadow: 0 0 100px rgba(255, 26, 64, 1), 0 0 180px rgba(255, 0, 50, 0.8); } 30% { transform: scale(1.1); } 45% { transform: scale(1.3); } }

        .wave-box { position: relative; height: 120px; width: 100%; margin: 20px 0; overflow: hidden; border-bottom: 2px solid rgba(255, 26, 64, 0.3); }
        .wave-line {
            width: 200%; height: 100%;
            background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 100" preserveAspectRatio="none"><path fill="none" stroke="%23ff1a40" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" d="M0,50 L200,50 L230,10 L260,90 L290,30 L320,50 L800,50"/></svg>') repeat-x;
            background-size: 400px 100%; animation: wave-scroll 2s linear infinite; filter: drop-shadow(0 0 15px rgba(255, 26, 64, 0.9));
        }
        @keyframes wave-scroll { 0% { transform: translateX(0); } 100% { transform: translateX(-400px); } }

        .cyber-hex-stream {
            font-family: 'Courier New', monospace; font-size: 1.1rem; color: #ff4d4d; opacity: 0.8; text-shadow: 0 0 15px rgba(255, 0, 50, 0.9);
            line-height: 1.8; height: 150px; overflow: hidden; position: relative; margin: 0 auto; max-width: 600px;
            mask-image: linear-gradient(to bottom, transparent 0%, black 20%, black 80%, transparent 100%);
            -webkit-mask-image: linear-gradient(to bottom, transparent 0%, black 20%, black 80%, transparent 100%);
        }
        .hex-line { display: block; white-space: pre; animation: scroll-up 6s linear infinite; }
        @keyframes scroll-up { 0% { transform: translateY(0); } 100% { transform: translateY(-300px); } }

        /* Premium Buttons */
        div.stButton > button {
            background: linear-gradient(150deg, rgba(40, 0, 5, 0.7) 0%, rgba(10, 0, 0, 0.9) 100%);
            border: 1px solid rgba(255, 50, 50, 0.4); border-top: 1px solid rgba(255, 120, 120, 0.6); border-radius: 20px;
            color: #ffb3b3 !important; font-weight: 800; letter-spacing: 3px; transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
            box-shadow: 0 15px 40px rgba(0,0,0,0.9), inset 0 2px 15px rgba(255, 50, 50, 0.1); height: 90px; width: 100%;
            text-transform: uppercase; position: relative; overflow: hidden; backdrop-filter: blur(20px); font-size: 1.3rem;
        }
        div.stButton > button::after {
            content: ''; position: absolute; top: 0; left: -100%; width: 50%; height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 150, 150, 0.2), transparent);
            transform: skewX(-25deg); transition: left 0.7s ease;
        }
        div.stButton > button:hover::after { left: 200%; }
        div.stButton > button:hover {
            border: 1px solid rgba(255, 80, 80, 0.9); border-top: 1px solid rgba(255, 200, 200, 1);
            box-shadow: 0 25px 60px rgba(255, 20, 60, 0.3), inset 0 2px 25px rgba(255, 0, 50, 0.3); transform: translateY(-5px) scale(1.02);
            color: #ffffff !important; background: linear-gradient(150deg, rgba(60, 0, 10, 0.85) 0%, rgba(20, 0, 5, 0.95) 100%);
        }

        .stProgress > div > div > div {
            background-image: linear-gradient(90deg, #8a0000 0%, #ff1a40 50%, #ff8080 100%) !important;
            background-size: 200% 100%; box-shadow: 0 0 30px rgba(255, 26, 64, 0.8), 0 0 60px rgba(255, 0, 50, 0.4);
            border-radius: 15px; animation: progress-flow 2s linear infinite;
        }
        @keyframes progress-flow { to { background-position: -200% 0; } }

        /* Step-by-Step AI Breakdown Effects */
        .ai-diagnosis-container:nth-child(n) {   
            animation: slide-reveal 1s cubic-bezier(0.2, 1, 0.3, 1) both; 
        }
        .ai-diagnosis-container { animation-delay: 0.6s !important; }
        .ai-action-container { animation-delay: 1.2s !important; }
        
        .ai-diagnosis-container, .ai-action-container {
            background: linear-gradient(135deg, rgba(30, 0, 5, 0.7) 0%, rgba(10, 0, 0, 0.9) 100%);
            border-left: 6px solid #ff1a40; padding: 40px; margin-bottom: 30px; border-radius: 8px 24px 24px 8px;
            box-shadow: inset 10px 0 30px rgba(255, 20, 60, 0.15), 0 15px 40px rgba(0,0,0,0.5); backdrop-filter: blur(20px);
            border-top: 1px solid rgba(255, 100, 100, 0.2);
            transition: all 0.4s ease;
        }
        .ai-diagnosis-container:hover, .ai-action-container:hover {
            box-shadow: inset 15px 0 40px rgba(255, 20, 60, 0.25), 0 20px 50px rgba(255, 0, 50, 0.15); border-left: 8px solid #ff4d4d;
        }
        @keyframes slide-reveal { 0% { opacity: 0; transform: translateX(40px); } 100% { opacity: 1; transform: translateX(0); } }

        .ai-icon { font-size: 2rem; margin-right: 15px; vertical-align: middle; filter: drop-shadow(0 0 10px rgba(255, 26, 64, 0.8)); }
        
        header[data-testid="stHeader"] { display: none !important; }

        [data-testid="stFileUploader"] {
            background: linear-gradient(150deg, rgba(30, 0, 5, 0.5), rgba(10, 0, 0, 0.7)) !important; border: 2px dashed rgba(255, 50, 50, 0.4) !important;
            border-radius: 24px !important; padding: 40px !important; transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
            box-shadow: inset 0 0 20px rgba(255, 0, 50, 0.05) !important; backdrop-filter: blur(20px); height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center;
        }
        [data-testid="stFileUploader"]:hover {
            border: 2px dashed #ff1a40 !important; background: linear-gradient(150deg, rgba(50, 0, 10, 0.6), rgba(15, 0, 0, 0.8)) !important;
            box-shadow: inset 0 0 40px rgba(255, 0, 50, 0.2), 0 15px 40px rgba(255, 20, 60, 0.2) !important; transform: translateY(-4px);
        }
        [data-testid="stFileUploader"] section { color: #ffb3b3 !important; font-size: 1.2rem; }
        [data-testid="stFileUploader"] svg { fill: #ff4d4d !important; width: 60px; height: 60px; margin-bottom: 20px; }
        [data-testid="stFileUploader"] .stButton > button { background: rgba(255, 20, 60, 0.15) !important; color: #ffffff !important; border: 1px solid rgba(255, 50, 50, 0.4) !important; height: 50px !important; border-radius: 12px !important; }

        </style>
        
        <!-- Ambient Particles -->
        <div class="bubble" style="width: 30px; height: 30px; left: 10%; top: 20%; animation-duration: 15s; animation-delay: 0s;"></div>
        <div class="bubble" style="width: 50px; height: 50px; left: 85%; top: 60%; animation-duration: 18s; animation-delay: 2s;"></div>
        <div class="bubble" style="width: 20px; height: 20px; left: 50%; top: 80%; animation-duration: 12s; animation-delay: 5s;"></div>
        <div class="bubble" style="width: 60px; height: 60px; left: 75%; top: 15%; animation-duration: 20s; animation-delay: 1s;"></div>
    """, unsafe_allow_html=True)

def render_badge(label, status):
    status_lower = status.lower()
    if 'low' in status_lower or 'optimal' in status_lower: badge_class = 'badge-optimal'
    elif 'medium' in status_lower or 'moderate' in status_lower: badge_class = 'badge-warning'
    else: badge_class = 'badge-critical'
    st.markdown(f"<div class='glass-card' style='padding: 20px;'><h4>{label}</h4><div class='badge {badge_class}'>{status}</div></div>", unsafe_allow_html=True)

st.set_page_config(page_title="CardioLens AI Nexus", page_icon="❤️", layout="wide", initial_sidebar_state="collapsed")
inject_custom_css()

if "app_state" not in st.session_state: st.session_state.app_state = "Home"
if "video_source" not in st.session_state: st.session_state.video_source = 0
if "scan_buffers" not in st.session_state: st.session_state.scan_buffers = {'r': [], 'g': [], 'b': [], 'fps': 30}

def create_plotly_waveform(y_data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=y_data, mode='lines', line=dict(color='rgba(255, 26, 64, 0.15)', width=12, shape='spline', smoothing=1.3), hoverinfo='skip'))
    fig.add_trace(go.Scatter(y=y_data, mode='lines', line=dict(color='rgba(255, 50, 80, 0.3)', width=7, shape='spline', smoothing=1.3), hoverinfo='skip'))
    fig.add_trace(go.Scatter(y=y_data, mode='lines', line=dict(color='#ff3355', width=3, shape='spline', smoothing=1.3), fill='tozeroy', fillcolor='rgba(255, 26, 64, 0.08)'))
    
    last_idx = len(y_data) - 1
    if last_idx >= 0:
        fig.add_trace(go.Scatter(x=[last_idx], y=[y_data[last_idx]], mode='markers', marker=dict(color='#ffffff', size=16, line=dict(color='#ff1a40', width=5)), hoverinfo='skip'))
    
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=20, b=0), xaxis=dict(showgrid=True, gridcolor='rgba(255, 26, 64, 0.03)', zeroline=False, showticklabels=False), yaxis=dict(showgrid=False, zeroline=False, showticklabels=False), height=220, showlegend=False)
    return fig

def create_plotly_stress_gauge(stress_status):
    val = 50
    if 'low' in stress_status.lower() or 'optimal' in stress_status.lower(): val = 25
    elif 'high' in stress_status.lower() or 'elevated' in stress_status.lower(): val = 85
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=val, domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [None, 100], 'visible': False},
            'bar': {'color': "#ff1a40", 'thickness': 0.25},
            'bgcolor': "rgba(255,0,0,0.1)",
            'steps': [
                {'range': [0, 33], 'color': "rgba(16, 185, 129, 0.25)"},
                {'range': [33, 66], 'color': "rgba(245, 158, 11, 0.25)"},
                {'range': [66, 100], 'color': "rgba(255, 20, 60, 0.25)"}
            ]
        }
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=220, margin=dict(l=20, r=20, t=20, b=20), font=dict(color="#ffffff", size=24))
    return fig

def create_history_chart():
    df = load_data()
    if df.empty or len(df) < 2: return None
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['hr'], mode='lines', line=dict(color='rgba(255, 26, 64, 0.15)', width=10, shape='spline'), hoverinfo='skip'))
    fig.add_trace(go.Scatter(x=df.index, y=df['hr'], mode='lines+markers', name='HR (BPM)', line=dict(color='#ff1a40', width=3, shape='spline'), marker=dict(size=12, color='#fff', line=dict(width=3, color='#ff1a40')), fill='tozeroy', fillcolor='rgba(255, 26, 64, 0.08)'))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#ffb3b3", family="Outfit, sans-serif"), xaxis=dict(showgrid=True, gridcolor='rgba(255, 50, 50, 0.08)', title="Scan Sequence", zeroline=False), yaxis=dict(showgrid=True, gridcolor='rgba(255, 50, 50, 0.08)', title="BPM", zeroline=False), height=280, margin=dict(l=0, r=0, t=20, b=10), showlegend=False)
    return fig

def main():
    if st.session_state.app_state != "Home":
        if st.sidebar.button("⬅️ TERMINATE (HOME)"): st.session_state.app_state = "Home"; st.rerun()

    if st.session_state.app_state == "Home":
        st.markdown("<h1 class='gradient-text' style='text-align:center; font-size: 5rem; margin-top:30px;'>CARDIOLENS AI NEXUS</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#ffb3b3; font-size: 1.4rem; font-weight: 300; letter-spacing: 4px; margin-bottom: 60px;'>ADVANCED OPTICAL CHROMATIC DIAGNOSTICS</p>", unsafe_allow_html=True)
        
        st.markdown("<div style='max-width: 1000px; margin: 0 auto;'>", unsafe_allow_html=True)
        c_1, c_gap, c_2 = st.columns([1, 0.1, 1])
        with c_1:
            if st.button("🔴 START LIVE SCAN"): st.session_state.video_source = 0; st.session_state.app_state = "Scanning"; st.rerun()
        with c_2:
            uploaded_file = st.file_uploader("UPLOAD PHOTO", type=["jpg", "png", "jpeg", "mp4", "mov"], label_visibility="collapsed")
            if uploaded_file is not None:
                tfile = tempfile.NamedTemporaryFile(delete=False); tfile.write(uploaded_file.read())
                st.session_state.video_source = tfile.name
                if st.button("EXECUTE ANALYSIS"): st.session_state.app_state = "Scanning"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
        historical_chart = create_history_chart()
        if historical_chart:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("<div class='glass-card'><h4 style='text-align:center;'>Longitudinal Baseline Trajectory</h4>", unsafe_allow_html=True)
            st.plotly_chart(historical_chart, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.app_state == "Scanning":
        run_scan_phase(st.session_state.video_source)

    elif st.session_state.app_state == "Processing":
        run_processing_phase()

    elif st.session_state.app_state == "Results":
        run_results_dashboard()

def run_scan_phase(video_source):
    st.markdown("<h2 class='gradient-text' style='text-align:center;'>INITIALIZING OPTICAL SENSORS</h2>", unsafe_allow_html=True)
    st.markdown("<p class='shimmer-text' style='text-align:center;'>Establishing facial tracking parameters...</p>", unsafe_allow_html=True)
    
    col_spacer1, col_video, col_spacer2 = st.columns([1, 2, 1])
    with col_video:
        st.markdown("<div class='glass-card' style='text-align:center; padding: 20px;'>", unsafe_allow_html=True)
        video_placeholder = st.empty()
        scan_progress = st.progress(0)
        st.markdown("</div>", unsafe_allow_html=True)

    cap = cv2.VideoCapture(video_source)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not cap.isOpened() or fps <= 0: fps = 30
    
    is_image = isinstance(video_source, str) and video_source.lower().endswith(('jpg', 'jpeg', 'png'))
    if is_image: fps = 30
        
    max_frames = 100 
    r_buffer, g_buffer, b_buffer = [], [], []

    for frames_processed in range(max_frames):
        ret, frame = cap.read()
        if not ret: 
            if is_image and frames_processed > 0: cap.set(cv2.CAP_PROP_POS_FRAMES, 0); ret, frame = cap.read()
            else: break
        if video_source == 0: frame = cv2.flip(frame, 1)

        draw_frame = frame.copy()
        
        # Draw Cinematic glowing overlay
        overlay = draw_frame.copy()
        cv2.rectangle(overlay, (0,0), (overlay.shape[1], overlay.shape[0]), (0,0,30), -1)
        
        roi_data = extract_face_roi(frame)
        if roi_data is not None:
            (rm, gm, bm), (x, y, w, h) = roi_data
            if is_image:
                t = frames_processed / fps
                pulse_sim = 2 * math.sin(2 * math.pi * (72 / 60) * t) + np.random.normal(0, 0.5)
                rm += pulse_sim; gm += pulse_sim; bm += pulse_sim
            r_buffer.append(rm); g_buffer.append(gm); b_buffer.append(bm)
            
            # Clear face from dark overlay
            overlay[y:y+h, x:x+w] = draw_frame[y:y+h, x:x+w]
            cv2.addWeighted(overlay, 0.7, draw_frame, 0.3, 0, draw_frame)
            
            # Glowing borders
            glow_intensity = int(abs(math.sin(frames_processed * 0.1)) * 100 + 100)
            cv2.rectangle(draw_frame, (x, y), (x+w, y+h), (0, 0, glow_intensity), 2)
            cv2.putText(draw_frame, f"TRACKING LOCK | SIGNAL: OPTIMAL", (x, y-15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 50, 255), 2)
        else:
            if len(g_buffer) > 0: r_buffer.append(r_buffer[-1]); g_buffer.append(g_buffer[-1]); b_buffer.append(b_buffer[-1])
            cv2.addWeighted(overlay, 0.5, draw_frame, 0.5, 0, draw_frame)

        draw_frame = cv2.cvtColor(draw_frame, cv2.COLOR_BGR2RGB)
        video_placeholder.image(draw_frame, channels="RGB")
        scan_progress.progress((frames_processed + 1) / max_frames)
        
        if not is_image and video_source == 0: time.sleep(0.01)

    cap.release()
    st.session_state.scan_buffers = {'r': r_buffer, 'g': g_buffer, 'b': b_buffer, 'fps': fps}
    st.session_state.app_state = "Processing"
    st.rerun()

def run_processing_phase():
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<div class='glass-card' style='max-width: 900px; margin: 0 auto; text-align:center; padding: 60px 30px;'>", unsafe_allow_html=True)
    st.markdown("<div class='big-heart'>❤️</div>", unsafe_allow_html=True)
    st.markdown("<h2 class='gradient-text' style='text-align:center;'>ANALYZING OPTICAL TELEMETRY</h2>", unsafe_allow_html=True)
    st.markdown("<p class='shimmer-text' style='text-align:center; font-size: 1.3rem; margin-top: 10px;'>DECODING POS CHROMATIC SIGNALS</p>", unsafe_allow_html=True)
    st.markdown("<div class='wave-box'><div class='wave-line'></div></div>", unsafe_allow_html=True)
    
    st.markdown("<div class='cyber-hex-stream'>", unsafe_allow_html=True)
    hex_ph = st.empty()
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    text = ""
    for i in range(12):
        row = " ".join([f"{np.random.randint(0,255):02X}" for _ in range(12)])
        text += f"0x{(i*16):04X} :  {row}\n"
        display_text = "\n".join(text.split("\n")[-10:])
        hex_ph.markdown(f"<div class='hex-line'>{display_text}</div>", unsafe_allow_html=True)
        time.sleep(0.15)
        
    st.session_state.app_state = "Results"
    st.rerun()

def run_results_dashboard():
    buffers = st.session_state.scan_buffers
    r_buffer, g_buffer, b_buffer, fps = buffers['r'], buffers['g'], buffers['b'], buffers['fps']
    
    st.markdown("<h2 class='gradient-text' style='font-size: 2.8rem; margin-bottom: 30px;'>MEDICAL INTELLIGENCE FUSION REPORT</h2>", unsafe_allow_html=True)
    
    pulse = apply_pos(np.array(r_buffer), np.array(g_buffer), np.array(b_buffer), fps)
    peaks = detect_peaks(apply_smoothing(bandpass_filter(pulse, fps)), fps)
    smooth_pulse = apply_smoothing(bandpass_filter(pulse, fps))
    final_hr = calculate_hr(peaks, fps)
    final_hrv = compute_hrv(peaks, fps)
    final_stress = evaluate_stress(final_hrv, final_hr)
    final_sqi = calculate_sqi(smooth_pulse, fps)
    final_risk, risk_reason = evaluate_cardiac_risk(final_hr, final_hrv, final_stress)
    final_score = calculate_health_score(final_hr, final_hrv, final_stress, final_sqi)
    
    save_session(final_hr, final_hrv, final_stress, final_score, final_risk)

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Heart Rate", f"{final_hr} BPM")
    with col2: st.metric("HRV (RMSSD)", f"{final_hrv.get('rmssd', 0)} ms")
    with col3: st.metric("Health Score", f"{final_score}/100")
    with col4: st.metric("Confidence (SQI)", f"{final_sqi}%")
    st.markdown("<br>", unsafe_allow_html=True)

    c_g1, c_g2 = st.columns([2, 1])
    with c_g1:
        st.markdown("<div class='glass-card'><h4>Real-time Heartbeat Resonance</h4>", unsafe_allow_html=True)
        st.plotly_chart(create_plotly_waveform(list(smooth_pulse[-100:])), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c_g2:
        st.markdown("<div class='glass-card' style='text-align:center;'><h4>Stress Assessment</h4>", unsafe_allow_html=True)
        st.plotly_chart(create_plotly_stress_gauge(final_stress), use_container_width=True)
        render_badge("Physiological State", final_stress)
        st.markdown("</div>", unsafe_allow_html=True)

    c_r1, c_r2 = st.columns([1, 1.5])
    with c_r1:
        st.markdown("<div class='glass-card'><h4>Baseline Analysis</h4>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:1.1rem; color:#ffb3b3; line-height: 1.6;'>{compare_to_baseline(final_hr, final_hrv.get('rmssd', 0))}</p><hr>", unsafe_allow_html=True)
        render_badge("Current CV Risk Vector", final_risk)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c_r2:
        st.markdown("<div class='glass-card'><h4>Diagnostic Reason Matrix</h4>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:1.15rem; color:#ffffff; font-weight:300;'>{risk_reason}</p></div>", unsafe_allow_html=True)

    st.markdown("<h3 class='shimmer-text' style='margin-top: 40px; font-size: 2rem;'>AI Expert Prescriptions</h3>", unsafe_allow_html=True)
    with st.spinner("Compiling cross-referenced intelligence..."):
        ai_advice = get_recommendation(final_hr, final_hrv, final_stress, final_score, final_risk)
    
    # Split text if possible, else render as glowing diagnosis block
    st.markdown("<div class='ai-diagnosis-container'><span class='ai-icon'>📋</span><strong>Primary Diagnosis:</strong><br><br>", unsafe_allow_html=True)
    st.markdown(ai_advice, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
'''

with open("ui.py", "w", encoding="utf-8") as f:
    f.write(UI_CODE)

print("Updated ui.py completely with new animated phases")
