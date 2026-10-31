import re

with open('ui.py', 'r', encoding='utf-8') as f:
    content = f.read()


# 1. Update the inject_custom_css function to add high animations but keep original layout
new_css = '''def inject_custom_css():
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
            0%, 100% { transform: translateY(0) scale(1) rotate(0deg); }
            50% { transform: translateY(-40px) scale(1.15) rotate(15deg); opacity: 0.4; }
        }

        /* Highly Animated Entrances for ALL main blocks */
        [data-testid="stVerticalBlock"] > div {
            animation: bounce-in-up 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275) both;
        }
        [data-testid="stVerticalBlock"] > div:nth-child(n) {   
            animation-delay: calc(0.1s * var(--delay, 1)); 
        }

        @keyframes bounce-in-up {
            0% { opacity: 0; transform: translateY(40px) scale(0.95); filter: blur(4px); }
            100% { opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }
        }

        /* Typography */
        h1, h2, h3, h4 { color: #ffffff; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; }

        /* Value Metrics */
        div[data-testid="stMetricValue"] {
            font-size: 3.2rem; font-weight: 900; color: #ffffff;
            text-shadow: 0 0 20px rgba(255, 40, 60, 0.5), 0 0 40px rgba(255, 0, 80, 0.3);
            animation: metric-glow 3s infinite alternate ease-in-out;
        }
        @keyframes metric-glow {
            0% { text-shadow: 0 0 20px rgba(255, 40, 60, 0.5), 0 0 40px rgba(255, 0, 80, 0.3); transform: scale(1); }
            100% { text-shadow: 0 0 25px rgba(255, 60, 80, 0.8), 0 0 50px rgba(255, 20, 100, 0.5); transform: scale(1.03); }
        }
        
        div[data-testid="stMetricLabel"] { color: #ffb3b3; font-size: 1.15rem; font-weight: 600; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 8px; opacity: 0.9; }

        /* Crimson Glassmorphism Cards */
        .glass-card {
            background: linear-gradient(145deg, rgba(20, 0, 5, 0.5), rgba(10, 0, 0, 0.7));
            backdrop-filter: blur(25px); border-radius: 24px; border: 1px solid rgba(255, 80, 80, 0.15);
            border-top: 1px solid rgba(255, 120, 120, 0.3); padding: 26px;
            box-shadow: 0 15px 45px 0 rgba(0, 0, 0, 0.7), inset 0 0 25px rgba(255, 0, 50, 0.05);
            margin-bottom: 24px; transition: all 0.5s cubic-bezier(0.2, 0.8, 0.2, 1);
            position: relative; overflow: hidden; z-index: 1; animation: card-breathe 8s infinite alternate ease-in-out;
        }
        .glass-card::before {
            content: ''; position: absolute; top: 0; left: -100%; width: 50%; height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.03), transparent);
            transform: skewX(-20deg); transition: left 0.7s ease;
        }
        .glass-card:hover::before { left: 150%; }
        .glass-card:hover {
            box-shadow: 0 20px 50px 0 rgba(255, 20, 60, 0.25), inset 0 0 40px rgba(255, 0, 50, 0.1);
            border-top: 1px solid rgba(255, 100, 100, 0.6); border-bottom: 1px solid rgba(255, 80, 80, 0.2);
            transform: translateY(-8px) scale(1.02);
        }
        @keyframes card-breathe { 0% { box-shadow: 0 15px 45px 0 rgba(0, 0, 0, 0.7), inset 0 0 25px rgba(255, 0, 50, 0.05); } 100% { box-shadow: 0 15px 45px 0 rgba(0, 0, 0, 0.8), inset 0 0 35px rgba(255, 0, 50, 0.08); } }
        
        [data-testid="stMetric"], .stPlotlyChart {
            background: linear-gradient(145deg, rgba(20, 0, 5, 0.5), rgba(10, 0, 0, 0.7)) !important;
            backdrop-filter: blur(25px) !important; border: 1px solid rgba(255, 80, 80, 0.15) !important;
            border-top: 1px solid rgba(255, 120, 120, 0.3) !important; border-radius: 20px !important; padding: 20px !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.8), inset 0 0 20px rgba(255, 0, 50, 0.05) !important;
            animation: card-breathe 8s infinite alternate ease-in-out; transition: all 0.3s ease;
        }
        [data-testid="stMetric"]:hover, .stPlotlyChart:hover {
            transform: translateY(-6px) scale(1.03) !important; border-top: 1px solid rgba(255, 100, 100, 0.6) !important;
            box-shadow: 0 20px 50px 0 rgba(255, 20, 60, 0.3), inset 0 0 40px rgba(255, 0, 50, 0.2) !important;
        }
        
        [data-testid="stMainBlockContainer"] { animation: fade-slide-up 0.8s cubic-bezier(0.2, 0.8, 0.2, 1); }
        
        .badge { padding: 8px 20px; border-radius: 30px; font-weight: 900; text-transform: uppercase; font-size: 1.05rem; letter-spacing: 1.5px; display: inline-block; margin: 5px 0; backdrop-filter: blur(5px); }
        .badge-optimal { background: rgba(16, 185, 129, 0.1); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); box-shadow: 0 0 20px rgba(16, 185, 129, 0.3), inset 0 0 10px rgba(16, 185, 129, 0.1); }
        .badge-warning { background: rgba(245, 158, 11, 0.1); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); box-shadow: 0 0 20px rgba(245, 158, 11, 0.3), inset 0 0 10px rgba(245, 158, 11, 0.1); }
        .badge-critical { background: rgba(255, 20, 60, 0.1); color: #ff3333; border: 1px solid rgba(255, 51, 51, 0.6); box-shadow: 0 0 30px rgba(255, 20, 60, 0.5), inset 0 0 15px rgba(255, 20, 60, 0.2); animation: pulse-alert 1.2s infinite alternate ease-in-out; }
        @keyframes pulse-alert { 0% { box-shadow: 0 0 25px rgba(255, 20, 60, 0.5), inset 0 0 15px rgba(255, 20, 60, 0.2); } 100% { box-shadow: 0 0 45px rgba(255, 20, 60, 0.9), inset 0 0 25px rgba(255, 20, 60, 0.4); border-color: #ff4d4d; } }

        .gradient-text {
            background: linear-gradient(135deg, #ff4d4d 0%, #ff0044 25%, #ffb3b3 50%, #ff0044 75%, #ff4d4d 100%);
            background-size: 300% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900;
            animation: gradient-flow 4s linear infinite; text-shadow: 0 0 30px rgba(255, 0, 50, 0.3);
        }
        @keyframes gradient-flow { to { background-position: 300% center; } }

        .shimmer-text {
            color: rgba(255, 255, 255, 0.9);
            background: linear-gradient(90deg, rgba(255, 255, 255, 0.8) 0%, rgba(255, 50, 100, 1) 50%, rgba(255, 255, 255, 0.8) 100%);
            background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            animation: shimmer 3s infinite linear; font-weight: 600;
        }
        @keyframes shimmer { to { background-position: 200% center; } }

        .loader-glow {
            width: 80px; height: 80px; border-radius: 50%; border: 4px solid rgba(255, 0, 50, 0.2); border-top: 4px solid #ff1a40;
            animation: spin 1s linear infinite, glow 2s ease-in-out infinite alternate; margin: 40px auto;
        }
        @keyframes spin { 100% { transform: rotate(360deg); } }
        @keyframes glow { 0% { box-shadow: 0 0 20px rgba(255, 0, 50, 0.5); } 100% { box-shadow: 0 0 60px rgba(255, 0, 50, 1); } }

        div.stButton > button {
            background: linear-gradient(145deg, rgba(40, 0, 0, 0.8) 0%, rgba(15, 0, 0, 0.9) 100%);
            border: 1px solid rgba(255, 50, 50, 0.3); border-top: 1px solid rgba(255, 100, 100, 0.5); border-radius: 14px;
            color: #ff4d4d !important; font-weight: 900; letter-spacing: 2.5px; transition: all 0.4s cubic-bezier(0.2, 0.8, 0.2, 1);
            box-shadow: 0 10px 30px rgba(0,0,0,0.8), inset 0 0 10px rgba(255, 50, 50, 0.05); height: 58px; width: 100%; text-transform: uppercase; position: relative; overflow: hidden; backdrop-filter: blur(10px);
        }
        div.stButton > button::after {
            content: ''; position: absolute; top: 0; left: -100%; width: 50%; height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 100, 100, 0.2), transparent);
            transform: skewX(-20deg); transition: left 0.6s ease;
        }
        div.stButton > button:hover::after { left: 150%; }
        div.stButton > button:hover {
            border: 1px solid rgba(255, 50, 50, 0.8); border-top: 1px solid rgba(255, 150, 150, 1);
            box-shadow: 0 15px 40px rgba(255, 0, 50, 0.4), inset 0 0 20px rgba(255, 0, 50, 0.2); transform: translateY(-4px) scale(1.05);
            color: #ffffff !important; background: linear-gradient(145deg, rgba(60, 0, 0, 0.9) 0%, rgba(20, 0, 0, 1) 100%);
        }
        div.stButton > button:active {
            transform: scale(0.92) translateY(2px) !important; background: radial-gradient(circle, rgba(255, 100, 100, 0.5) 0%, rgba(20, 0, 0, 1) 100%) !important;
            box-shadow: inset 0 0 25px rgba(255, 50, 50, 0.6), 0 0 10px rgba(255, 20, 60, 0.4) !important;
        }

        .stProgress > div > div > div { background-image: linear-gradient(to right, #cc0000, #ff1a1a, #ff4d4d) !important; box-shadow: 0 0 20px rgba(255, 20, 60, 0.9), 0 0 40px rgba(255, 0, 50, 0.5); border-radius: 10px; }
        
        hr { border-top: 1px solid rgba(255, 50, 50, 0.15); box-shadow: 0 1px 10px rgba(255, 0, 50, 0.2); }

        .heartbeat-loader {
            display: inline-block; width: 150px; height: 60px;
            background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 100"><path fill="none" stroke="%23ff1a40" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" d="M 0 50 L 50 50 L 70 10 L 90 90 L 110 30 L 130 50 L 200 50"/></svg>') no-repeat center;
            background-size: cover; filter: drop-shadow(0 0 15px rgba(255, 26, 64, 0.9)); animation: pulse-svg 1.2s infinite ease-in-out; margin: 20px 0; position: relative;
        }
        .heartbeat-loader::after {
            content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(90deg, transparent 50%, rgba(5, 0, 0, 1) 50%); background-size: 200% 100%; animation: scanline 1.5s infinite linear;
        }
        @keyframes pulse-svg { 0%, 100% { filter: drop-shadow(0 0 8px rgba(255, 26, 64, 0.5)); transform: scale(1); } 50% { filter: drop-shadow(0 0 25px rgba(255, 26, 64, 1)); transform: scale(1.05); } }
        @keyframes scanline { 0% { background-position: 100% 0; } 100% { background-position: -100% 0; } }

        @keyframes fade-slide-up { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        .ai-diagnosis-container { background: rgba(40, 0, 10, 0.4); border-left: 4px solid #ff1a40; padding: 24px; margin-bottom: 20px; border-radius: 4px 12px 12px 4px; box-shadow: inset 5px 0 15px rgba(255, 20, 60, 0.1); animation: fade-slide-up 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) both; animation-delay: 0.1s; }
        .ai-action-list { background: rgba(20, 0, 5, 0.6); padding: 24px; border-radius: 12px; border: 1px solid rgba(255, 50, 50, 0.2); animation: fade-slide-up 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) both; animation-delay: 0.5s; }
        
        .dashboard-wrapper { animation: fade-slide-up 0.9s cubic-bezier(0.2, 0.8, 0.2, 1); }

        header[data-testid="stHeader"] { background-color: transparent !important; visibility: hidden !important; }
        .block-container { padding-top: 2rem !important; }

        [data-testid="stFileUploader"] { background: linear-gradient(145deg, rgba(40, 0, 5, 0.6), rgba(15, 0, 0, 0.8)) !important; border: 1px dashed rgba(255, 50, 50, 0.5) !important; border-radius: 16px !important; padding: 20px !important; transition: all 0.3s ease-in-out !important; box-shadow: inset 0 0 15px rgba(255, 0, 50, 0.1) !important; }
        [data-testid="stFileUploader"]:hover { border: 1px dashed rgba(255, 100, 100, 0.8) !important; background: linear-gradient(145deg, rgba(60, 0, 10, 0.7), rgba(25, 0, 0, 0.9)) !important; box-shadow: inset 0 0 25px rgba(255, 0, 50, 0.2), 0 0 15px rgba(255, 20, 60, 0.3) !important; }
        [data-testid="stFileUploader"] section { color: #ffb3b3 !important; }
        [data-testid="stFileUploader"] svg { fill: #ff4d4d !important; }
        [data-testid="stFileUploader"] div { color: #ffb3b3 !important; }
        [data-testid="stFileUploader"] .stButton > button { background: rgba(255, 20, 60, 0.2) !important; color: #ffffff !important; border: 1px solid rgba(255, 50, 50, 0.5) !important; height: 40px !important; box-shadow: none !important; }
        
        </style>
        
        <!-- Bubble Engine UI Injection -->
        <div class="bubble" style="width: 18px; height: 18px; left: 12%; top: 25%; animation-duration: 10s;"></div>
        <div class="bubble" style="width: 28px; height: 28px; left: 82%; top: 55%; animation-duration: 12s;"></div>
        <div class="bubble" style="width: 12px; height: 12px; left: 45%; top: 85%; animation-duration: 8s;"></div>
        <div class="bubble" style="width: 35px; height: 35px; left: 72%; top: 12%; animation-duration: 14s;"></div>
        <div class="bubble" style="width: 20px; height: 20px; left: 25%; top: 75%; animation-duration: 11s;"></div>
    """, unsafe_allow_html=True)'''

pattern1 = re.compile(r'def inject_custom_css\(\):.*?\"\"\", unsafe_allow_html=True\)', re.DOTALL)
content = pattern1.sub(new_css, content)

# 2. Add history chart to results page
# find `st.markdown(ai_advice, unsafe_allow_html=True)` 
# and add history chart below it

append_graphs = '''st.markdown(ai_advice, unsafe_allow_html=True)
    
    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    st.markdown("<h3 class='gradient-text'>Advanced Diagnostic Visuals</h3>", unsafe_allow_html=True)
    
    c_h1, c_h2 = st.columns([1, 1])
    with c_h1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("#### Longitudinal Pattern Analysis")
        h_chart = create_history_chart()
        if h_chart is not None:
            st.plotly_chart(h_chart, use_container_width=True)
        else:
            st.info("Continuous scan data required to plot longitudinal trajectory.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c_h2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("#### Signal Morphology View")
        # Add a longer waveform plot for analysis
        if len(smooth_pulse) > 300:
            long_wave = list(smooth_pulse[-300:])
        else:
            long_wave = list(smooth_pulse)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=long_wave, mode='lines', line=dict(color='#ff1a40', width=2), fill='tozeroy', fillcolor='rgba(255, 26, 64, 0.1)'))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=10, b=0), xaxis=dict(showgrid=True, gridcolor='rgba(255, 50, 50, 0.08)'), yaxis=dict(showgrid=True, gridcolor='rgba(255, 50, 50, 0.08)'), height=260)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
'''

content = content.replace('st.markdown(ai_advice, unsafe_allow_html=True)', append_graphs)

with open('ui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated ui.py with highly animated CSS and final graphs")
