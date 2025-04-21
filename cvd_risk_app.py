
import streamlit as st
import math
import pandas as pd
import matplotlib.pyplot as plt

# ----- Page Configuration & Branding -----
st.set_page_config(layout="wide", page_title="SMART CVD Risk Reduction")
col1, col2, col3 = st.columns([1, 6, 1])
with col3:
    try:
        st.image("logo.png", width=600)
    except Exception:
        st.warning("⚠️ Logo could not be loaded; please ensure 'logo.png' is in your app directory.")

# ----- Sidebar: Core Risk Factors -----
with st.sidebar:
    st.header("CV Risk Factors")
    age = st.slider("Age", 30, 90, 60)
    sex = st.radio("Sex", ["Male", "Female"])
    weight = st.number_input("Weight (kg)", 40.0, 200.0, 75.0)
    height = st.number_input("Height (cm)", 140.0, 210.0, 170.0)
    bmi = weight / ((height / 100)**2)
    st.write(f"**BMI:** {bmi:.1f} kg/m²")
    smoker = st.checkbox("Current smoker")
    diabetes = st.checkbox("Diabetes")
    egfr = st.slider("eGFR", 15, 120, 90)
    st.markdown("**Vascular Disease (select all that apply)**")
    vasc1 = st.checkbox("Coronary artery disease")
    vasc2 = st.checkbox("Cerebrovascular disease")
    vasc3 = st.checkbox("Peripheral artery disease")
    vasc_count = sum([vasc1, vasc2, vasc3])

# ----- Tabs Layout -----
tab1, tab2, tab3 = st.tabs(["Lab Results", "Therapies", "Results"])

with tab1:
    st.subheader("Lab Results")
    total_chol = st.number_input("Total Cholesterol (mmol/L)", 2.0, 10.0, 5.2)
    hdl = st.number_input("HDL-C (mmol/L)", 0.5, 3.0, 1.3)
    ldl = st.number_input("LDL-C (mmol/L)", 0.5, 6.0, 3.0)
    crp = st.number_input("hs-CRP (mg/L) — Baseline (not during acute illness/MI)", 0.1, 20.0, 2.5)
    hba1c = st.number_input("Latest HbA1c (%)", 4.5, 15.0, 7.0)
    tg = st.number_input("Fasting Triglycerides (mmol/L)", 0.5, 5.0, 1.5)

with tab2:
    st.subheader("Current Lipid-lowering Therapy")
    statin = st.selectbox("Statin (pre-admission)", ["None", "Atorvastatin 80 mg", "Rosuvastatin 20 mg"])
    ezetimibe = st.checkbox("Ezetimibe")
    bempedoic = st.checkbox("Bempedoic acid")

    st.subheader("Advised Lipid-lowering Therapy (if appropriate)")
    if ldl > 1.8:
        pcsk9 = st.checkbox("PCSK9 inhibitor")
        inclisiran = st.checkbox("Inclisiran (siRNA)")
    else:
        st.info("LDL-C < 1.8 mmol/L — PCSK9i and Inclisiran not shown.")

    st.subheader("Lifestyle Changes")
    smoke_cease = st.checkbox("Smoking cessation", disabled=not smoker)
    semaglutide = st.checkbox("GLP-1 RA (Semaglutide)", disabled=(bmi < 30))
    mediterranean = st.checkbox("Mediterranean diet")
    activity = st.checkbox("Physical activity")
    alcohol = st.checkbox("Alcohol moderation (>14 units/week)")
    stress = st.checkbox("Stress reduction")

    st.subheader("Other Interventions")
    antiplatelet = st.checkbox("Single antiplatelet (ASA or Clopidogrel)")
    bp_control = st.checkbox("BP control (target <130 mmHg)")
    sglt2i = st.checkbox("SGLT2 inhibitor")
    if tg > 1.7:
        icosapent = st.checkbox("Icosapent ethyl")
    else:
        st.info("Icosapent ethyl only available if TG > 1.7 mmol/L")

with tab3:
    st.subheader("Results")
    st.write("This section will calculate SMART score and estimated ARR/RRR based on above inputs.")
    st.markdown("*(Full calculation logic would be displayed here as per the full build.)*")

# ----- Footer -----
st.markdown("---")
st.markdown("Created by PRIME team (Prevention Recurrent Ischaemic Myocardial Events)")
st.markdown("King's College Hospital, London")
st.markdown("Created by Samuel Panday — 21/04/2025")
st.markdown("This tool is provided for informational purposes and designed to support discussions with your healthcare provider—it’s not a substitute for professional medical advice.")
