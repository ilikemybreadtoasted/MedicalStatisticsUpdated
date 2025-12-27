import streamlit as st
import pandas as pd

from pages.dashboard import show_dashboard
from pages.patients import show_patients
from pages.diagnosis import show_diagnosis
from pages.statistics import show_statistics
from pages.billing import show_billing

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="Hospital Dashboard", layout="wide")
st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True
)
# ---------------------------
# SESSION STATE (BACKEND)
# ---------------------------
if "patients_df" not in st.session_state:
    if "patients_df" not in st.session_state:
        st.session_state.patients_df = pd.DataFrame([
        {
            "id": 1,
            "name": "Rahul",
            "age": 32,
            "gender": "Male",
            "phone": "9876543210",
            "emergency_contact": "9876500000",
            "address": "Mumbai",
            "insurance_policy": "LIC-112233",
            "last_visited": "2025-01-10",
            "status": "Active"
        },
        {
            "id": 2,
            "name": "Anita",
            "age": 45,
            "gender": "Female",
            "phone": "9876541111",
            "emergency_contact": "9876501111",
            "address": "Pune",
            "insurance_policy": "HDFC-998877",
            "last_visited": "2025-01-05",
            "status": "Recovered"
        },
        {
            "id": 3,
            "name": "Suresh",
            "age": 60,
            "gender": "Male",
            "phone": "9876542222",
            "emergency_contact": "9876502222",
            "address": "Delhi",
            "insurance_policy": "STAR-445566",
            "last_visited": "2025-01-12",
            "status": "Critical"
        },
    ])

if "diagnosis_df" not in st.session_state:
    st.session_state.diagnosis_df = pd.DataFrame([
        {"patient_id": 1, "disease": "Dengue"},
        {"patient_id": 2, "disease": "Flu"},
    ])

if "billing_df" not in st.session_state:
    st.session_state.billing_df = pd.DataFrame([
        {"patient_id": 1, "amount": 12000},
        {"patient_id": 2, "amount": 8000},
    ])

# ---------------------------
# SIDEBAR NAVIGATION
# ---------------------------
st.sidebar.markdown("## 🏥 Hospital Menu")

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

def nav(label):
    if st.sidebar.button(label, use_container_width=True):
        st.session_state.page = label
        st.rerun()

nav("Dashboard")
nav("Patients")
nav("Diagnosis")
nav("Statistics")
nav("Billing")

st.sidebar.markdown("---")
st.sidebar.button("Logout", use_container_width=True)

# ---------------------------
# PAGE ROUTING
# ---------------------------
page = st.session_state.page

if page == "Dashboard":
    show_dashboard()

elif page == "Patients":
    show_patients()

elif page == "Diagnosis":
    show_diagnosis()

elif page == "Statistics":
    show_statistics()

elif page == "Billing":
    show_billing()
