import re

with open('ui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update render_badge
new_render_badge = '''def render_badge(label, status):
    status_lower = status.lower()
    if 'low' in status_lower or 'optimal' in status_lower:
        badge_class = 'badge-optimal'
    elif 'medium' in status_lower or 'moderate' in status_lower:
        badge_class = 'badge-warning'
    else:
        badge_class = 'badge-critical'
    return f"<div><h4 style='margin-bottom: 5px;'>{label}</h4><div class='badge {badge_class}'>{status}</div></div>"
'''

content = re.sub(
    r'def render_badge.*?st\.markdown\(f"<div class=\'glass-card\'><h4>\{label\}</h4><div class=\'badge \{badge_class\}\'>\{status\}</div></div>", unsafe_allow_html=True\)',
    new_render_badge,
    content,
    flags=re.DOTALL
)

# 2. Fix the layout block in run_results_dashboard()
# We need to replace the c_g1, c_g2 and c_r1, c_r2 columns entirely.
# Let's find: `c_g1, c_g2 = st.columns([2, 1])`
# down to `st.markdown("#### <span class='shimmer-text'>AI Expert Prescriptions</span>"`

old_layout_regex = r'c_g1, c_g2 = st\.columns\(\[2, 1\]\).*?st\.markdown\("#### <span class=\'shimmer-text\'>AI Expert Prescriptions</span>"'

new_layout = '''
    st.markdown("<br>", unsafe_allow_html=True)
    c_g1, c_g2 = st.columns([2, 1])
    with c_g1:
        st.markdown("<div class='glass-card' style='height: 100%; min-height: 280px;'>", unsafe_allow_html=True)
        st.markdown("#### Real-time Heartbeat Resonance")
        st.plotly_chart(create_plotly_waveform(list(smooth_pulse[-100:])), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c_g2:
        st.markdown("<div class='glass-card' style='height: 100%; min-height: 280px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;'>", unsafe_allow_html=True)
        st.markdown("#### Stress Assessment", unsafe_allow_html=True)
        st.plotly_chart(create_plotly_stress_gauge(final_stress), use_container_width=True)
        st.markdown(render_badge("Physiological State", final_stress), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    c_r1, c_r2, c_r3 = st.columns([1, 1, 1.5])
    with c_r1:
        st.markdown("<div class='glass-card' style='height: 100%; text-align: center;'>", unsafe_allow_html=True)
        st.markdown(render_badge("CV Risk Vector", final_risk), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c_r2:
        st.markdown("<div class='glass-card' style='height: 100%;'>", unsafe_allow_html=True)
        st.markdown("#### Baseline Analysis")
        st.markdown(f"<p style='color:#ffb3b3; line-height: 1.5;'>{compare_to_baseline(final_hr, final_hrv.get('rmssd', 0))}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c_r3:
        st.markdown("<div class='glass-card' style='height: 100%;'>", unsafe_allow_html=True)
        st.markdown("#### Diagnostic Reason Matrix")
        st.markdown(f"<div style='background: rgba(255, 0, 50, 0.1); border-left: 3px solid #ff1a40; padding: 15px; border-radius: 4px; color: #fff;'>{risk_reason}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("#### <span class='shimmer-text'>AI Expert Prescriptions</span>"'''

content = re.sub(old_layout_regex, new_layout.strip(), content, flags=re.DOTALL)

with open('ui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed layout of glass cards and badges")
