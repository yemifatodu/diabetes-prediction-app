import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.graph_objects as go

st.set_page_config(
    page_title="Diabetes Risk Predictor",
    page_icon="🩺",
    layout="wide"
)

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

# ── HEADER ────────────────────────────────────────────────────────────────────
h1, h2 = st.columns([2, 1])
with h1:
    st.title("🩺 Diabetes Risk Predictor")
    st.write("Enter patient clinical values to predict diabetes risk.")
with h2:
    st.write("")
    model_choice = st.selectbox(
        "⚙️ Active Model",
        ["Random Forest (AUC: 0.948)", "XGBoost (AUC: 0.947)"]
    )

st.divider()

# ── TWO COLUMN LAYOUT ─────────────────────────────────────────────────────────
left, right = st.columns([4, 6])

# ── LEFT — INPUTS ─────────────────────────────────────────────────────────────
with left:
    st.subheader("📋 Patient Clinical Values")
    st.divider()

    pregnancies = st.number_input("Pregnancies",
        min_value=0, max_value=20, value=1)
    glucose = st.number_input("Glucose (mg/dL)",
        min_value=0, max_value=300, value=110)
    blood_pressure = st.number_input("Blood Pressure (mmHg)",
        min_value=0, max_value=200, value=70)
    skin_thickness = st.number_input("Skin Thickness (mm)",
        min_value=0, max_value=100, value=20)
    insulin = st.number_input("Insulin (IU/mL)",
        min_value=0, max_value=900, value=80)
    bmi = st.number_input("BMI",
        min_value=0.0, max_value=70.0, value=25.0)
    dpf = st.number_input("Diabetes Pedigree Function",
        min_value=0.0, max_value=3.0, value=0.3, step=0.01)
    age = st.number_input("Age",
        min_value=21, max_value=100, value=30)

# ── RIGHT — RESULTS ───────────────────────────────────────────────────────────
with right:
    st.subheader("📊 Prediction Results")
    st.divider()

    predict_btn = st.button("🔍 Predict Diabetes Risk",
                             type="primary",
                             use_container_width=True)

    st.write("")

    if predict_btn:
        # Feature engineering
        bmi_category = 0 if bmi < 18.5 else 1 if bmi < 24.9 else 2 if bmi < 29.9 else 3
        glucose_risk = 0 if glucose < 100 else 1 if glucose < 126 else 2
        age_group = 0 if age <= 30 else 1 if age <= 45 else 2

        input_data = pd.DataFrame([[
            pregnancies, glucose, blood_pressure, skin_thickness,
            insulin, bmi, dpf, age,
            bmi_category, glucose_risk, age_group
        ]], columns=features)

        input_scaled = scaler.transform(input_data)
        selected_model = rf_model if "Random Forest" in model_choice else xgb_model
        prediction = selected_model.predict(input_scaled)[0]
        probability = selected_model.predict_proba(input_scaled)[0]
        no_diabetes_prob = probability[0] * 100
        diabetes_prob = probability[1] * 100

        # Row 1 — Result
        if prediction == 1:
            st.error(f"⚠️ HIGH RISK — Diabetes Likely")
            st.metric("Diabetes Probability", f"{diabetes_prob:.1f}%")
            st.metric("No Diabetes Probability", f"{no_diabetes_prob:.1f}%")
            st.warning("⚕️ Refer this patient for clinical testing.")
        else:
            st.success("✅ LOW RISK — Diabetes Unlikely")
            st.metric("No Diabetes Probability", f"{no_diabetes_prob:.1f}%")
            st.metric("Diabetes Probability", f"{diabetes_prob:.1f}%")
            st.info("⚕️ Continue routine monitoring.")

        st.divider()

        # Row 2 — Gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=diabetes_prob,
            title={'text': "Diabetes Risk %"},
            number={'suffix': '%'},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#C0392B" if prediction == 1 else "#1E8449"},
                'steps': [
                    {'range': [0, 30], 'color': "#D5F5E3"},
                    {'range': [30, 60], 'color': "#FDEBD0"},
                    {'range': [60, 100], 'color': "#FADBD8"}
                ],
                'threshold': {
                    'line': {'color': "#C0392B", 'width': 3},
                    'thickness': 0.75,
                    'value': 50
                }
            }
        ))
        fig.update_layout(height=220,
                          margin=dict(t=40, b=0, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # Row 3 — Clinical factors
        st.write("**🔬 Clinical Risk Factors**")
        m1, m2 = st.columns(2)
        with m1:
            g_status = "🔴 Diabetes Range" if glucose >= 126 else \
                       "🟡 Prediabetes" if glucose >= 100 else "🟢 Normal"
            st.metric("Glucose", g_status, f"{glucose} mg/dL")
            b_status = "🔴 Obese" if bmi >= 30 else \
                       "🟡 Overweight" if bmi >= 25 else "🟢 Normal"
            st.metric("BMI", b_status, f"{bmi}")
        with m2:
            a_status = "🔴 Senior" if age > 45 else \
                       "🟡 Middle" if age > 30 else "🟢 Young"
            st.metric("Age Group", a_status, f"{age} yrs")
            i_status = "🔴 High" if insulin > 200 else \
                       "🟡 Elevated" if insulin > 100 else "🟢 Normal"
            st.metric("Insulin", i_status, f"{insulin} IU/mL")

    else:
        st.info("👈 Enter patient values on the left and click Predict")

st.divider()
st.caption("⚠️ Disclaimer: For educational and portfolio purposes only. "
           "Not a substitute for professional medical advice. | "
           "Built by Yemi Fatodu | Pima Indians Diabetes Dataset (NIDDK)")