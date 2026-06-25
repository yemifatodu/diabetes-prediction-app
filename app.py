# ── Diabetes Prediction App ───────────────────────────────────────────────────
import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.graph_objects as go

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Diabetes Risk Predictor",
    page_icon="🩺",
    layout="wide"
)

# ── Load Models ───────────────────────────────────────────────────────────────
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

rf_model, xgb_model, scaler, features = load_models()

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🩺 Diabetes Risk Predictor")
st.markdown("### Clinical Pre-Screening Tool — MeriSkill Data Science Project")
st.markdown("Enter patient clinical values below to predict diabetes risk using "
            "two trained machine learning models.")
st.divider()

# ── Model Selection ───────────────────────────────────────────────────────────
st.subheader("⚙️ Select Model")
model_choice = st.radio(
    "Choose prediction model:",
    ["Random Forest (AUC: 0.948)", "XGBoost (AUC: 0.947)"],
    horizontal=True
)

st.divider()

# ── Input Form ────────────────────────────────────────────────────────────────
st.subheader("📋 Patient Clinical Values")

col1, col2, col3 = st.columns(3)

with col1:
    pregnancies = st.number_input("Pregnancies", 
                                   min_value=0, max_value=20, value=1,
                                   help="Number of times pregnant")
    glucose = st.number_input("Glucose (mg/dL)", 
                               min_value=0, max_value=300, value=110,
                               help="Plasma glucose concentration")
    blood_pressure = st.number_input("Blood Pressure (mmHg)", 
                                      min_value=0, max_value=200, value=70,
                                      help="Diastolic blood pressure")

with col2:
    skin_thickness = st.number_input("Skin Thickness (mm)", 
                                      min_value=0, max_value=100, value=20,
                                      help="Triceps skin fold thickness")
    insulin = st.number_input("Insulin (IU/mL)", 
                               min_value=0, max_value=900, value=80,
                               help="2-Hour serum insulin")
    bmi = st.number_input("BMI", 
                           min_value=0.0, max_value=70.0, value=25.0,
                           help="Body Mass Index")

with col3:
    dpf = st.number_input("Diabetes Pedigree Function", 
                           min_value=0.0, max_value=3.0, value=0.3,
                           step=0.01,
                           help="Diabetes pedigree function (family history)")
    age = st.number_input("Age", 
                           min_value=21, max_value=100, value=30,
                           help="Age in years")

st.divider()

# ── Predict Button ────────────────────────────────────────────────────────────
if st.button("🔍 Predict Diabetes Risk", type="primary", use_container_width=True):

    # Engineer features to match training
    bmi_category = 0 if bmi < 18.5 else 1 if bmi < 24.9 else 2 if bmi < 29.9 else 3
    glucose_risk = 0 if glucose < 100 else 1 if glucose < 126 else 2
    age_group = 0 if age <= 30 else 1 if age <= 45 else 2

    # Build input dataframe
    input_data = pd.DataFrame([[
        pregnancies, glucose, blood_pressure, skin_thickness,
        insulin, bmi, dpf, age,
        bmi_category, glucose_risk, age_group
    ]], columns=features)

    # Scale
    input_scaled = scaler.transform(input_data)

    # Select model
    selected_model = rf_model if "Random Forest" in model_choice else xgb_model
    model_name = "Random Forest" if "Random Forest" in model_choice else "XGBoost"

    # Predict
    prediction = selected_model.predict(input_scaled)[0]
    probability = selected_model.predict_proba(input_scaled)[0]

    no_diabetes_prob = probability[0] * 100
    diabetes_prob = probability[1] * 100

    st.divider()
    st.subheader(f"📊 Prediction Results — {model_name}")

    # ── Result Banner ─────────────────────────────────────────────────────────
    col_result, col_gauge = st.columns([1, 1])

    with col_result:
        if prediction == 1:
            st.error(f"⚠️ HIGH RISK — Diabetes Likely")
            st.markdown(f"**Diabetes Probability: {diabetes_prob:.1f}%**")
            st.markdown(f"No Diabetes Probability: {no_diabetes_prob:.1f}%")
            st.warning("⚕️ This patient should be referred for clinical testing.")
        else:
            st.success(f"✅ LOW RISK — Diabetes Unlikely")
            st.markdown(f"**No Diabetes Probability: {no_diabetes_prob:.1f}%**")
            st.markdown(f"Diabetes Probability: {diabetes_prob:.1f}%")
            st.info("⚕️ Continue routine monitoring.")

    # ── Gauge Chart ───────────────────────────────────────────────────────────
    with col_gauge:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=diabetes_prob,
            title={'text': "Diabetes Risk %"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#e74c3c" if prediction == 1 else "#2ecc71"},
                'steps': [
                    {'range': [0, 30], 'color': "#d5f5e3"},
                    {'range': [30, 60], 'color': "#fdebd0"},
                    {'range': [60, 100], 'color': "#fadbd8"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 50
                }
            }
        ))
        fig.update_layout(height=250, margin=dict(t=40, b=0, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)

    # ── Clinical Risk Factors ─────────────────────────────────────────────────
    st.divider()
    st.subheader("🔬 Clinical Risk Factor Analysis")

    risk_col1, risk_col2, risk_col3 = st.columns(3)

    with risk_col1:
        glucose_status = "🔴 Diabetes Range" if glucose >= 126 else \
                         "🟡 Prediabetes" if glucose >= 100 else "🟢 Normal"
        st.metric("Glucose Status", glucose_status, f"{glucose} mg/dL")

    with risk_col2:
        bmi_status = "🔴 Obese" if bmi >= 30 else \
                     "🟡 Overweight" if bmi >= 25 else "🟢 Normal"
        st.metric("BMI Status", bmi_status, f"{bmi}")

    with risk_col3:
        age_status = "🔴 Senior" if age > 45 else \
                     "🟡 Middle" if age > 30 else "🟢 Young"
        st.metric("Age Group", age_status, f"{age} years")

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown("""
**⚠️ Disclaimer:** This tool is for educational and portfolio demonstration purposes only. 
It is not a substitute for professional medical advice, diagnosis, or treatment.

*Built by Yemi Fatodu   
Dataset: Pima Indians Diabetes Dataset (NIDDK)*
""")