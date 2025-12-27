import streamlit as st
import matplotlib.pyplot as plt

def patient_status_counts(df):
    statuses = ["Active", "Recovered", "Critical"]
    counts = df["status"].value_counts()
    return [counts.get(s, 0) for s in statuses], statuses

def stat_card(title, value, icon):
    st.image(icon, width=40)
    st.metric(title, value)

def show_dashboard():
    st.title("📊 Hospital Dashboard")

    patients_df = st.session_state.patients_df
    diagnosis_df = st.session_state.diagnosis_df
    billing_df = st.session_state.billing_df

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        stat_card("Total Patients", len(patients_df), "assets/patient.png")
    with c2:
        stat_card("Active Cases", (patients_df.status=="Active").sum(), "assets/active.png")
    with c3:
        stat_card("Total Diagnoses", len(diagnosis_df), "assets/diagnosis.png")
    with c4:
        stat_card("Revenue Collected", f"₹ {billing_df.amount.sum():,}", "assets/revenue.png")

    st.markdown("---")
    st.subheader("Patient Status Distribution")

    values, labels = patient_status_counts(patients_df)

    # define consistent colors for statuses
    status_colors = {
        "Active": "#66c2a5",
        "Recovered": "#8da0cb",
        "Critical": "#fc8d62",
    }
    colors = [status_colors.get(l, "#dddddd") for l in labels]

    fig, ax = plt.subplots(figsize=(2.5, 2.5))
    # remove percentage labels (autopct) per request
    # remove labels near the pie chart
    wedges, texts = ax.pie(values, labels=None, colors=colors, startangle=90, wedgeprops={"linewidth": 1, "edgecolor": "white"})
    ax.axis("equal")
    st.pyplot(fig, use_container_width=False)

    # Show colored labels alongside counts for Active, Recovered, and Critical, one below the other
    status_counts = dict(zip(labels, values))
    a_count = status_counts.get("Active", 0)
    r_count = status_counts.get("Recovered", 0)
    c_count = status_counts.get("Critical", 0)

    st.markdown(f'<span style="display:inline-block;width:12px;height:12px;background:{status_colors["Active"]};margin-right:8px;border-radius:2px;"></span> <b>Active:</b> {a_count}', unsafe_allow_html=True)
    st.markdown(f'<span style="display:inline-block;width:12px;height:12px;background:{status_colors["Recovered"]};margin-right:8px;border-radius:2px;"></span> <b>Recovered:</b> {r_count}', unsafe_allow_html=True)
    st.markdown(f'<span style="display:inline-block;width:12px;height:12px;background:{status_colors["Critical"]};margin-right:8px;border-radius:2px;"></span> <b>Critical:</b> {c_count}', unsafe_allow_html=True)
