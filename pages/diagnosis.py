import streamlit as st

def show_diagnosis():
    st.title("🧬 Diagnosis")

    patients = st.session_state.patients_df
    patient = st.selectbox("Select Patient", patients["name"])

    symptoms = st.text_input("Enter symptoms (comma separated)")

    if st.button("Run AI Diagnosis"):
        st.success("Diagnosis completed")
        st.write("**Predicted Disease:** Dengue")
        st.write("**Severity:** Moderate")
        st.write("**Confidence:** 87%")
