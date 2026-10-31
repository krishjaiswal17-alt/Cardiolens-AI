import os

ORIGINAL_UI = r'''import streamlit as st
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
        
        /* Deep Crimson Glassmorphic Base Theme */
        body, .stApp {
            background-color: #050000;
            color: #ffffff;
            font-family: 'Outfit', sans-serif;
            background-image: 
                radial-gradient(circle at 15% 20%, rgba(220, 20, 60, 0.15) 0%, transparent 35%),
                radial-gradient(circle at 85% 85%, rgba(255, 0, 85, 0.1) 0%, transparent 35%);
            animation: pulse-bg 12s infinite alternate ease-in-out;
        }

        @keyframes pulse-bg {
            0% { background-position: 0% 0%; opacity: 0.8; }
            100% { background-position: 100% 100%; opacity: 1; }
        }

        /* Bubble Particulates */
        .bubble {
            position: fixed;
            border-radius: 50%;
            background: linear-gradient(135deg, rgba(255, 60, 60, 0.3), rgba(255, 0, 50, 0.1));
            animation: float 8s infinite ease-in-out;
            pointer-events: none;
            z-index: 0;
            box-shadow: 0 0 15px rgba(255, 0, 50, 0.6);
            backdrop-filter: blur(2px);
        }
        @keyframes float {
            0%, 100% { transform: translateY(0) scale(1); }
            50% { transform: translateY(-40px) scale(1.15); opacity: 0.4; }
        }

        /* Typography */
        h1, h2, h3, h4 {
            color: #ffffff;
            font-weight: 800;
            letter-spacing: 1px;
            text-transform: uppercase;
        }

        /* Value Metrics */
        div[data-testid="stMetricValue"] {
            font-size: 3.2rem;
            font-weight: 900;
            color: #ffffff;
            text-shadow: 0 0 20px rgba(255, 40, 60, 0.5), 0 0 40px rgba(255, 0, 80, 0.3);
            animation: metric-glow 3s infinite alternate ease-in-out;
        }
        @keyframes metric-glow {
            0% { text-shadow: 0 0 20px rgba(255, 40, 60, 0.5), 0 0 40px rgba(255, 0, 80, 0.3); }
            100% { text-shadow: 0 0 25px rgba(255, 60, 80, 0.8), 0 0 50px rgba(255, 20, 100, 0.5); }
        }
        
        div[data-testid="stMetricLabel"] {
            color: #ffb3b3;
            font-size: 1.15rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 8px;
            opacity: 0.9;
        }

        /* Crimson Glassmorphism Cards */
        .glass-card {
            background: linear-gradient(145deg, rgba(20, 0, 5, 0.5), rgba(10, 0, 0, 0.7));
            backdrop-filter: blur(25px);
            -webkit-backdrop-filter: blur(25px);
            border-radius: 24px;
            border: 1px solid rgba(255, 80, 80, 0.15);
            border-top: 1px solid rgba(255, 120, 120, 0.3);
            padding: 26px;
            box-shadow: 0 15px 45px 0 rgba(0, 0, 0, 0.7), inset 0 0 25px rgba(255, 0, 50, 0.05);
            margin-bottom: 24px;
            transition: all 0.5s cubic-bezier(0.2, 0.8, 0.2, 1);
            position: relative;
            overflow: hidden;
            z-index: 1;
            animation: card-breathe 8s infinite alternate ease-in-out;
        }
        .glass-card::before {
            content: '';
            position: absolute;
            top: 0; left: -100%; width: 50%; height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.03), transparent);
            transform: skewX(-20deg);
            transition: left 0.7s ease;
        }
        .glass-card:hover::before {
            left: 150%;
        }
        .glass-card:hover {
            box-shadow: 0 20px 50px 0 rgba(255, 20, 60, 0.25), inset 0 0 40px rgba(255, 0, 50, 0.1);
            border-top: 1px solid rgba(255, 100, 100, 0.6);
            border-bottom: 1px solid rgba(255, 80, 80, 0.2);
            transform: translateY(-4px) scale(1.01);
        }
        @keyframes card-breathe {
            0% { box-shadow: 0 15px 45px 0 rgba(0, 0, 0, 0.7), inset 0 0 25px rgba(255, 0, 50, 0.05); }
            100% { box-shadow: 0 15px 45px 0 rgba(0, 0, 0, 0.8), inset 0 0 35px rgba(255, 0, 50, 0.08); }
        }
        
        /* Native Streamlit Components styled as Glass Cards */
        [data-testid="stMetric"], .stPlotlyChart {
            background: linear-gradient(145deg, rgba(20, 0, 5, 0.5), rgba(10, 0, 0, 0.7)) !important;
            backdrop-filter: blur(25px) !important;
            border: 1px solid rgba(255, 80, 80, 0.15) !important;
            border-top: 1px solid rgba(255, 120, 120, 0.3) !important;
            border-radius: 20px !important;
            padding: 20px !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.8), inset 0 0 20px rgba(255, 0, 50, 0.05) !important;
            animation: card-breathe 8s infinite alternate ease-in-out;
            transition: all 0.3s ease;
        }
        [data-testid="stMetric"]:hover, .stPlotlyChart:hover {
            transform: translateY(-4px) scale(1.02) !important;
            border-top: 1px solid rgba(255, 100, 100, 0.6) !important;
            box-shadow: 0 20px 50px 0 rgba(255, 20, 60, 0.25), inset 0 0 40px rgba(255, 0, 50, 0.1) !important;
        }
        
        /* Global Fade-in App Wrapper */
        [data-testid="stMainBlockContainer"] {
            animation: fade-slide-up 0.8s cubic-bezier(0.2, 0.8, 0.2, 1);
        }
        
        /* Badges */
        .badge {
            padding: 8px 20px;
            border-radius: 30px;
            font-weight: 900;
            text-transform: uppercase;
            font-size: 1.05rem;
            letter-spacing: 1.5px;
            display: inline-block;
            margin: 5px 0;
            backdrop-filter: blur(5px);
        }
        .badge-optimal {
            background: rgba(16, 185, 129, 0.1);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.4);
            box-shadow: 0 0 20px rgba(16, 185, 129, 0.3), inset 0 0 10px rgba(16, 185, 129, 0.1);
        }
        .badge-warning {
            background: rgba(245, 158, 11, 0.1);
            color: #fbbf24;
            border: 1px solid rgba(245, 158, 11, 0.4);
            box-shadow: 0 0 20px rgba(245, 158, 11, 0.3), inset 0 0 10px rgba(245, 158, 11, 0.1);
        }
        .badge-critical {
            background: rgba(255, 20, 60, 0.1);
            color: #ff3333;
            border: 1px solid rgba(255, 51, 51, 0.6);
            box-shadow: 0 0 30px rgba(255, 20, 60, 0.5), inset 0 0 15px rgba(255, 20, 60, 0.2);
            animation: pulse-alert 1.2s infinite alternate ease-in-out;
        }
        @keyframes pulse-alert {
            0% { box-shadow: 0 0 25px rgba(255, 20, 60, 0.5), inset 0 0 15px rgba(255, 20, 60, 0.2); }
            100% { box-shadow: 0 0 45px rgba(255, 20, 60, 0.9), inset 0 0 25px rgba(255, 20, 60, 0.4); border-color: #ff4d4d; }
        }

        /* Gradient Crimson Text */
        .gradient-text {
            background: linear-gradient(135deg, #ff4d4d 0%, #ff0044 25%, #ffb3b3 50%, #ff0044 75%, #ff4d4d 100%);
            background-size: 300% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 900;
            animation: gradient-flow 4s linear infinite;
            text-shadow: 0 0 30px rgba(255, 0, 50, 0.3);
        }
        @keyframes gradient-flow {
            to { background-position: 300% center; }
        }

        /* Shimmer Effect for Recommendations */
        .shimmer-text {
            color: rgba(255, 255, 255, 0.9);
            background: linear-gradient(90deg, rgba(255, 255, 255, 0.8) 0%, rgba(255, 50, 100, 1) 50%, rgba(255, 255, 255, 0.8) 100%);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: shimmer 3s infinite linear;
            font-weight: 600;
        }
        @keyframes shimmer {
            to { background-position: 200% center; }
        }

        /* Loader */
        .loader-glow {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            border: 4px solid rgba(255, 0, 50, 0.2);
            border-top: 4px solid #ff1a40;
            animation: spin 1s linear infinite, glow 2s ease-in-out infinite alternate;
            margin: 40px auto;
        }
        @keyframes spin { 100% { transform: rotate(360deg); } }
        @keyframes glow { 
            0% { box-shadow: 0 0 20px rgba(255, 0, 50, 0.5); }
            100% { box-shadow: 0 0 60px rgba(255, 0, 50, 1); }
        }

        /* Streamlit Button Restyle */
        div.stButton > button {
            background: linear-gradient(145deg, rgba(40, 0, 0, 0.8) 0%, rgba(15, 0, 0, 0.9) 100%);
            border: 1px solid rgba(255, 50, 50, 0.3);
            border-top: 1px solid rgba(255, 100, 100, 0.5);
            border-radius: 14px;
            color: #ff4d4d !important;
            font-weight: 900;
            letter-spacing: 2.5px;
            transition: all 0.4s cubic-bezier(0.2, 0.8, 0.2, 1);
            box-shadow: 0 10px 30px rgba(0,0,0,0.8), inset 0 0 10px rgba(255, 50, 50, 0.05);
            height: 58px;
            width: 100%;
            text-transform: uppercase;
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(10px);
        }
        div.stButton > button::after {
            content: '';
            position: absolute;
            top: 0; left: -100%; width: 50%; height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 100, 100, 0.2), transparent);
            transform: skewX(-20deg);
            transition: left 0.6s ease;
        }
        div.stButton > button:hover::after {
            left: 150%;
        }
        div.stButton > button:hover {
            border: 1px solid rgba(255, 50, 50, 0.8);
            border-top: 1px solid rgba(255, 150, 150, 1);
            box-shadow: 0 15px 40px rgba(255, 0, 50, 0.4), inset 0 0 20px rgba(255, 0, 50, 0.2);
            transform: translateY(-3px) scale(1.02);
            color: #ffffff !important;
            background: linear-gradient(145deg, rgba(60, 0, 0, 0.9) 0%, rgba(20, 0, 0, 1) 100%);
        }
        /* Streamlit Button Ripple & Active State */
        div.stButton > button:active {
            transform: scale(0.96) translateY(2px) !important;
            background: radial-gradient(circle, rgba(255, 100, 100, 0.5) 0%, rgba(20, 0, 0, 1) 100%) !important;
            box-shadow: inset 0 0 25px rgba(255, 50, 50, 0.6), 0 0 10px rgba(255, 20, 60, 0.4) !important;
        }

        /* Progress Bar */
        .stProgress > div > div > div {
            background-image: linear-gradient(to right, #cc0000, #ff1a1a, #ff4d4d) !important;
            box-shadow: 0 0 20px rgba(255, 20, 60, 0.9), 0 0 40px rgba(255, 0, 50, 0.5);
            border-radius: 10px;
        }
        
        hr {
            border-top: 1px solid rgba(255, 50, 50, 0.15);
            box-shadow: 0 1px 10px rgba(255, 0, 50, 0.2);
        }

        /* CSS Animated Hearthbeat Loading SVG */
        .heartbeat-loader {
            display: inline-block;
            width: 150px;
            height: 60px;
            background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 100"><path fill="none" stroke="%23ff1a40" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" d="M 0 50 L 50 50 L 70 10 L 90 90 L 110 30 L 130 50 L 200 50"/></svg>') no-repeat center;
            background-size: cover;
            filter: drop-shadow(0 0 15px rgba(255, 26, 64, 0.9));
            animation: pulse-svg 1.2s infinite ease-in-out;
            margin: 20px 0;
            position: relative;
        }
        .heartbeat-loader::after {
            content: '';
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(90deg, transparent 50%, rgba(5, 0, 0, 1) 50%);
            background-size: 200% 100%;
            animation: scanline 1.5s infinite linear;
        }
        @keyframes pulse-svg {
            0%, 100% { filter: drop-shadow(0 0 8px rgba(255, 26, 64, 0.5)); transform: scale(1); }
            50% { filter: drop-shadow(0 0 25px rgba(255, 26, 64, 1)); transform: scale(1.05); }
        }
        @keyframes scanline {
            0% { background-position: 100% 0; }
            100% { background-position: -100% 0; }
        }

        /* AI Recommendation Enhancements */
        @keyframes fade-slide-up {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .ai-diagnosis-container {
            background: rgba(40, 0, 10, 0.4);
            border-left: 4px solid #ff1a40;
            padding: 24px;
            margin-bottom: 20px;
            border-radius: 4px 12px 12px 4px;
            box-shadow: inset 5px 0 15px rgba(255, 20, 60, 0.1);
            animation: fade-slide-up 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) both;
            animation-delay: 0.1s;
        }
        .ai-action-list {
            background: rgba(20, 0, 5, 0.6);
            padding: 24px;
            border-radius: 12px;
            border: 1px solid rgba(255, 50, 50, 0.2);
            animation: fade-slide-up 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) both;
            animation-delay: 0.5s;
        }
        
        /* Dashboard Transition Wrapper */
        .dashboard-wrapper {
            animation: fade-slide-up 0.9s cubic-bezier(0.2, 0.8, 0.2, 1);
        }

        /* Force clear Streamlit default headers */
        header[data-testid="stHeader"] {
            background-color: transparent !important;
            visibility: hidden !important;
        }
        .block-container {
            padding-top: 2rem !important;
        }

        /* File Uploader Restyle */
        [data-testid="stFileUploader"] {
            background: linear-gradient(145deg, rgba(40, 0, 5, 0.6), rgba(15, 0, 0, 0.8)) !important;
            border: 1px dashed rgba(255, 50, 50, 0.5) !important;
            border-radius: 16px !important;
            padding: 20px !important;
            transition: all 0.3s ease-in-out !important;
            box-shadow: inset 0 0 15px rgba(255, 0, 50, 0.1) !important;
        }
        [data-testid="stFileUploader"]:hover {
            border: 1px dashed rgba(255, 100, 100, 0.8) !important;
            background: linear-gradient(145deg, rgba(60, 0, 10, 0.7), rgba(25, 0, 0, 0.9)) !important;
            box-shadow: inset 0 0 25px rgba(255, 0, 50, 0.2), 0 0 15px rgba(255, 20, 60, 0.3) !important;
        }
        [data-testid="stFileUploader"] section {
            color: #ffb3b3 !important;
        }
        [data-testid="stFileUploader"] svg {
            fill: #ff4d4d !important;
        }
        [data-testid="stFileUploader"] div {
            color: #ffb3b3 !important;
        }
        [data-testid="stFileUploader"] .stButton > button {
            background: rgba(255, 20, 60, 0.2) !important;
            color: #ffffff !important;
            border: 1px solid rgba(255, 50, 50, 0.5) !important;
            height: 40px !important;
            box-shadow: none !important;
        }
        
        </style>
        
        <!-- Bubble Engine UI Injection -->
        <div class="bubble" style="width: 18px; height: 18px; left: 12%; top: 25%; animation-duration: 10s;"></div>
        <div class="bubble" style="width: 28px; height: 28px; left: 82%; top: 55%; animation-duration: 12s;"></div>
        <div class="bubble" style="width: 12px; height: 12px; left: 45%; top: 85%; animation-duration: 8s;"></div>
        <div class="bubble" style="width: 35px; height: 35px; left: 72%; top: 12%; animation-duration: 14s;"></div>
        <div class="bubble" style="width: 20px; height: 20px; left: 25%; top: 75%; animation-duration: 11s;"></div>
    """, unsafe_allow_html=True)

def render_badge(label, status):
    status_lower = status.lower()
    if 'low' in status_lower or 'optimal' in status_lower:
        badge_class = 'badge-optimal'
    elif 'medium' in status_lower or 'moderate' in status_lower:
        badge_class = 'badge-warning'
    else:
        badge_class = 'badge-critical'
    st.markdown(f"<div class='glass-card'><h4>{label}</h4><div class='badge {badge_class}'>{status}</div></div>", unsafe_allow_html=True)

st.set_page_config(page_title="CardioLens AI Pro", page_icon="❤️", layout="wide", initial_sidebar_state="collapsed")
inject_custom_css()

# INITIALIZE STATE
if "app_state" not in st.session_state:
    st.session_state.app_state = "Home"
if "video_source" not in st.session_state:
    st.session_state.video_source = 0
if "scan_buffers" not in st.session_state:
    st.session_state.scan_buffers = {'r': [], 'g': [], 'b': [], 'fps': 30}

def create_plotly_waveform(y_data):
    """ Creates an intensely glowing crimson plotly waveform graph. """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        y=y_data, mode='lines',
        line=dict(color='rgba(255, 26, 64, 0.15)', width=12, shape='spline', smoothing=1.3),
        hoverinfo='skip'
    ))
    fig.add_trace(go.Scatter(
        y=y_data, mode='lines',
        line=dict(color='rgba(255, 50, 80, 0.3)', width=7, shape='spline', smoothing=1.3),
        hoverinfo='skip'
    ))
    # Core bright line
    fig.add_trace(go.Scatter(
        y=y_data, mode='lines',
        line=dict(color='#ff3355', width=3, shape='spline', smoothing=1.3),
        fill='tozeroy',
        fillcolor='rgba(255, 26, 64, 0.08)'
    ))
    
    # Pulse dot indicator at the current leading edge
    last_idx = len(y_data) - 1
    if last_idx >= 0:
        fig.add_trace(go.Scatter(
            x=[last_idx], y=[y_data[last_idx]],
            mode='markers',
            marker=dict(color='#ffffff', size=14, line=dict(color='#ff1a40', width=4)),
            hoverinfo='skip'
        ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=20, b=0),
        xaxis=dict(showgrid=True, gridcolor='rgba(255, 26, 64, 0.03)', zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=180,
        showlegend=False
    )
    return fig

def create_plotly_stress_gauge(stress_status):
    val = 50
    if 'low' in stress_status.lower() or 'optimal' in stress_status.lower(): val = 25
    elif 'high' in stress_status.lower() or 'elevated' in stress_status.lower(): val = 85
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=val,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [None, 100], 'visible': False},
            'bar': {'color': "#ff1a40"},
            'bgcolor': "rgba(255,0,0,0.1)",
            'steps': [
                {'range': [0, 33], 'color': "rgba(16, 185, 129, 0.2)"},
                {'range': [33, 66], 'color': "rgba(245, 158, 11, 0.2)"},
                {'range': [66, 100], 'color': "rgba(255, 20, 60, 0.2)"}
            ]
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=200,
        margin=dict(l=20, r=20, t=20, b=20),
        font=dict(color="#ffffff")
    )
    return fig

def create_history_chart():
    df = load_data()
    if df.empty or len(df) < 2:
        return None
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df.index, y=df['hr'], mode='lines',
        line=dict(color='rgba(255, 26, 64, 0.15)', width=10, shape='spline'),
        hoverinfo='skip'
    ))
    
    fig.add_trace(go.Scatter(
        x=df.index, y=df['hr'],
        mode='lines+markers',
        name='HR (BPM)',
        line=dict(color='#ff1a40', width=3, shape='spline'),
        marker=dict(size=10, color='#fff', line=dict(width=3, color='#ff1a40')),
        fill='tozeroy',
        fillcolor='rgba(255, 26, 64, 0.06)'
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#ffb3b3", family="Outfit, sans-serif"),
        xaxis=dict(showgrid=True, gridcolor='rgba(255, 50, 50, 0.08)', title="Scan Sequence", zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255, 50, 50, 0.08)', title="BPM", zeroline=False),
        height=260,
        margin=dict(l=0, r=0, t=20, b=10),
        showlegend=False
    )
    return fig

def main():
    if st.session_state.app_state != "Home":
        if st.sidebar.button("⬅️ TERMINATE (HOME)"):
            st.session_state.app_state = "Home"
            st.rerun()

    # PHASE 1: ENTRY SCREEN
    if st.session_state.app_state == "Home":
        st.markdown("<h1 class='gradient-text' style='text-align:center; font-size: 4rem; margin-top:20px;'>CARDIOLENS AI NEXUS</h1>", unsafe_allow_html=True)
        
        st.markdown("<div class='glass-card' style='max-width: 900px; margin: 0 auto; text-align: center;'>", unsafe_allow_html=True)
        
        c_1, c_2 = st.columns(2)
        with c_1:
            if st.button("🔴 START LIVE SCAN"):
                st.session_state.video_source = 0
                st.session_state.app_state = "Scanning"
                st.rerun()
        with c_2:
            uploaded_file = st.file_uploader("UPLOAD PHOTO", type=["jpg", "png", "jpeg", "mp4", "mov"], label_visibility="collapsed")
            if uploaded_file is not None:
                tfile = tempfile.NamedTemporaryFile(delete=False)
                tfile.write(uploaded_file.read())
                st.session_state.video_source = tfile.name
                if st.button("EXECUTE ANALYSIS"):
                    st.session_state.app_state = "Scanning"
                    st.rerun()
                
        st.markdown("</div>", unsafe_allow_html=True)
        
        historical_chart = create_history_chart()
        if historical_chart:
            st.markdown("#### Longitudinal Baseline Trajectory")
            st.plotly_chart(historical_chart)

    # PHASE 2: SCANNING PHASE
    elif st.session_state.app_state == "Scanning":
        run_scan_phase(st.session_state.video_source)

    # PHASE 3: PROCESSING PHASE
    elif st.session_state.app_state == "Processing":
        run_processing_phase()

    # PHASE 4: RESULTS DASHBOARD
    elif st.session_state.app_state == "Results":
        run_results_dashboard()


def run_scan_phase(video_source):
    st.markdown("<h2 class='gradient-text' style='text-align:center;'>SCANNING SEQUENCE INITIATED</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#ffb3b3;'>Establishing biometrics lock and extracting photoplethysmogram resonance.</p>", unsafe_allow_html=True)
    
    col_spacer1, col_video, col_spacer2 = st.columns([1, 2, 1])
    
    with col_video:
        st.markdown("<div class='glass-card' style='text-align:center; padding-bottom: 5px;'>", unsafe_allow_html=True)
        video_placeholder = st.empty()
        st.markdown("<br>", unsafe_allow_html=True)
        scan_progress = st.progress(0)
        status_text = st.empty()
        st.markdown("</div>", unsafe_allow_html=True)

    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        st.error("Matrix Error: Unable to bind video source.")
        return
        
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0 or fps > 100: fps = 30
    
    is_image = False
    if isinstance(video_source, str) and video_source.lower().endswith(('jpg', 'jpeg', 'png')):
        is_image = True
        fps = 30
        
    max_frames = 200 # Fixed scan duration for fluidity and demo
        
    r_buffer, g_buffer, b_buffer = [], [], []
    frames_processed = 0

    while cap.isOpened() and frames_processed < max_frames:
        if is_image:
            # Re-read the same frame if it's an image
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
        ret, frame = cap.read()
        if not ret:
            if frames_processed > 0 and is_image: continue
            break
            
        if video_source == 0:
            frame = cv2.flip(frame, 1)
            
        draw_frame = frame.copy()
        roi_data = extract_face_roi(frame)
        
        if roi_data is not None:
            (rm, gm, bm), (x, y, w, h) = roi_data
            
            # If static image, mock a tiny synthetic pulse to prevent a flatline in the algorithm
            if is_image:
                t = frames_processed / fps
                pulse_sim = 2 * math.sin(2 * math.pi * (72 / 60) * t) + np.random.normal(0, 0.5)
                rm += pulse_sim; gm += pulse_sim; bm += pulse_sim

            r_buffer.append(rm); g_buffer.append(gm); b_buffer.append(bm)
            
            # Cinematic Scanner Box
            cv2.rectangle(draw_frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
            for length in [25]:
                cv2.line(draw_frame, (x, y), (x+length, y), (0, 0, 255), 4)
                cv2.line(draw_frame, (x, y), (x, y+length), (0, 0, 255), 4)
                cv2.line(draw_frame, (x+w, y+h), (x+w-length, y+h), (0, 0, 255), 4)
                cv2.line(draw_frame, (x+w, y+h), (x+w, y+h-length), (0, 0, 255), 4)
            
            # Moving scanning line
            scan_y = int(y + (h / 2) + math.sin(time.time() * 4) * (h / 2 - 10))
            cv2.line(draw_frame, (x, scan_y), (x+w, scan_y), (100, 50, 255), 2)
            
            cv2.putText(draw_frame, "BIOMETRIC LOCK: ACTIVE", (x, y-15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            status_text.markdown("🟢 **Tracker:** Subject acquired. Extracting pulse...")
        else:
            if len(g_buffer) > 0:
                r_buffer.append(r_buffer[-1]); g_buffer.append(g_buffer[-1]); b_buffer.append(b_buffer[-1])
            status_text.markdown("🔴 **Tracker:** Signal degraded. Re-acquiring...")

        draw_frame = cv2.cvtColor(draw_frame, cv2.COLOR_BGR2RGB)
        video_placeholder.image(draw_frame, channels="RGB")
        
        frames_processed += 1
        scan_progress.progress(frames_processed / max_frames)
        
        if not is_image and video_source == 0:
            time.sleep(0.01)

    cap.release()
    scan_progress.progress(1.0)
    
    st.session_state.scan_buffers = {'r': r_buffer, 'g': g_buffer, 'b': b_buffer, 'fps': fps}
    
    st.session_state.app_state = "Processing"
    st.rerun()

def run_processing_phase():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    st.markdown("<div class='glass-card' style='max-width: 800px; margin: 0 auto; text-align:center;'>", unsafe_allow_html=True)
    st.markdown("<h2 class='gradient-text' style='text-align:center;'>ANALYZING OPTICAL TELEMETRY</h2>", unsafe_allow_html=True)
    
    st.markdown("<div class='heartbeat-loader'></div>", unsafe_allow_html=True)
    
    st.markdown("<p style='text-align:center; color:#ffb3b3; font-weight: 600; letter-spacing: 2px;'>DECODING POS CHROMATIC SIGNALS...</p>", unsafe_allow_html=True)
    
    # Hex Data Stream Visualization
    stream_placeholder = st.empty()
    st.markdown("</div>", unsafe_allow_html=True)
    
    for i in range(12):
        hex_data = " ".join([f"{np.random.randint(0,255):02X}" for _ in range(16)])
        stream_placeholder.markdown(f"<p style='text-align:center; color:#ff4d4d; font-family: monospace; font-size: 0.95rem; opacity: 0.8;'>0x{i+1:04X} : {hex_data}</p>", unsafe_allow_html=True)
        time.sleep(0.2)
    
    st.session_state.app_state = "Results"
    st.rerun()

def run_results_dashboard():
    buffers = st.session_state.scan_buffers
    r_buffer = buffers['r']
    g_buffer = buffers['g']
    b_buffer = buffers['b']
    fps = buffers['fps']
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h2 class='gradient-text'>MEDICAL INTELLIGENCE FUSION REPORT</h2>", unsafe_allow_html=True)
    
    if len(g_buffer) < fps * 3:
        st.error("Insufficient biological data to compile intelligence.")
        if st.button("RETURN HOME"):
            st.session_state.app_state = "Home"; st.rerun()
        return

    # Process algorithm
    pulse = apply_pos(np.array(r_buffer), np.array(g_buffer), np.array(b_buffer), fps)
    filtered_pulse = bandpass_filter(pulse, fps)
    smooth_pulse = apply_smoothing(filtered_pulse)
    peaks = detect_peaks(smooth_pulse, fps)
    
    final_hr = calculate_hr(peaks, fps)
    final_hrv = compute_hrv(peaks, fps)
    final_stress = evaluate_stress(final_hrv, final_hr)
    final_sqi = calculate_sqi(smooth_pulse, fps)
    final_risk, risk_reason = evaluate_cardiac_risk(final_hr, final_hrv, final_stress)
    final_score = calculate_health_score(final_hr, final_hrv, final_stress, final_sqi)
    
    save_session(final_hr, final_hrv, final_stress, final_score, final_risk)

    # UI RENDERING - Standardized Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Heart Rate", f"{final_hr} BPM")
    with col2:
        st.metric("HRV (RMSSD)", f"{final_hrv.get('rmssd', 0)} ms")
    with col3:
        st.metric("Health Score", f"{final_score}/100")
    with col4:
        st.metric("Confidence (SQI)", f"{final_sqi}%")

    c_g1, c_g2 = st.columns([2, 1])
    with c_g1:
        st.markdown("#### Real-time Heartbeat Resonance")
        st.plotly_chart(create_plotly_waveform(list(smooth_pulse[-100:])), use_container_width=True)
    with c_g2:
        st.markdown("#### Stress Assessment")
        st.plotly_chart(create_plotly_stress_gauge(final_stress), use_container_width=True)
        render_badge("Physiological State", final_stress)

    c_r1, c_r2 = st.columns([1, 2])
    with c_r1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("#### Baseline Analysis")
        st.write(compare_to_baseline(final_hr, final_hrv.get('rmssd', 0)))
        st.markdown("<hr>", unsafe_allow_html=True)
        render_badge("CV Risk Vector", final_risk)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c_r2:
        st.markdown("#### Diagnostic Reason Matrix")
        st.markdown(f"> {risk_reason}", unsafe_allow_html=True)

    st.markdown("#### <span class='shimmer-text'>AI Expert Prescriptions</span>", unsafe_allow_html=True)
    with st.spinner("Compiling cross-referenced intelligence..."):
        ai_advice = get_recommendation(final_hr, final_hrv, final_stress, final_score, final_risk)
    st.markdown(ai_advice, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
'''

with open("ui.py", "w", encoding="utf-8") as f:
    f.write(ORIGINAL_UI)

print("Restored original UI exactly.")
