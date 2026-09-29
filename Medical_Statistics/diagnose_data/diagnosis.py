import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.naive_bayes import MultinomialNB
import matplotlib.pyplot as plt
from diagnose_data.patients_crud import load_patients_basic
import math
from sklearn.linear_model import LinearRegression
from diagnose_data import diagnosis_crud
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import black, grey
from reportlab.lib.enums import TA_CENTER
from io import BytesIO
import requests
import pandas as pd


hospital= [
    {"name":"Fortis Hospital",
    "address":"Bhandup West, Mumbai",
    "contact":"022-12345678",
    "email":"info@fortishospital.com",
    "logo":"https://upload.wikimedia.org/wikipedia/en/thumb/0/0b/Fortis_Hospital_Logo.svg/1200px-Fortis_Hospital_Logo.svg.png"},
    {"name":"Apollo Hospital",
    "address":"Andheri East, Mumbai",
    "contact":"022-87654321",
    "email":"info@apollohospital.com",
    "logo":"https://upload.wikimedia.org/wikipedia/en/thumb/5/5e/Apollo_Hospitals_Logo.svg/1200px-Apollo_Hospitals_Logo.svg.png"},
    {"name":"Lilavati Hospital",
    "address":"Lilavati Hospital, Mumbai",
    "contact":"022-98765432",
    "email":"info@lilavatihospital.com",
    "logo":"https://upload.wikimedia.org/wikipedia/en/thumb/0/0b/Lilavati_Hospital_Logo.svg/1200px-Lilavati_Hospital_Logo.svg.png"}
]

# MAIN PAGE FUNCTION

@st.cache_data
def load_and_prepare_data():
    df = pd.read_csv(
        "C:\\Users\\Atharv\\OneDrive\\Desktop\\Medical_Statistics\\diagnose_data\\dataset.csv"
    )
    symptom_cols = df.columns[1:]
    df[symptom_cols] = (
        df[symptom_cols]
        .apply(lambda col: col.astype(str).str.strip())
        .replace("", np.nan)
    )
    all_symptoms = sorted(
        df[symptom_cols]
        .stack()
        .dropna()
        .unique()
    )

    X = pd.DataFrame(0, index=df.index, columns=all_symptoms)
    for i, row in df.iterrows():
        for symptom in row[symptom_cols].dropna():
            X.at[i, symptom] = 1

    disease_encoder = LabelEncoder()
    y = disease_encoder.fit_transform(df["Disease"])

    return X, y, all_symptoms, disease_encoder

@st.cache_resource
def train_model(X, y):
    model = MultinomialNB()
    model.fit(X, y)
    return model

@st.cache_data
def load_recovery_data(disease):
    df = pd.read_csv(
        "C:\\Users\\Atharv\\OneDrive\\Desktop\\Medical_Statistics\\disease_data.csv"
    )

    df["Disease"] = df["Disease"].astype(str).str.strip()
    disease = disease.strip()

    if df.empty:
        return None, None
    
    df=df[df["Disease"]==disease]

    X = df[["Age"]]
    y = df["Recovery Time"]

    return X, y

@st.cache_resource
def train_recovery_model(X, y):
    model = LinearRegression()
    model.fit(X, y)
    return model

def predict_recovery_time(age, model):
    predicted_days = model.predict([[age]])[0]
    return max(7, min(round(predicted_days),30))

#Print details
def create_pdf_report(
    hospital,
    selected_patient,
    patient_info,
    doctor_name,
    symptoms,
    predicted_disease,
    final_disease,
    recovery_days,
    hemoglobin,
    wbc,
    platelets,
    urine_color,
    urine_observation,
    urine_condition,
    additional_notes
):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        rightMargin=40,
        leftMargin=40,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        name="TitleStyle",
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=15
    )

    section_style = ParagraphStyle(
        name="SectionStyle",
        fontSize=14,
        spaceAfter=8
    )

    normal_style = styles["Normal"]

    elements = []

    # ============================
    # LOAD APP LOGO (LOCAL)
    # ============================

    try:
        app_logo = Image("logo2.png", width=25, height=1*inch)
    except:
        app_logo = ""

    # ============================
    # LOAD HOSPITAL LOGO (FROM JSON URL)
    # ============================

    hospital_logo = ""

    if hospital.get("logo"):
        try:
            response = requests.get(hospital["logo"])
            hospital_logo_bytes = BytesIO(response.content)
            hospital_logo = Image(
                hospital_logo_bytes,
                width=1*inch,
                height=1*inch
            )
        except:
            hospital_logo = ""

    # ============================
    # HEADER TABLE
    # ============================

    hospital_details = Paragraph(
        f"""
        <b>{hospital['name']}</b><br/>
        {hospital['address']}<br/>
        Contact: {hospital['contact']}<br/>
        Email: {hospital['email']}
        """,
        normal_style
    )

    header_table = Table(
        [
            [app_logo, hospital_details, hospital_logo]
        ],
        colWidths=[1.3*inch, 3.9*inch, 1.3*inch]
    )

    header_table.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))

    elements.append(header_table)

    elements.append(Spacer(1, 15))

    elements.append(Paragraph(
        "<b>MEDICAL DIAGNOSTIC REPORT</b>",
        title_style
    ))

    # ============================
    # PATIENT DETAILS
    # ============================

    elements.append(Paragraph("<b>Patient Details</b>", section_style))

    patient_table = Table([
        ["Patient Name", selected_patient],
        ["Age", str(patient_info["age"])],
        ["Gender", patient_info["gender"]],
        ["Doctor", f"Dr. {doctor_name}"],
        ["Report Date", pd.Timestamp.now().strftime("%Y-%m-%d")]
    ])

    patient_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, black),
        ("BACKGROUND", (0,0), (0,-1), grey),
    ]))

    elements.append(patient_table)

    elements.append(Spacer(1, 15))

    # ============================
    # SYMPTOMS
    # ============================

    elements.append(Paragraph("<b>Symptoms</b>", section_style))

    elements.append(
        Paragraph(", ".join(symptoms) if symptoms else "None", normal_style)
    )

    elements.append(Spacer(1, 15))

   
    # BLOOD TEST WITH REFERENCES

    elements.append(Paragraph("<b>Blood Test Results</b>", section_style))

    blood_table = Table([
        ["Test", "Observed", "Reference Range", "Unit"],
        ["Hemoglobin", hemoglobin, "13.5–17.5 (Male), 12–15.5 (Female)", "g/dL"],
        ["WBC", wbc, "4,000–11,000", "cells / µL"],
        ["Platelets", platelets, "150,000–450,000", "cells / µL"]
    ])

    blood_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, black),
        ("BACKGROUND", (0,0), (-1,0), grey),
    ]))

    elements.append(blood_table)

    elements.append(Spacer(1, 15))

    # URINE TEST

    elements.append(Paragraph("<b>Urine Test Results</b>", section_style))

    urine_table = Table([
        ["Color", urine_color],
        ["Observation", urine_observation],
        ["Condition", urine_condition]
    ])

    urine_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, black),
        ("BACKGROUND", (0,0), (0,-1), grey),
    ]))

    elements.append(urine_table)
    elements.append(Spacer(1, 15))
    # DIAGNOSIS
    elements.append(Paragraph("<b>Diagnosis</b>", section_style))
    diagnosis_table = Table([
        ["Predicted Disease", predicted_disease],
        ["Final Diagnosis", final_disease],
        ["Recovery Time", f"{recovery_days} days"]
    ])

    diagnosis_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, black),
        ("BACKGROUND", (0,0), (0,-1), grey),
    ]))

    elements.append(diagnosis_table)

    elements.append(Spacer(1, 15))

    # NOTES
    elements.append(Paragraph("<b>Medication+Notes</b>", section_style))

    elements.append(
        Paragraph(additional_notes if additional_notes else "None", normal_style)
    )

    elements.append(Spacer(1, 30))

    elements.append(
        Paragraph("Doctor Signature: _________________________", normal_style)
    )
    # BUILD PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


#Main page
def show_diagnosis():
    st.title("Disease Prediction System")
    appointment_tab,prediction_tab,blood_tab, urine_tab, diagnostic_tab = st.tabs(["Schedule Session","Predict Disease through Symptoms","Blood Test", "Urine Test", "Final Diagnostic Report"])
    
    with appointment_tab:

    # Import Custom Font + Styling
        st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

        html, body, [class*="css"]  {
            font-family: 'Poppins', sans-serif;
        }

        .custom-card {
            background-color: #f5f7fa;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.08);
            margin-top: 10px;
        }

        .custom-title {
            font-size: 26px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 15px;
        }

        .patient-info {
            font-size: 18px;
            font-weight: 400;
            color: #34495e;
        }

        .highlight {
            font-weight: 600;
            color: #1abc9c;
        }
        </style>
    """, unsafe_allow_html=True)
        hospital_names = [h["name"] for h in hospital]
        selected_hospital_name = st.selectbox("🏥 Select Hospital", hospital_names)

# Get selected hospital details
        selected_hospital = next(h for h in hospital if h["name"] == selected_hospital_name)

    # Custom Header
        st.markdown('<div class="custom-title">👤 Select Patient</div>', unsafe_allow_html=True)

        patients_df = load_patients_basic()
        selected_patient = st.selectbox("Choose patient", patients_df["name"])

        patient_info = patients_df[
        patients_df["name"] == selected_patient
    ].iloc[0]

    # Custom Info Card
        st.markdown(f"""
        <div class="custom-card">
            <div class="patient-info">
                <span class="highlight">Name:</span> {selected_patient} <br><br>
                <span class="highlight">Age:</span> {patient_info['age']} <br><br>
                <span class="highlight">Gender:</span> {patient_info['gender']}
            </div>
        </div>
    """, unsafe_allow_html=True)
        doctor_name = st.text_input("👨‍⚕️ Enter Doctor Name")

        if doctor_name:
            st.success(f"Session scheduled with Dr. {doctor_name} at {selected_hospital_name}.")

    # PREDICTION TAB
    with prediction_tab:
        with st.spinner("Loading diagnosis engine..."):
            X, y, all_symptoms, disease_encoder = load_and_prepare_data()
            model = train_model(X, y)
        st.subheader("🧾 Select Symptoms")
        selected_symptoms = st.multiselect("Choose symptoms you are experiencing:",all_symptoms)

        def prepare_input(symptoms):
            vec = np.zeros(len(all_symptoms))
            for s in symptoms:
                vec[all_symptoms.index(s)] = 1
            return vec.reshape(1, -1)

        if st.button("Predict Disease"):
            if not selected_symptoms:
                st.warning("Please select at least one symptom.")
            else:
                probs = model.predict_proba(prepare_input(selected_symptoms))[0]
                idx = np.argmax(probs)
                predicted_disease = disease_encoder.inverse_transform([model.classes_[idx]])[0]
                st.success(f"**Predicted Disease:** {predicted_disease}")
                st.info(f"**Confidence:** {probs[idx] * 100:.2f}%")        
                st.session_state.predicted_disease = predicted_disease

    # BLOOD TEST TAB
    with blood_tab:
        st.subheader("Blood Composition Analysis")
        analyze=st.button("Analyze")
    # Inputs
        blood_volume = st.number_input("Blood Volume (mL)", 2.0, 3.0, 2.5, 0.1)
        plasma = st.number_input("Plasma Volume (mL)", 0.8, blood_volume, 1.4, 0.1)
        hemoglobin = st.number_input("Hemoglobin (g/dL)",min_value=0.0,step=0.1,value=14.5)
        wbc = st.number_input("WBC (cells / µL)", 8000.0)
        platelets = st.number_input("Platelets (cells / µL)", 200000.0)
        rbc = (hemoglobin / 3) * 1_000_000

    # Composition 
        def composition(rbc, wbc, plt, plasma, total):
            plasma_pct = (plasma / total) * 100
            cell_pct = 100 - plasma_pct
            total_cells = rbc + wbc + plt
            if total_cells==0:
                return [0, 0, 0, plasma_pct]
            rbc_pct=(rbc / total_cells) * cell_pct
            wbc_pct=(wbc / total_cells) * cell_pct
            plt_pct=(plt / total_cells) * cell_pct
            return [rbc_pct, wbc_pct, plt_pct, plasma_pct]
        if analyze:
            healthy = composition(5e6, 7000, 250000, 1.375, blood_volume)
            observed = composition(rbc, wbc, platelets, plasma, blood_volume)
            col1, col2 = st.columns([1, 1.1])
    # BAR CHART
            with col1:
                st.markdown("Blood Composition")
                fig, ax = plt.subplots(figsize=(2.6, 3.0), dpi=100)
                labels = ["RBCs", "WBCs", "Platelets", "Plasma"]
                colors = ["#ff1a1a", "#d0d0d0", "#ff9933", "#ffff4c"]
                def draw(x, vals):
                    bottom = 0
                    for v, c in zip(vals, colors):
                        ax.bar(x, v, bottom=bottom, color=c, width=0.45)
                        bottom += v
                draw(0, healthy)
                draw(1, observed)
                ax.set_ylim(0, 100)
                ax.set_xticks([0, 1])
                ax.set_xticklabels(["Healthy", "Observed"], fontsize=7)
                ax.legend(labels, fontsize=6)
                ax.tick_params(axis="y", labelsize=6)
                st.pyplot(fig, clear_figure=True) 
                # HYPOTHESIS TESTING
                with col2:
                    st.markdown("Individual Blood Cell Hypothesis Testing")
                    tabs = st.tabs(["Hemoglobin", "WBC", "Platelets"])
                    def normal_test(observed, mean, std, label, unit):
                        z = (observed - mean) / std
                        p = 2*(1-0.5*(1+math.erf(abs(z)/math.sqrt(2))))
                        # Bell curve
                        x = np.linspace(mean - 4*std, mean + 4*std, 500)
                        y = (1 / (std * np.sqrt(2 * np.pi))) * np.exp(
                        -0.5 * ((x - mean) / std) ** 2)
                        fig, ax = plt.subplots(figsize=(3.2, 2.4))
                        ax.plot(x, y, linewidth=2)
                        ax.axvline(observed, linestyle="--", linewidth=2)
                        ax.set_title(f"{label} Distribution", fontsize=9)
                        ax.set_xlabel(unit, fontsize=8)
                        ax.set_ylabel("Probability Density", fontsize=8)
                        ax.tick_params(labelsize=7)
                        st.pyplot(fig, clear_figure=True)
                        # Inference
                        if p < 0.05:
                            st.error(f"⚠️ Significant deviation detected (p = {p:.4f})")
                            if observed < mean:
                                st.warning(f"⬇️ Low {label} count")
                            else:
                                st.warning(f"⬆️ High {label} count")
                        else:
                            st.success(f"✅ {label} count is within normal range (p = {p:.4f})")

        # RBC
                    with tabs[0]:
                        normal_test(observed=hemoglobin,mean=14.5,std=1.5,label="Hemoglobin",unit="g/dL")
                        if hemoglobin<14.5:
                            st.warning("Low Hemoglobin,Potential Disease:Anemia")

        # WBC
                    with tabs[1]:
                        normal_test(observed=wbc,mean=7000,std=1500,label="WBC",unit="cells / µL")
                        if wbc<7000:
                            st.warning("Low WBC,Potential Disease:Leukopenia")
                        elif wbc>11000:
                            st.warning("High WBC,Potential Disease:Infection or Leukemia")

        # Platelets
                    with tabs[2]:
                        normal_test(observed=platelets,mean=250000,std=50000,label="Platelets",unit="cells / µL")
                        if platelets<150000:
                            st.warning("Low Platelets,Potential Disease:Thrombocytopenia, Dengue")

    # URINE TEST TAB
    # =========================
    with urine_tab:
        st.subheader("Urine Test")
        urine_scale = [
            ("Pale Yellow", "#FFFACD", "Well hydrated", "Normal"),
            ("Yellow", "#FFD700", "Normal urine color", "Healthy"),
            ("Dark Yellow", "#DAA520", "Mild dehydration", "Drink more water"),
            ("Amber", "#FFBF00", "Dehydration", "Dehydration risk"),
            ("Orange", "#FF8C00", "Possible liver issue", "Liver disorder"),
            ("Red", "#B22222", "Blood detected", "UTI / Kidney stones"),
            ("Brown", "#654321", "Severe dehydration", "Liver disorder"),
            ("Cloudy", "#E8E8E8", "Possible infection", "UTI")
        ]
        color_index = st.slider(" ",0,len(urine_scale) - 1,2,label_visibility="collapsed")
        color_name, color_hex, observation, condition = urine_scale[color_index]
        position_percent = (color_index / (len(urine_scale) - 1)) * 100

        st.markdown(
        f"""
        <style>
        /* Remove tooltip number */
        div[data-baseweb="slider"] span {{
            display: none;
        }}
        /* Slider track gradient */
        div[data-baseweb="slider"] > div {{
            background: linear-gradient(
                to right,
                #FFFACD, #FFD700, #DAA520, #FFBF00,
                #FF8C00, #B22222, #654321, #E8E8E8
            );
            height: 12px;
            border-radius: 12px;
        }}

        /* Slider thumb */
        div[data-baseweb="thumb"] {{
            background-color: {color_hex} !important;
            border: 3px solid black;
            width: 22px;
            height: 22px;
        }}

        /* Floating color label */
        .color-label {{
            position: relative;
            top: -40px;
            left: {position_percent}%;
            transform: translateX(-50%);
            font-weight: bold;
            color: {color_hex};
            font-size: 14px;
            background: black;
            padding: 3px 10px;
            border-radius: 10px;
            display: inline-block;
        }}
        </style>

        <div class="color-label">{color_name}</div>
        """,
        unsafe_allow_html=True
        )
        st.divider()
        st.success(f"Observed Color: **{color_name}**")
        st.warning(f"Inference: **{observation}**")
        st.info(f"Possible Condition: **{condition}**")

    with diagnostic_tab:
        st.subheader("Final Diagnostics")
        if "predicted_disease" not in st.session_state:
            st.warning("⚠️ No predicted disease available. Please complete symptom diagnosis first.")
            st.stop()
        # Final disease input
        final_disease = st.text_input("Final Diagnosed Disease",value=st.session_state.get("final_diagnosis",st.session_state.predicted_disease))
        if st.button("Confirm Diagnosis"):
            st.session_state.final_diagnosis = final_disease
            st.success("Final diagnosis saved")

        # RECOVERY TIME PREDICTION
        if "final_diagnosis" in st.session_state:
            X, y = load_recovery_data(st.session_state.final_diagnosis)
            if X is None or X.empty:
                st.error("No recovery data available for this disease.")
                st.stop()
            recovery_model = train_recovery_model(X, y)
            patients_df = load_patients_basic()
            patient_age = patients_df[patients_df["name"] == selected_patient].iloc[0]["age"]
            recovery_days = predict_recovery_time(patient_age, recovery_model)
            if recovery_days is None:
                st.error("Not enough data to predict recovery time for this disease.")
            else:
                st.markdown("--Final Diagnosis--")
                st.markdown("Name of Patient:**{}**".format(selected_patient))
                st.markdown("Diagnosed Disease: **{}**".format(final_disease))
                st.markdown("Age of Patient: **{} years**".format(patient_age))
                st.success(f"Estimated Recovery Time: **{recovery_days} days**")
                additional_info = st.text_area("Additional Notes for Patient")


                #Print details
                if st.button("Generate Report"):

                    selected_hospital = next(h for h in hospital if h["name"] == selected_hospital_name)
                    patient_info = patients_df[
                    patients_df["name"] == selected_patient].iloc[0]

                    pdf_buffer=create_pdf_report(
                       hospital=selected_hospital,
                       selected_patient=selected_patient,
                        patient_info=patient_info,
                        doctor_name=doctor_name,
                          symptoms=selected_symptoms,
                          predicted_disease=st.session_state.get("predicted_disease", ""),
                        final_disease=final_disease,
                        recovery_days=recovery_days,
                         hemoglobin=hemoglobin,
                         wbc=wbc,
                        platelets=platelets,
                        urine_color=color_name,
                          urine_observation=observation,
                         urine_condition=condition,
                        additional_notes=additional_info)
                      
                    st.download_button(label="Download Report as PDF",data=pdf_buffer, file_name=f"{selected_patient}_diagnostic_report.pdf",mime="application/pdf")


                #Saving diagnosis to database
                if st.button("Save Diagnosis"):
                    diagnosis_crud.save_diagnosis(
                        patient_id = patients_df[patients_df["name"] == selected_patient].iloc[0]["id"],
                        disease=final_disease,
                        status="Diagnosed",
                        symptoms=selected_symptoms,
                        expected_recovery_time=recovery_days,
                        date_of_diagnosis=pd.Timestamp.now().strftime("%Y-%m-%d"),
                        date_of_recoveryordischarge=None,
                        actual_recovery_time=None
                    )
                    st.success("Diagnosis saved to database!")
            st.caption("Prediction based on regression using patient age and diagnosed disease")

    
