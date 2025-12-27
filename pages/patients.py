import streamlit as st
import pandas as pd
from datetime import date

# ---------------------------
# ADD PATIENT DIALOG
# ---------------------------
@st.dialog("➕ Add New Patient")
def add_patient_dialog():

    with st.form("add_patient_form"):

        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input("Name")
        with col2:
            age = st.number_input("Age", 0, 120, 30)
        with col3:
            gender = st.radio("Gender", ["Male", "Female", "Other"], horizontal=True)

        col4, col5 = st.columns(2)
        with col4:
            phone = st.text_input("Phone Number")
        with col5:
            email = st.text_input("Email")

        col6, col7 = st.columns(2)
        with col6:
            blood_group = st.radio(
                "Blood Group",
                ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
                horizontal=True
            )
        with col7:
            emergency_contact = st.text_input("Emergency Contact")

        address = st.text_area("Address")

        st.subheader("Insurance Details")
        col8, col9 = st.columns(2)
        with col8:
            insurance_provider = st.text_input("Provider")
        with col9:
            insurance_policy = st.text_input("Policy ID")

        col10, col11 = st.columns(2)
        with col10:
            admission_date = st.date_input("Date of Admission", date.today())
        with col11:
            status = st.selectbox("Status", ["Active", "Recovered", "Critical"])

        submitted = st.form_submit_button("Add Patient")

        if submitted:
            df = st.session_state.patients_df

            new_patient = {
                "id": int(df["id"].max()) + 1 if not df.empty else 1,
                "name": name,
                "age": age,
                "gender": gender,
                "phone": phone,
                "email": email,
                "blood_group": blood_group,
                "emergency_contact": emergency_contact,
                "address": address,
                "insurance_provider": insurance_provider,
                "insurance_policy": insurance_policy,
                "last_visited": str(admission_date),
                "status": status
            }

            st.session_state.patients_df = pd.concat(
                [df, pd.DataFrame([new_patient])],
                ignore_index=True
            )

            st.success("Patient added successfully")
            st.rerun()


# ---------------------------
# EDIT PATIENT DIALOG
# ---------------------------
@st.dialog("✏️ Edit Patient")
def edit_patient_dialog(index):

    df = st.session_state.patients_df
    patient = df.loc[index]

    with st.form("edit_patient_form"):

        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input("Name", patient["name"])
        with col2:
            age = st.number_input("Age", 0, 120, int(patient["age"]))
        with col3:
            gender = st.radio(
                "Gender",
                ["Male", "Female", "Other"],
                index=["Male", "Female", "Other"].index(patient.get("gender","Male")),
                horizontal=True
            )

        col4, col5 = st.columns(2)
        with col4:
            phone = st.text_input("Phone", patient.get("phone",""))
        with col5:
            email = st.text_input("Email", patient.get("email",""))

        col6, col7 = st.columns(2)
        with col6:
            emergency_contact = st.text_input(
                "Emergency Contact",
                patient.get("emergency_contact","")
            )
        with col7:
            status = st.selectbox(
                "Status",
                ["Active", "Recovered", "Critical"],
                index=["Active","Recovered","Critical"].index(patient["status"])
            )

        address = st.text_area("Address", patient.get("address",""))

        insurance_policy = st.text_input(
            "Insurance Policy ID",
            patient.get("insurance_policy","")
        )

        submitted = st.form_submit_button("Save Changes")

        if submitted:
            for field, value in {
                "name": name,
                "age": age,
                "gender": gender,
                "phone": phone,
                "email": email,
                "emergency_contact": emergency_contact,
                "address": address,
                "insurance_policy": insurance_policy,
                "status": status
            }.items():
                st.session_state.patients_df.at[index, field] = value

            st.success("Patient updated successfully")
            st.rerun()


# ---------------------------
# MAIN PATIENTS PAGE
# ---------------------------
def show_patients():

    st.title("👨‍⚕️ Patients")

    # ---- TOP BAR ----
    col_search, col_add = st.columns([3, 1])

    with col_search:
        query = st.text_input(
            "",
            placeholder="🔍 Search patient by name"
        )

    with col_add:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Add Patient", use_container_width=True):
            add_patient_dialog()

    df = st.session_state.patients_df.copy()

    if query:
        df = df[df["name"].str.contains(query, case=False)]

    if df.empty:
        st.info("No patients found")
        return

    df = df.reset_index()

    # ---- 3x3 CARD GRID ----
    cols = st.columns(3)

    for i, row in df.iterrows():
        with cols[i % 3]:
            with st.container(border=True):

                letter = row["name"][0].upper()

                st.markdown(
                    f"""
                    <div style="
                        width:70px;
                        height:70px;
                        border-radius:12px;
                        background:#4f46e5;
                        color:white;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        font-size:28px;
                        font-weight:bold;
                        margin-bottom:10px;
                    ">
                        {letter}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(f"### {row['name']}")
                st.markdown(f"**Age:** {row['age']}")
                st.markdown(f"**Gender:** {row.get('gender','—')}")
                st.markdown(f"**Phone:** {row.get('phone','—')}")
                st.markdown(f"**Last Visited:** {row.get('last_visited','—')}")

                if st.button("✏️ Edit", key=f"edit_{row['id']}"):
                    edit_patient_dialog(row["index"])
