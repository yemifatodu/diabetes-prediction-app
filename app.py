import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.graph_objects as go

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GlucoseIQ | Clinical Risk Intelligence",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Design System ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp { background-color: #FFFFFF; }
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }

    [data-testid="stSidebar"] {
        background: #F0F9FF;
        border-right: 1px solid #BAE6FD;
    }
    [data-testid="stSidebar"] * { color: #0C4A6E !important; }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 { color: #0891B2 !important; }
    [data-testid="stSidebar"] a { color: #0891B2 !important; text-decoration: none; }
    [data-testid="stSidebar"] a:hover { color: #0E7490 !important; text-decoration: underline; }
    [data-testid="stSidebar"] hr { border-color: #BAE6FD !important; }
    [data-testid="stAppViewContainer"] > .main { background-color: #FFFFFF; }

    label, .stSlider label, .stSelectbox label, .stNumberInput label {
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        color: #0C4A6E !important;
        letter-spacing: 0.3px !important;
    }

    .stButton > button[kind="primary"] {
        background: #0891B2 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        padding: 14px 0 !important;
        box-shadow: 0 4px 14px rgba(8,145,178,0.3) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #0E7490 !important;
        box-shadow: 0 6px 20px rgba(8,145,178,0.45) !important;
    }

    .normal-range {
        font-size: 0.64rem;
        color: #94A3B8;
        font-family: 'DM Mono', monospace;
        margin-top: 2px;
        margin-bottom: 10px;
    }

    .result-panel-high {
        background: #FFF1F2;
        border: 1.5px solid #FDA4AF;
        border-radius: 14px;
        overflow: hidden;
        margin-bottom: 16px;
    }
    .result-panel-low {
        background: #F0F9FF;
        border: 1.5px solid #7DD3FC;
        border-radius: 14px;
        overflow: hidden;
        margin-bottom: 16px;
    }
    .result-panel-top-high { background: #DC2626; padding: 18px 22px; }
    .result-panel-top-low  { background: #0891B2; padding: 18px 22px; }
    .result-panel-verdict  { font-size: 1.1rem; font-weight: 700; color: #FFFFFF; }
    .result-panel-sublabel { font-size: 0.67rem; color: rgba(255,255,255,0.75);
                              letter-spacing: 1.5px; text-transform: uppercase; margin-top: 3px; }
    .result-panel-body     { padding: 18px 22px; }
    .result-prob-high { font-size: 3rem; font-weight: 700; color: #DC2626;
                        line-height: 1; font-family: 'DM Mono', monospace; }
    .result-prob-low  { font-size: 3rem; font-weight: 700; color: #0891B2;
                        line-height: 1; font-family: 'DM Mono', monospace; }
    .result-prob-label { font-size: 0.67rem; font-weight: 600; letter-spacing: 1.5px;
                         text-transform: uppercase; color: #64748B; margin-top: 4px; }

    .rbar-track { background: #E2E8F0; border-radius: 999px; height: 6px;
                  margin: 12px 0 5px 0; overflow: hidden; }
    .rbar-fill-high { height: 100%; border-radius: 999px;
                      background: linear-gradient(90deg, #FCA5A5, #DC2626); }
    .rbar-fill-low  { height: 100%; border-radius: 999px;
                      background: linear-gradient(90deg, #7DD3FC, #0891B2); }

    .bm-row { display: flex; align-items: center; justify-content: space-between;
               padding: 10px 0; border-bottom: 1px solid #F1F5F9; }
    .bm-row:last-child { border-bottom: none; }
    .bm-name { font-size: 0.77rem; font-weight: 600; color: #334155; }
    .bm-val  { font-size: 0.77rem; font-weight: 700; color: #0C4A6E;
                font-family: 'DM Mono', monospace; }
    .pill-red   { background:#FEE2E2; color:#DC2626; font-size:0.64rem; font-weight:700;
                  padding:3px 9px; border-radius:999px; }
    .pill-amber { background:#FEF9C3; color:#CA8A04; font-size:0.64rem; font-weight:700;
                  padding:3px 9px; border-radius:999px; }
    .pill-teal  { background:#E0F2FE; color:#0891B2; font-size:0.64rem; font-weight:700;
                  padding:3px 9px; border-radius:999px; }

    .protocol-step { display:flex; gap:14px; align-items:flex-start;
                     padding:13px 0; border-bottom:1px solid #F1F5F9; }
    .protocol-step:last-child { border-bottom: none; }
    .step-num { width:28px; height:28px; min-width:28px; border-radius:50%;
                background:#E0F2FE; color:#0891B2; font-size:0.74rem; font-weight:700;
                display:flex; align-items:center; justify-content:center; }
    .step-num-high { width:28px; height:28px; min-width:28px; border-radius:50%;
                     background:#FEE2E2; color:#DC2626; font-size:0.74rem; font-weight:700;
                     display:flex; align-items:center; justify-content:center; }
    .step-body strong { font-size:0.81rem; font-weight:700; color:#0C4A6E;
                        display:block; margin-bottom:2px; }
    .step-body span   { font-size:0.74rem; color:#64748B; line-height:1.5; }

    .disclaimer { background:#FFFBEB; border:1px solid #FDE68A;
                  border-left:3px solid #F59E0B; border-radius:8px;
                  padding:11px 15px; font-size:0.71rem; color:#78350F;
                  margin-top:20px; line-height:1.7; }

    [data-testid="stMetric"] { background:#F0F9FF; border:1px solid #BAE6FD;
                                border-radius:10px; padding:12px 16px; }
    [data-testid="stMetricLabel"] { font-size:0.67rem !important; font-weight:700 !important;
                                    letter-spacing:1.2px !important; text-transform:uppercase !important;
                                    color:#64748B !important; }
    [data-testid="stMetricValue"] { font-size:1.3rem !important; font-weight:700 !important;
                                    color:#0C4A6E !important; }
    [data-testid="stExpander"] { border:1px solid #E0F2FE !important;
                                  border-radius:10px !important; background:#FAFCFF !important; }
</style>
""", unsafe_allow_html=True)

# ── Load models ───────────────────────────────────────────────────────────────
@st.cache_resource
def load_models():
    with open('models/random_forest_model.pkl', 'rb') as f:
        rf_model = pickle.load(f)
    with open('models/xgboost_model.pkl', 'rb') as f:
        xgb_model = pickle.load(f)
    with open('models/scaler_v2.pkl', 'rb') as f:
        scaler = pickle.load(f)
    with open('models/features_v2.pkl', 'rb') as f:
        features = pickle.load(f)
    return rf_model, xgb_model, scaler, features

try:
    rf_model, xgb_model, scaler, features = load_models()
    model_ok = True
except Exception as e:
    model_ok = False
    model_error = str(e)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:10px 0 20px 0;">
        <div style="font-size:1.3rem;font-weight:700;color:#0891B2;">🩺 GlucoseIQ</div>
        <div style="font-size:0.65rem;letter-spacing:2px;text-transform:uppercase;
                    color:#64748B;margin-top:3px;">Clinical Risk Intelligence</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Platform")
    st.markdown("""
    <div style="font-size:0.79rem;color:#0C4A6E;line-height:1.9;">
    Dual-ensemble ML system applying <strong>Random Forest</strong> and
    <strong>XGBoost</strong> to stratify Type 2 diabetes onset risk
    from eight validated clinical biomarkers.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Model Performance")
    st.markdown("""
    <div style="font-size:0.77rem;color:#334155;line-height:2.3;">
    <span style="color:#64748B;">Random Forest AUC</span><br/>
    <strong style="color:#0891B2;font-size:1rem;">0.948</strong><br/>
    <span style="color:#64748B;">XGBoost AUC</span><br/>
    <strong style="color:#0891B2;font-size:1rem;">0.947</strong><br/>
    <span style="color:#64748B;">Dataset</span><br/>Pima Indians · NIDDK · 768 records<br/>
    <span style="color:#64748B;">Population</span><br/>Female patients · Ages 21–81
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Links")
    st.markdown("""
    <div style="font-size:0.79rem;line-height:2.5;">
    <a href="https://github.com/yemifatodu" target="_blank">⟶ GitHub</a><br/>
    <a href="https://yemifatodu.online" target="_blank">⟶ Portfolio</a><br/>
    <a href="https://linkedin.com/in/yemifatodu" target="_blank">⟶ LinkedIn</a>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.69rem;color:#475569;line-height:1.8;">
    <strong style="color:#0891B2;">Yemi Fatodu</strong><br/>
    Data Scientist · BI Specialist<br/>Full-Stack Product Builder<br/><br/>
    <em style="color:#94A3B8;">Available for freelance &amp; contract work</em>
    </div>
    """, unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
hc1, hc2 = st.columns([3, 1])
with hc1:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:14px;padding-bottom:0px;
                border-bottom:2px solid #E0F2FE;margin-bottom:0px;">
        <div style="width:80px;height:80px;background:linear-gradient(135deg,#0891B2,#0E7490);
                    border-radius:12px;display:flex;align-items:center;
                    justify-content:center;font-size:2.9rem;">🩺</div>
        <div>
            <div style="font-size:3.2rem;font-weight:700;color:#0C4A6E;letter-spacing:-1px;margin-bottom:2px;">
                Glucose<span style="color:#0891B2;">IQ</span>
            </div>
            <div style="font-size:1rem;letter-spacing:2px;text-transform:uppercase;color:#94A3B8;font-weight:700;">
                Clinical Diabetes Risk Assessment Platform
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with hc2:
    st.markdown("""
    <div style="display:flex;justify-content:flex-end;padding-top:6px;">
        <div style="background:#F0F9FF;border:1px solid #BAE6FD;border-radius:8px;
                    padding:8px 14px;font-size:0.71rem;font-weight:600;color:#0891B2;
                    display:flex;align-items:center;gap:7px;">
            <span style="width:7px;height:7px;background:#0891B2;
                         border-radius:50%;display:inline-block;"></span>
            DUAL MODEL ACTIVE
        </div>
    </div>
    """, unsafe_allow_html=True)

if not model_ok:
    st.error(f"Model error: {model_error}")
    st.stop()

# ── Two-panel layout ──────────────────────────────────────────────────────────
left_panel, right_panel = st.columns([1.05, 1], gap="large")

# ════════════════════ LEFT — Patient Intake ════════════════════
with left_panel:

    st.markdown("""
    <div style="font-size:0.67rem;font-weight:700;letter-spacing:2px;
                text-transform:uppercase;color:#64748B;margin-bottom:8px;">Active Model</div>
    """, unsafe_allow_html=True)
    model_choice = st.selectbox("Active Model", [
        "Random Forest (AUC: 0.948)", "XGBoost (AUC: 0.947)"
    ], label_visibility="collapsed")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # CARD 1 — Metabolic
    st.markdown("""
    <div style="background:#FAFCFF;border:1px solid #E0F2FE;border-top:3px solid #0891B2;
                border-radius:12px;padding:18px 20px 6px 20px;margin-bottom:14px;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
            <div style="width:32px;height:32px;background:#E0F2FE;border-radius:8px;
                        display:flex;align-items:center;justify-content:center;">🧪</div>
            <div>
                <div style="font-size:0.69rem;font-weight:700;letter-spacing:2px;
                            text-transform:uppercase;color:#0891B2;">Metabolic Markers</div>
                <div style="font-size:0.67rem;color:#94A3B8;">Glucose, insulin &amp; body composition</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    mc1, mc2 = st.columns(2)
    with mc1:
        glucose = st.number_input("Glucose (mg/dL)", min_value=0, max_value=300, value=110)
        st.markdown('<div class="normal-range">Normal: 70–99 · Prediabetes: 100–125</div>', unsafe_allow_html=True)
        bmi = st.number_input("BMI", min_value=0.0, max_value=70.0, value=25.0)
        st.markdown('<div class="normal-range">Normal: 18.5–24.9 · Obese: ≥30</div>', unsafe_allow_html=True)
    with mc2:
        insulin = st.number_input("Insulin (IU/mL)", min_value=0, max_value=900, value=80)
        st.markdown('<div class="normal-range">Normal: 16–166 IU/mL</div>', unsafe_allow_html=True)
        skin_thickness = st.number_input("Skin Thickness (mm)", min_value=0, max_value=100, value=20)
        st.markdown('<div class="normal-range">Triceps skinfold · Avg: 20–30mm</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # CARD 2 — Cardiovascular
    st.markdown("""
    <div style="background:#FFFBFB;border:1px solid #FEE2E2;border-top:3px solid #F87171;
                border-radius:12px;padding:18px 20px 6px 20px;margin-bottom:14px;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
            <div style="width:32px;height:32px;background:#FEE2E2;border-radius:8px;
                        display:flex;align-items:center;justify-content:center;">❤️</div>
            <div>
                <div style="font-size:0.69rem;font-weight:700;letter-spacing:2px;
                            text-transform:uppercase;color:#DC2626;">Cardiovascular</div>
                <div style="font-size:0.67rem;color:#94A3B8;">Blood pressure indicators</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    blood_pressure = st.number_input("Blood Pressure (mmHg)", min_value=0, max_value=200, value=70)
    st.markdown('<div class="normal-range">Normal: &lt;120 · Elevated: 120–139 · Hypertensive: ≥140</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # CARD 3 — Demographics
    st.markdown("""
    <div style="background:#FFFDF0;border:1px solid #FEF08A;border-top:3px solid #CA8A04;
                border-radius:12px;padding:18px 20px 6px 20px;margin-bottom:16px;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
            <div style="width:32px;height:32px;background:#FEF9C3;border-radius:8px;
                        display:flex;align-items:center;justify-content:center;">👤</div>
            <div>
                <div style="font-size:0.69rem;font-weight:700;letter-spacing:2px;
                            text-transform:uppercase;color:#CA8A04;">Patient Demographics</div>
                <div style="font-size:0.67rem;color:#94A3B8;">Age, reproductive &amp; genetic history</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    dc1, dc2 = st.columns(2)
    with dc1:
        age = st.number_input("Age (years)", min_value=21, max_value=100, value=30)
        st.markdown('<div class="normal-range">Elevated risk after age 45</div>', unsafe_allow_html=True)
    with dc2:
        pregnancies = st.number_input("Pregnancies", min_value=0, max_value=20, value=1)
        st.markdown('<div class="normal-range">Gestational risk: ≥5 pregnancies</div>', unsafe_allow_html=True)

    dpf = st.number_input("Diabetes Pedigree Function", min_value=0.0, max_value=3.0, value=0.3, step=0.01)
    st.markdown('<div class="normal-range">Genetic likelihood score · Low: &lt;0.5 · High: &gt;1.0</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    predict_clicked = st.button("⟶  RUN CLINICAL RISK ASSESSMENT", type="primary", use_container_width=True)

# ════════════════════ RIGHT — Results ════════════════════
with right_panel:

    if not predict_clicked:
        st.markdown("""
        <div style="background:#F0F9FF;border:1px solid #BAE6FD;border-radius:14px;
                    padding:44px 32px;text-align:center;margin-top:16px;">
            <div style="font-size:2.5rem;margin-bottom:14px;">🩺</div>
            <div style="font-size:1rem;font-weight:700;color:#0C4A6E;margin-bottom:8px;">
                Awaiting Patient Data
            </div>
            <div style="font-size:0.79rem;color:#64748B;line-height:1.7;
                        max-width:260px;margin:0 auto;">
                Complete the clinical biomarker form and run the assessment
                to receive a full risk stratification report.
            </div>
            <div style="margin-top:24px;padding-top:20px;border-top:1px solid #BAE6FD;">
                <div style="font-size:0.67rem;letter-spacing:1.5px;text-transform:uppercase;
                            color:#94A3B8;margin-bottom:10px;">Models on standby</div>
                <div style="display:flex;justify-content:center;gap:12px;">
                    <div style="background:#FFFFFF;border:1px solid #BAE6FD;border-radius:8px;
                                padding:8px 16px;font-size:0.74rem;font-weight:600;color:#0891B2;">
                        RF · AUC 0.948
                    </div>
                    <div style="background:#FFFFFF;border:1px solid #BAE6FD;border-radius:8px;
                                padding:8px 16px;font-size:0.74rem;font-weight:600;color:#0891B2;">
                        XGB · AUC 0.947
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        bmi_category = 0 if bmi < 18.5 else 1 if bmi < 24.9 else 2 if bmi < 29.9 else 3
        glucose_risk = 0 if glucose < 100 else 1 if glucose < 126 else 2
        age_group    = 0 if age <= 30 else 1 if age <= 45 else 2

        input_data = pd.DataFrame([[
            pregnancies, glucose, blood_pressure, skin_thickness,
            insulin, bmi, dpf, age, bmi_category, glucose_risk, age_group
        ]], columns=features)

        input_scaled   = scaler.transform(input_data)
        selected_model = rf_model if "Random Forest" in model_choice else xgb_model
        prediction     = selected_model.predict(input_scaled)[0]
        probability    = selected_model.predict_proba(input_scaled)[0]
        diabetes_prob  = probability[1] * 100
        no_diab_prob   = probability[0] * 100
        confidence     = max(probability) * 100
        model_tag      = "RF" if "Random Forest" in model_choice else "XGB"

        # Verdict
        bar_pct = int(diabetes_prob)
        if prediction == 1:
            st.markdown(f"""
            <div class="result-panel-high">
                <div class="result-panel-top-high">
                    <div class="result-panel-sublabel">⚠ Risk Assessment Complete</div>
                    <div class="result-panel-verdict">HIGH RISK — DIABETES LIKELY</div>
                </div>
                <div class="result-panel-body">
                    <div class="result-prob-high">{diabetes_prob:.1f}%</div>
                    <div class="result-prob-label">Predicted Diabetes Probability</div>
                    <div class="rbar-track">
                        <div class="rbar-fill-high" style="width:{bar_pct}%;"></div>
                    </div>
                    <div style="font-size:0.67rem;color:#94A3B8;">
                        Threshold: 50% &nbsp;·&nbsp; Confidence: {confidence:.1f}% &nbsp;·&nbsp; Model: {model_tag}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="result-panel-low">
                <div class="result-panel-top-low">
                    <div class="result-panel-sublabel">✔ Risk Assessment Complete</div>
                    <div class="result-panel-verdict">LOW RISK — DIABETES UNLIKELY</div>
                </div>
                <div class="result-panel-body">
                    <div class="result-prob-low">{no_diab_prob:.1f}%</div>
                    <div class="result-prob-label">Predicted No-Diabetes Probability</div>
                    <div class="rbar-track">
                        <div class="rbar-fill-low" style="width:{int(no_diab_prob)}%;"></div>
                    </div>
                    <div style="font-size:0.67rem;color:#94A3B8;">
                        Threshold: 50% &nbsp;·&nbsp; Confidence: {confidence:.1f}% &nbsp;·&nbsp; Model: {model_tag}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=diabetes_prob,
            number={'suffix': '%', 'font': {'size': 26, 'color': '#0C4A6E', 'family': 'DM Sans'}},
            title={'text': "Diabetes Risk Score", 'font': {'size': 10, 'color': '#94A3B8', 'family': 'DM Sans'}},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': '#CBD5E0', 'tickfont': {'size': 9}},
                'bar': {'color': "#DC2626" if prediction == 1 else "#0891B2", 'thickness': 0.2},
                'bgcolor': '#F8FAFC', 'bordercolor': '#E2E8F0',
                'steps': [
                    {'range': [0,  35],  'color': '#E0F2FE'},
                    {'range': [35, 60],  'color': '#FEF9C3'},
                    {'range': [60, 100], 'color': '#FEE2E2'}
                ],
                'threshold': {'line': {'color': '#64748B', 'width': 2}, 'thickness': 0.75, 'value': 50}
            }
        ))
        fig.update_layout(height=200, margin=dict(t=46, b=0, l=10, r=10),
                          paper_bgcolor='#FFFFFF', plot_bgcolor='#FFFFFF')
        st.plotly_chart(fig, use_container_width=True)

        # Biomarker status
        st.markdown("""
        <div style="font-size:0.67rem;font-weight:700;letter-spacing:2px;
                    text-transform:uppercase;color:#64748B;margin-bottom:8px;">Biomarker Status</div>
        <div style="background:#FAFCFF;border:1px solid #E0F2FE;border-radius:10px;
                    padding:4px 16px;margin-bottom:14px;">
        """, unsafe_allow_html=True)

        def get_pill(val, red_fn, amber_fn):
            if red_fn(val):   return "pill-red",   "HIGH"
            if amber_fn(val): return "pill-amber", "ELEVATED"
            return "pill-teal", "NORMAL"

        rows = [
            ("Glucose",        f"{glucose} mg/dL",
             get_pill(glucose,        lambda x: x >= 126, lambda x: x >= 100)),
            ("BMI",            f"{bmi:.1f}",
             get_pill(bmi,            lambda x: x >= 30,  lambda x: x >= 25)),
            ("Blood Pressure", f"{blood_pressure} mmHg",
             get_pill(blood_pressure, lambda x: x >= 140, lambda x: x >= 120)),
            ("Insulin",        f"{insulin} IU/mL",
             get_pill(insulin,        lambda x: x > 200,  lambda x: x > 100)),
            ("Age",            f"{age} yrs",
             get_pill(age,            lambda x: x > 45,   lambda x: x > 30)),
            ("DPF Score",      f"{dpf:.2f}",
             get_pill(dpf,            lambda x: x > 1.0,  lambda x: x >= 0.5)),
        ]

        for name, value, (pill_cls, pill_label) in rows:
            st.markdown(f"""
            <div class="bm-row">
                <span class="bm-name">{name}</span>
                <span style="display:flex;align-items:center;gap:8px;">
                    <span class="bm-val">{value}</span>
                    <span class="{pill_cls}">{pill_label}</span>
                </span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Protocol
        st.markdown("""
        <div style="font-size:0.67rem;font-weight:700;letter-spacing:2px;
                    text-transform:uppercase;color:#64748B;margin-bottom:8px;">Clinical Protocol</div>
        <div style="background:#FAFCFF;border:1px solid #E0F2FE;border-radius:10px;
                    padding:4px 16px;margin-bottom:14px;">
        """, unsafe_allow_html=True)

        if prediction == 1:
            steps = [
                ("Confirmatory Testing",    "Order FPG and HbA1c. FPG ≥126 mg/dL or HbA1c ≥6.5% confirms diagnosis."),
                ("Specialist Referral",     "Refer to endocrinologist for full clinical evaluation and management plan."),
                ("Lifestyle Intervention",  "Structured nutrition counselling + 150 min/week physical activity protocol."),
                ("Pharmacological Review",  "Assess metformin candidacy per ADA/WHO guidelines."),
                ("Monitoring Schedule",     "3-month follow-up: repeat HbA1c, lipid panel, renal function."),
            ]
            nc = "step-num-high"
        else:
            steps = [
                ("Routine Screening",       "Annual FPG and HbA1c as standard preventive care."),
                ("Lifestyle Optimisation",  "Mediterranean diet + ≥150 min/week moderate aerobic activity."),
                ("Risk Factor Surveillance","Monitor BMI, BP, and lipid profile at each encounter."),
                ("Patient Education",       "Provide diabetes prevention resources and self-monitoring tools."),
                ("Annual Review",           "12-month wellness check with updated risk stratification."),
            ]
            nc = "step-num"

        for i, (title, desc) in enumerate(steps, 1):
            st.markdown(f"""
            <div class="protocol-step">
                <div class="{nc}">{i}</div>
                <div class="step-body"><strong>{title}</strong><span>{desc}</span></div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("📋 Full Patient Input Record"):
            st.dataframe(input_data.iloc[:, :8].T.rename(columns={0: 'Value'}), use_container_width=True)

        st.markdown("""
        <div class="disclaimer">
            ⚠️ <strong>Clinical Disclaimer:</strong> GlucoseIQ is an AI-assisted decision support tool
            for educational and portfolio demonstration purposes only. Not a substitute for professional
            medical advice, diagnosis, or treatment. All clinical decisions must be made by qualified
            healthcare professionals. &nbsp;|&nbsp; Dataset: Pima Indians Diabetes Database · NIDDK.
            &nbsp;|&nbsp; Built by <strong>Yemi Fatodu</strong> — Data Scientist &amp; Full-Stack Product Builder.
        </div>
        """, unsafe_allow_html=True)
