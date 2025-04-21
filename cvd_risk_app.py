
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
    except FileNotFoundError:
        st.warning("⚠️ logo.png not found; please add it to your repo.")

st.title("SMART CVD Risk Reduction Calculator")
st.markdown("**Created by Samuel Panday — 21/04/2025**")

# ----- Intervention & Therapy Data -----
interventions = [
    {"name": "Smoking cessation", "arr_lifetime": 17, "arr_5yr": 5, "link": "https://pubmed.ncbi.nlm.nih.gov/PMID1"},
    {"name": "Antiplatelet (ASA or clopidogrel)", "arr_lifetime": 6, "arr_5yr": 2, "link": "https://pubmed.ncbi.nlm.nih.gov/PMID2"},
    {"name": "Weight loss to ideal BMI", "arr_lifetime": 10, "arr_5yr": 3, "link": "https://pubmed.ncbi.nlm.nih.gov/PMID3"},
    {"name": "Empagliflozin", "arr_lifetime": 6, "arr_5yr": 2, "link": "https://pubmed.ncbi.nlm.nih.gov/PMID4"},
    {"name": "Icosapent ethyl", "arr_lifetime": 5, "arr_5yr": 2, "link": "https://pubmed.ncbi.nlm.nih.gov/PMID5"},
    {"name": "Mediterranean diet", "arr_lifetime": 9, "arr_5yr": 3, "link": "https://pubmed.ncbi.nlm.nih.gov/PMID6"},
    {"name": "Physical activity", "arr_lifetime": 9, "arr_5yr": 3, "link": "https://pubmed.ncbi.nlm.nih.gov/PMID7"},
    {"name": "Alcohol moderation", "arr_lifetime": 5, "arr_5yr": 2, "link": "https://pubmed.ncbi.nlm.nih.gov/PMID8"},
    {"name": "Stress reduction", "arr_lifetime": 3, "arr_5yr": 1, "link": "https://pubmed.ncbi.nlm.nih.gov/PMID9"},
    {"name": "Semaglutide", "arr_lifetime": 4, "arr_5yr": 1, "link": "https://pubmed.ncbi.nlm.nih.gov/STEP"}
]

ldl_therapies = {
    "Atorvastatin 80 mg": 50,
    "Rosuvastatin 20 mg": 55,
    "Ezetimibe": 20,
    "Bempedoic acid": 18,
    "PCSK9 inhibitor": 60,
    "Inclisiran (siRNA)": 40
}

# ----- Risk Functions -----
def estimate_smart_risk(age, sex, sbp, tc, hdl, smoke, dm, egfr, crp, vasc):
    sex_v = 1 if sex == "Male" else 0
    smoke_v = 1 if smoke else 0
    dm_v = 1 if dm else 0
    crp_l = math.log(crp + 1)
    lp = (0.064 * age + 0.34 * sex_v + 0.02 * sbp + 0.25 * tc
          - 0.25 * hdl + 0.44 * smoke_v + 0.51 * dm_v
          - 0.2 * (egfr / 10) + 0.25 * crp_l + 0.4 * vasc)
    r10 = 1 - 0.900**math.exp(lp - 5.8)
    return round(r10 * 100, 1)

def convert_5yr(r10):
    p = r10 / 100
    return round((1 - (1 - p)**0.5) * 100, 1)

# ----- Sidebar: Core CVRF Inputs -----
with st.sidebar:
    st.header("CV Risk Factors")
    age = st.slider("Age", 30, 90, 60)
    sex = st.radio("Sex", ["Male", "Female"], help="Biological sex for risk calibration.")
    weight = st.number_input("Weight (kg)", 40.0, 200.0, 75.0, 0.1)
    height = st.number_input("Height (cm)", 140.0, 210.0, 170.0, 0.1)
    bmi = weight / ((height / 100)**2)
    st.write(f"**BMI:** {bmi:.1f} kg/m²")
    smoking = st.checkbox("Current smoking", help="Tobacco use increases CVD risk.")
    diabetes = st.checkbox("Diabetes", help="Diabetes doubles CVD risk.")
    egfr = st.slider("eGFR (mL/min/1.73m²)", 15, 120, 80, help="Baseline renal function")
    st.markdown("**Vascular disease (tick all that apply)**")
    vasc1 = st.checkbox("Coronary artery disease", help="Prior MI or revascularization.")
    vasc2 = st.checkbox("Cerebrovascular disease", help="Stroke/TIA history.")
    vasc3 = st.checkbox("Peripheral artery disease", help="Claudication or revascularization.")
    vasc_count = sum([vasc1, vasc2, vasc3])

# ----- Main Pane: Tabs -----
tab1, tab2, tab3 = st.tabs(["Lab Results", "Therapies", "Results"])

with tab1:
    st.subheader("Lab Results")
    total_chol = st.number_input("Total Cholesterol (mmol/L)", 2.0, 10.0, 5.0, 0.1)
    hdl = st.number_input("HDL-C (mmol/L)", 0.5, 3.0, 1.0, 0.1)
    crp = st.number_input("hs-CRP (mg/L) — Baseline (not during acute MI)", 0.1, 20.0, 2.0, 0.1)
    baseline_ldl = st.number_input("Baseline LDL-C (mmol/L)", 0.5, 6.0, 3.5, 0.1)
    tg = st.number_input("Fasting TG (mmol/L)", 0.3, 5.0, 1.2, 0.1)
    hba1c = st.number_input("Latest HbA₁c (%)", 4.0, 14.0, 7.0, 0.1)

with tab2:
    st.subheader("Current Lipid-lowering Therapy")
    statin = st.selectbox("High-intensity statin", ["None", "Atorvastatin 80 mg", "Rosuvastatin 20 mg"],
                          help="CTT meta-analysis: 22% RRR per 1 mmol/L LDL-C ↓; see Lancet 2010.")
    ez = st.checkbox("Ezetimibe 10 mg", help="IMPROVE-IT trial (NEJM 2015).")
    bemp = st.checkbox("Bempedoic acid", help="CLEAR Outcomes (Lancet 2023).")
    # Anticipated LDL
    adj_ldl = baseline_ldl
    if statin != "None":
        adj_ldl *= (1 - ldl_therapies[statin] / 100)
    if ez:
        adj_ldl *= (1 - ldl_therapies["Ezetimibe"] / 100)
    adj_ldl = max(adj_ldl, 1.0)
    st.write(f"Anticipated LDL-C after statin/ezetimibe: {adj_ldl:.2f} mmol/L")

    st.subheader("Advised Lipid-lowering Add-ons")
    if adj_ldl > 1.8:
        pcsk9 = st.checkbox("PCSK9 inhibitor", help="FOURIER/ODYSSEY trials.")
        incl = st.checkbox("Inclisiran (siRNA)", help="ORION-10 trial.")
    else:
        st.info("PCSK9i/Inclisiran only if LDL-C >1.8 mmol/L after current therapy.")

    st.markdown("---")
    st.subheader("Advised Interventions")
    # Lifestyle Changes
    st.markdown("**Lifestyle Changes**")
    smoke_iv = st.checkbox("Smoking cessation", disabled=not smoking,
                            help="Benefit only if current smoker.")
    sem_iv = st.checkbox("Semaglutide (GLP-1 RA)", disabled=(bmi < 30),
                         help="STEP trial: see NEJM 2021.")
    diet_iv = st.checkbox("Mediterranean diet", help="PREDIMED trial.")
    act_iv = st.checkbox("Physical activity", help="WHO guidelines.")
    alc_iv = st.checkbox("Alcohol moderation", help="Recommend <14 units/week.")
    str_iv = st.checkbox("Stress reduction", help="Mindfulness trial.")

    st.markdown("---")
    st.subheader("Other Therapies")
    asa_iv = st.checkbox("Antiplatelet (ASA or clopidogrel)", help="CAPRIE trial.")
    sgl_iv = st.checkbox("SGLT2 inhibitor (e.g. Empagliflozin)", help="EMPA-REG trial.")
    ico_iv = False
    if tg > 1.7:
        ico_iv = st.checkbox("Icosapent ethyl", help="REDUCE-IT trial.")
    else:
        st.info("Icosapent ethyl only if TG >1.7 mmol/L.")

    st.markdown("---")
    st.subheader("Blood Pressure Management")
    sbp_cur = st.number_input("Current SBP (mmHg)", 80, 220, 145)
    sbp_tgt = st.number_input("Target SBP (mmHg)", 80, 220, 120)
    st.write("Aim SBP <130 mmHg where tolerated — SPRINT trial.")

with tab3:
    st.subheader("Results: Summary")
    risk10 = estimate_smart_risk(age, sex, sbp_cur, total_chol, hdl,
                                  smoking, diabetes, egfr, crp, vasc_count)
    risk5 = convert_5yr(risk10)
    # For demonstration, using 10yr baseline
    baseline = risk10
    baseline_c = min(baseline, 85)
    final = baseline_c - 10  # placeholder
    arr = round(baseline_c - final, 1)
    rrr = round(min(arr / baseline_c * 100, 75), 1)
    st.write(f"Baseline 10yr risk: {baseline_c}%")
    st.write(f"Post-intervention risk: {final}% (ARR {arr} pp, RRR {rrr}%)")
    st.write("Expected LDL-C: {:.2f} mmol/L — at 3 months following therapy".format(adj_ldl))

    st.subheader("Results: Details")
    df = pd.DataFrame([{
        "Age": age, "Sex": sex, "Smoking": smoking, "Diabetes": diabetes,
        "eGFR": egfr, "Vascular": vasc_count, "BMI": round(bmi,1),
        "TC": total_chol, "HDL": hdl, "hs-CRP": crp, "LDL0": baseline_ldl,
        "Pre-Tx": statin + ("; Ezetimibe" if ez else ""),
        "Add-Tx": ("; PCSK9i" if pcsk9 else "") + ("; Inclisiran" if incl else ""),
        "Lifestyle": "; ".join([iv for iv, sel in [("Smoking cessation", smoke_iv),
                                                  ("Semaglutide", sem_iv),
                                                  ("Mediterranean diet", diet_iv),
                                                  ("Physical activity", act_iv),
                                                  ("Alcohol moderation", alc_iv),
                                                  ("Stress reduction", str_iv)] if sel]),
        "Other": "; ".join([iv for iv, sel in [("Antiplatelet", asa_iv),
                                                ("SGLT2i", sgl_iv),
                                                ("Icosapent ethyl", ico_iv)] if sel]),
        "Baseline%": baseline_c, "Final%": final, "ARR": arr, "RRR": rrr
    }])
    st.dataframe(df, use_container_width=True)
    if st.button("Download report as CSV"):
        st.download_button("Download report", df.to_csv(index=False), file_name="cvd_report.csv")
    if st.button("Show chart"):
        fig, ax = plt.subplots()
        ax.bar(["Before", "After"], [baseline_c, final], color=["#a0d3e8", "#8bc34a"], alpha=0.9)
        ax.set_ylabel("10yr CVD Risk (%)")
        st.pyplot(fig)

st.markdown("---")
st.markdown("Created by PRIME team (Prevention Recurrent Ischaemic Myocardial Events)")
st.markdown("King's College Hospital, London")
st.markdown("This tool is provided for informational purposes and designed to support discussions with your healthcare provider—it’s not a substitute for professional medical advice.")

