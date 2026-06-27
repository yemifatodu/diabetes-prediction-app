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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp { background-color: #F4F7F9; }

    /* ── Hide Streamlit chrome ── */
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0B2545 0%, #0D2E55 60%, #0F3460 100%);
        border-right: 1px solid #1A6B4A33;
    }
    [data-testid="stSidebar"] * { color: #CBD5E0 !important; }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 { color: #2ECC8A !important; }
    [data-testid="stSidebar"] a { color: #2ECC8A !important; text-decoration: none; }
    [data-testid="stSidebar"] a:hover { color: #56E6A8 !important; text-decoration: underline; }
    [data-testid="stSidebar"] hr { border-color: #2ECC8A33 !important; }

    /* ── Main background ── */
    [data-testid="stAppViewContainer"] > .main { background-color: #F4F7F9; }

    /* ── Header bar ── */
    .top-bar {
        background: linear-gradient(135deg, #0B2545 0%, #0D2E55 100%);
        padding: 22px 36px;
        border-radius: 12px;
        margin-bottom: 24px;
        border-bottom: 3px solid #2ECC8A;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .top-bar-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.9rem;
        font-weight: 700;
        color: #FFFFFF;
        margin: 0;
    }
    .top-bar-title span { color: #2ECC8A; }
    .top-bar-subtitle {
        font-size: 0.78rem;
        color: #94A3B8;
        margin-top: 4px;
        letter-spacing: 1.8px;
        text-transform: uppercase;
    }
    .top-bar-badge {
        background: #2ECC8A22;
        border: 1px solid #2ECC8A66;
        color: #2ECC8A;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    /* ── Section label ── */
    .section-label {
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 2.5px;
        text-transform: uppercase;
        color: #64748B;
        margin-bottom: 10px;
        padding-left: 2px;
    }

    /* ── Cards ── */
    .card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 22px 26px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 4px rgba(11,37,69,0.06);
        margin-bottom: 18px;
    }
    .card-title {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 1.8px;
        text-transform: uppercase;
        color: #0B2545;
        border-left: 3px solid #2ECC8A;
        padding-left: 10px;
        margin-bottom: 18px;
    }

    /* ── KPI strip ── */
    .kpi-row {
        display: flex;
        gap: 14px;
        margin-bottom: 22px;
        flex-wrap: wrap;
    }
    .kpi-chip {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 14px 20px;
        flex: 1;
        min-width: 120px;
        box-shadow: 0 1px 3px rgba(11,37,69,0.05);
    }
    .kpi-chip-accent {
        width: 26px;
        height: 3px;
        background: #2ECC8A;
        border-radius: 2px;
        margin-bottom: 8px;
    }
    .kpi-chip-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #0B2545;
        line-height: 1;
    }
    .kpi-chip-label {
        font-size: 0.68rem;
        font-weight: 600;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        color: #64748B;
        margin-top: 4px;
    }

    /* ── Input labels ── */
    label, .stSlider label, .stSelectbox label, .stNumberInput label {
        font-size: 0.76rem !important;
        font-weight: 600 !important;
        color: #334155 !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
    }

    /* ── Primary button ── */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #0B2545 0%, #0D2E55 100%) !important;
        color: #2ECC8A !important;
        border: 1px solid #2ECC8A !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 0.88rem !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
        padding: 14px 0 !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 14px rgba(11,37,69,0.2) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #2ECC8A 0%, #56E6A8 100%) !important;
        color: #0B2545 !important;
        box-shadow: 0 6px 20px rgba(46,204,138,0.35) !important;
    }

    /* ── Verdict cards ── */
    .verdict-high {
        background: linear-gradient(135deg, #FFF1F1 0%, #FEE2E2 100%);
        border: 1.5px solid #DC2626;
        border-left: 5px solid #DC2626;
        border-radius: 12px;
        padding: 22px 26px;
        margin-bottom: 16px;
    }
    .verdict-low {
        background: linear-gradient(135deg, #F0FDF8 0%, #DCFCEE 100%);
        border: 1.5px solid #2ECC8A;
        border-left: 5px solid #2ECC8A;
        border-radius: 12px;
        padding: 22px 26px;
        margin-bottom: 16px;
    }
    .verdict-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .verdict-prob {
        font-size: 2.2rem;
        font-weight: 700;
        line-height: 1;
        margin: 8px 0 4px 0;
    }
    .verdict-sublabel {
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        opacity: 0.65;
    }

    /* ── Risk bar ── */
    .risk-bar-wrap {
        background: #E2E8F0;
        border-radius: 6px;
        height: 8px;
        margin: 12px 0 5px 0;
        overflow: hidden;
    }
    .risk-bar-high {
        height: 100%;
        border-radius: 6px;
        background: linear-gradient(90deg, #F59E0B, #DC2626);
    }
    .risk-bar-low {
        height: 100%;
        border-radius: 6px;
        background: linear-gradient(90deg, #2ECC8A, #16A34A);
    }

    /* ── Clinical factor chips ── */
    .factor-chip {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .factor-name {
        font-size: 0.78rem;
        font-weight: 600;
        color: #334155;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .factor-value {
        font-size: 0.82rem;
        font-weight: 700;
        color: #0B2545;
    }
    .factor-badge-red {
        background: #FEE2E2; color: #DC2626;
        padding: 2px 8px; border-radius: 10px;
        font-size: 0.68rem; font-weight: 700;
    }
    .factor-badge-yellow {
        background: #FEF9C3; color: #CA8A04;
        padding: 2px 8px; border-radius: 10px;
        font-size: 0.68rem; font-weight: 700;
    }
    .factor-badge-green {
        background: #DCFCE7; color: #16A34A;
        padding: 2px 8px; border-radius: 10px;
        font-size: 0.68rem; font-weight: 700;
    }

    /* ── Action cards ── */
    .action-card {
        background: #FFFFFF;
        border-radius: 10px;
        padding: 16px 20px;
        border: 1px solid #E2E8F0;
        margin-bottom: 8px;
        display: flex;
        align-items: flex-start;
        gap: 12px;
    }
    .action-icon { font-size: 1.1rem; margin-top: 1px; }
    .action-text strong {
        font-size: 0.83rem; font-weight: 700;
        color: #0B2545; display: block; margin-bottom: 2px;
    }
    .action-text span { font-size: 0.76rem; color: #64748B; }

    /* ── Gold divider → clinical green ── */
    .green-divider {
        height: 1px;
        background: linear-gradient(90deg, #2ECC8A44, #2ECC8A, #2ECC8A44);
        margin: 24px 0;
        border: none;
    }

    /* ── Disclaimer ── */
    .disclaimer {
        background: #FFF7ED;
        border: 1px solid #FED7AA;
        border-left: 4px solid #F97316;
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 0.75rem;
        color: #92400E;
        margin-top: 20px;
        line-height: 1.6;
    }

    /* ── Metric overrides ── */
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 14px 18px;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.7rem !important;
        font-weight: 700 !important;
        letter-spacing: 1.2px !important;
        text-transform: uppercase !important;
        color: #64748B !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        color: #0B2545 !important;
    }

    [data-testid="stExpander"] {
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        background: #FFFFFF !important;
    }
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
    <div style="padding: 8px 0 22px 0;">
        <div style="font-family:'Playfair Display',serif; font-size:1.4rem; font-weight:700; color:#2ECC8A;">
            GlucoseIQ
        </div>
        <div style="font-size:0.68rem; letter-spacing:2px; text-transform:uppercase; color:#64748B; margin-top:2px;">
            Clinical Risk Intelligence
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🏥 Platform")
    st.markdown("""
    <div style="font-size:0.8rem; color:#94A3B8; line-height:1.8;">
    GlucoseIQ applies dual ensemble ML models — 
    <strong style="color:#2ECC8A;">Random Forest</strong> and 
    <strong style="color:#2ECC8A;">XGBoost</strong> — to assess 
    Type 2 diabetes onset risk from 8 clinical biomarkers.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📊 Model Performance")
    st.markdown("""
    <div style="font-size:0.78rem; color:#94A3B8; line-height:2.2;">
    <b style="color:#CBD5E0;">Random Forest AUC</b><br/>0.948<br/><br/>
    <b style="color:#CBD5E0;">XGBoost AUC</b><br/>0.947<br/><br/>
    <b style="color:#CBD5E0;">Dataset</b><br/>Pima Indians Diabetes (NIDDK)<br/><br/>
    <b style="color:#CBD5E0;">Features</b><br/>8 clinical biomarkers + 3 engineered<br/><br/>
    <b style="color:#CBD5E0;">Population</b><br/>768 female patients · Ages 21–81
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🔗 Resources")
    st.markdown("""
    <div style="font-size:0.8rem; line-height:2.4;">
    <a href="https://github.com/yemifatodu" target="_blank">⟶ GitHub</a><br/>
    <a href="https://yemifatodu.online" target="_blank">⟶ Portfolio</a><br/>
    <a href="https://linkedin.com/in/yemifatodu" target="_blank">⟶ LinkedIn</a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.7rem; color:#475569; line-height:1.7;">
    Built by <strong style="color:#2ECC8A;">Yemi Fatodu</strong><br/>
    Data Scientist · BI Specialist<br/>Full-Stack Product Builder<br/><br/>
    <em style="color:#64748B;">Open to freelance & contract engagements</em>
    </div>
    """, unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="top-bar">
    <div>
        <div class="top-bar-title">🩺 Glucose<span>IQ</span></div>
        <div class="top-bar-subtitle">Clinical Diabetes Risk Assessment Platform</div>
    </div>
    <div class="top-bar-badge">● Dual-Model Active</div>
</div>
""", unsafe_allow_html=True)

if not model_ok:
    st.error(f"❌ Model load error: {model_error}")
    st.stop()

# ── KPI strip ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="kpi-row">
    <div class="kpi-chip">
        <div class="kpi-chip-accent"></div>
        <div class="kpi-chip-value">0.948</div>
        <div class="kpi-chip-label">RF AUC Score</div>
    </div>
    <div class="kpi-chip">
        <div class="kpi-chip-accent"></div>
        <div class="kpi-chip-value">0.947</div>
        <div class="kpi-chip-label">XGB AUC Score</div>
    </div>
    <div class="kpi-chip">
        <div class="kpi-chip-accent"></div>
        <div class="kpi-chip-value">768</div>
        <div class="kpi-chip-label">Patient Records</div>
    </div>
    <div class="kpi-chip">
        <div class="kpi-chip-accent"></div>
        <div class="kpi-chip-value">11</div>
        <div class="kpi-chip-label">Feature Signals</div>
    </div>
    <div class="kpi-chip">
        <div class="kpi-chip-accent"></div>
        <div class="kpi-chip-value">2</div>
        <div class="kpi-chip-label">Active Models</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Model selector ────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Model Selection</div>', unsafe_allow_html=True)
model_choice = st.selectbox(
    "Active Predictive Model",
    ["Random Forest (AUC: 0.948)", "XGBoost (AUC: 0.947)"],
    label_visibility="collapsed"
)

st.markdown('<hr class="green-divider"/>', unsafe_allow_html=True)

# ── Input form ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Patient Clinical Biomarkers</div>', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="card"><div class="card-title">Clinical Input Parameters</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        pregnancies = st.number_input("Pregnancies", min_value=0, max_value=20, value=1)
        glucose     = st.number_input("Glucose (mg/dL)", min_value=0, max_value=300, value=110)

    with col2:
        blood_pressure  = st.number_input("Blood Pressure (mmHg)", min_value=0, max_value=200, value=70)
        skin_thickness  = st.number_input("Skin Thickness (mm)", min_value=0, max_value=100, value=20)

    with col3:
        insulin = st.number_input("Insulin (IU/mL)", min_value=0, max_value=900, value=80)
        bmi     = st.number_input("BMI", min_value=0.0, max_value=70.0, value=25.0)

    with col4:
        dpf = st.number_input("Diabetes Pedigree Function", min_value=0.0, max_value=3.0, value=0.3, step=0.01)
        age = st.number_input("Age (years)", min_value=21, max_value=100, value=30)

    st.markdown('</div>', unsafe_allow_html=True)

# ── Predict button ────────────────────────────────────────────────────────────
predict_clicked = st.button("⟶  RUN CLINICAL RISK ASSESSMENT", type="primary", use_container_width=True)

# ── Results ───────────────────────────────────────────────────────────────────
if predict_clicked:
    # Feature engineering
    bmi_category  = 0 if bmi < 18.5 else 1 if bmi < 24.9 else 2 if bmi < 29.9 else 3
    glucose_risk  = 0 if glucose < 100 else 1 if glucose < 126 else 2
    age_group     = 0 if age <= 30 else 1 if age <= 45 else 2

    input_data = pd.DataFrame([[
        pregnancies, glucose, blood_pressure, skin_thickness,
        insulin, bmi, dpf, age,
        bmi_category, glucose_risk, age_group
    ]], columns=features)

    input_scaled     = scaler.transform(input_data)
    selected_model   = rf_model if "Random Forest" in model_choice else xgb_model
    prediction       = selected_model.predict(input_scaled)[0]
    probability      = selected_model.predict_proba(input_scaled)[0]
    diabetes_prob    = probability[1] * 100
    no_diabetes_prob = probability[0] * 100
    confidence       = max(probability) * 100

    st.markdown('<hr class="green-divider"/>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Clinical Risk Assessment Output</div>', unsafe_allow_html=True)

    res_col1, res_col2 = st.columns([1.3, 1])

    with res_col1:
        bar_pct = int(diabetes_prob)
        if prediction == 1:
            st.markdown(f"""
            <div class="verdict-high">
                <div class="verdict-sublabel">⚠ Diabetes Risk Verdict</div>
                <div class="verdict-title" style="color:#DC2626;">HIGH RISK — DIABETES LIKELY</div>
                <div class="verdict-prob" style="color:#DC2626;">{diabetes_prob:.1f}%</div>
                <div class="verdict-sublabel">Predicted Diabetes Probability</div>
                <div class="risk-bar-wrap">
                    <div class="risk-bar-high" style="width:{bar_pct}%;"></div>
                </div>
                <div style="font-size:0.7rem;color:#64748B;">
                    Clinical threshold: 50% · Model confidence: {confidence:.1f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="verdict-low">
                <div class="verdict-sublabel">✔ Diabetes Risk Verdict</div>
                <div class="verdict-title" style="color:#16A34A;">LOW RISK — DIABETES UNLIKELY</div>
                <div class="verdict-prob" style="color:#16A34A;">{no_diabetes_prob:.1f}%</div>
                <div class="verdict-sublabel">Predicted No-Diabetes Probability</div>
                <div class="risk-bar-wrap">
                    <div class="risk-bar-low" style="width:{int(no_diabetes_prob)}%;"></div>
                </div>
                <div style="font-size:0.7rem;color:#64748B;">
                    Clinical threshold: 50% · Model confidence: {confidence:.1f}%
                </div>
            </div>
            """, unsafe_allow_html=True)

    with res_col2:
        st.metric("Diabetes Probability",    f"{diabetes_prob:.1f}%")
        st.metric("No-Diabetes Probability", f"{no_diabetes_prob:.1f}%")
        st.metric("Model Confidence",        f"{confidence:.1f}%")
        st.metric("Active Model",            "RF" if "Random Forest" in model_choice else "XGB")

    # ── Gauge ──
    st.markdown('<hr class="green-divider"/>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Risk Probability Gauge</div>', unsafe_allow_html=True)

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=diabetes_prob,
        number={'suffix': '%', 'font': {'size': 32, 'color': '#0B2545', 'family': 'Inter'}},
        title={'text': "Diabetes Risk Score", 'font': {'size': 13, 'color': '#64748B', 'family': 'Inter'}},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': '#94A3B8', 'tickfont': {'size': 10}},
            'bar': {'color': "#DC2626" if prediction == 1 else "#2ECC8A", 'thickness': 0.25},
            'bgcolor': '#F4F7F9',
            'bordercolor': '#E2E8F0',
            'steps': [
                {'range': [0,  30],  'color': '#DCFCE7'},
                {'range': [30, 60],  'color': '#FEF9C3'},
                {'range': [60, 100], 'color': '#FEE2E2'}
            ],
            'threshold': {
                'line': {'color': '#0B2545', 'width': 2},
                'thickness': 0.75,
                'value': 50
            }
        }
    ))
    fig.update_layout(
        height=240,
        margin=dict(t=50, b=10, l=20, r=20),
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        font=dict(family='Inter')
    )
    gauge_col, _ = st.columns([1.5, 1])
    with gauge_col:
        st.plotly_chart(fig, use_container_width=True)

    # ── Clinical factor analysis ──
    st.markdown('<hr class="green-divider"/>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Biomarker Analysis</div>', unsafe_allow_html=True)

    def badge(status):
        if status == "red":    return "factor-badge-red"
        if status == "yellow": return "factor-badge-yellow"
        return "factor-badge-green"

    def glucose_status(g):
        if g >= 126: return ("Diabetes Range", "red")
        if g >= 100: return ("Prediabetes", "yellow")
        return ("Normal", "green")

    def bmi_status(b):
        if b >= 30:   return ("Obese", "red")
        if b >= 25:   return ("Overweight", "yellow")
        if b < 18.5:  return ("Underweight", "yellow")
        return ("Normal", "green")

    def bp_status(bp):
        if bp >= 140: return ("Hypertensive", "red")
        if bp >= 120: return ("Elevated", "yellow")
        return ("Normal", "green")

    def insulin_status(i):
        if i > 200:  return ("High", "red")
        if i > 100:  return ("Elevated", "yellow")
        return ("Normal", "green")

    def age_status(a):
        if a > 45:  return ("Senior Risk", "red")
        if a > 30:  return ("Moderate Risk", "yellow")
        return ("Low Risk", "green")

    factors = [
        ("Glucose", f"{glucose} mg/dL", *glucose_status(glucose)),
        ("BMI", f"{bmi:.1f}", *bmi_status(bmi)),
        ("Blood Pressure", f"{blood_pressure} mmHg", *bp_status(blood_pressure)),
        ("Insulin", f"{insulin} IU/mL", *insulin_status(insulin)),
        ("Age", f"{age} years", *age_status(age)),
        ("Pregnancies", str(pregnancies), ("Elevated" if pregnancies > 5 else "Normal"),
         "yellow" if pregnancies > 5 else "green"),
    ]

    fc1, fc2 = st.columns(2)
    for i, (name, value, label, status) in enumerate(factors):
        col = fc1 if i % 2 == 0 else fc2
        with col:
            st.markdown(f"""
            <div class="factor-chip">
                <span class="factor-name">{name}</span>
                <span>
                    <span class="factor-value">{value}</span>&nbsp;
                    <span class="{badge(status)}">{label}</span>
                </span>
            </div>
            """, unsafe_allow_html=True)

    # ── Clinical action plan ──
    st.markdown('<hr class="green-divider"/>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Clinical Recommendation Protocol</div>', unsafe_allow_html=True)

    if prediction == 1:
        actions = [
            ("🔬", "Confirmatory Diagnostic Testing",
             "Order fasting plasma glucose (FPG) and HbA1c tests immediately to confirm diagnosis."),
            ("👨‍⚕️", "Endocrinology Referral",
             "Refer patient to an endocrinologist or diabetologist for specialist evaluation."),
            ("🥗", "Therapeutic Lifestyle Intervention",
             "Initiate structured diet counselling and a supervised physical activity programme."),
            ("💊", "Pharmacological Assessment",
             "Evaluate candidacy for metformin or other glycaemic control agents per clinical guidelines."),
            ("📅", "Intensive Monitoring Protocol",
             "Schedule 3-month follow-up with repeat HbA1c, lipid panel, and renal function tests."),
        ]
    else:
        actions = [
            ("✅", "Routine Preventive Monitoring",
             "Continue annual screening with fasting glucose and HbA1c as standard of care."),
            ("🥗", "Lifestyle Optimisation",
             "Reinforce Mediterranean diet and 150 min/week moderate-intensity physical activity."),
            ("📊", "Risk Factor Surveillance",
             "Monitor BMI, blood pressure, and lipid profile at every clinical encounter."),
            ("📚", "Patient Education",
             "Provide diabetes prevention programme materials and self-monitoring guidance."),
            ("📅", "12-Month Review",
             "Schedule annual wellness review with updated risk stratification assessment."),
        ]

    for icon, title, desc in actions:
        st.markdown(f"""
        <div class="action-card">
            <div class="action-icon">{icon}</div>
            <div class="action-text">
                <strong>{title}</strong>
                <span>{desc}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Input summary ──
    with st.expander("📋 View Full Patient Input Summary"):
        st.dataframe(input_data[['Pregnancies','Glucose','BloodPressure','SkinThickness',
                                  'Insulin','BMI','DiabetesPedigreeFunction','Age']
                                  if all(c in input_data.columns for c in ['Pregnancies','Glucose'])
                                  else input_data].T.rename(columns={0: 'Value'}),
                     use_container_width=True)

    # ── Disclaimer ──
    st.markdown("""
    <div class="disclaimer">
        ⚠️ <strong>Clinical Disclaimer:</strong> GlucoseIQ is an AI-assisted decision support tool 
        intended for educational and portfolio demonstration purposes only. It is <strong>not a substitute 
        for professional medical advice, diagnosis, or treatment.</strong> All clinical decisions must be 
        made by qualified healthcare professionals in accordance with applicable guidelines and standards of care.
        <br/><br/>
        Dataset: Pima Indians Diabetes Database (National Institute of Diabetes and Digestive and Kidney Diseases).
        Built by <strong>Yemi Fatodu</strong> — Data Scientist & Full-Stack Product Builder.
    </div>
    """, unsafe_allow_html=True)