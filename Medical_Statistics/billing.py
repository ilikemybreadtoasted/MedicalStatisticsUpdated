import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


# =========================================================
# DATABASE FUNCTIONS
# =========================================================

def get_connection():
    conn = sqlite3.connect("patients.db")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def get_patients():
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT id, name, age, gender,
               insurance_policy, policy_id, coverage
        FROM patients
    """, conn)
    conn.close()
    return df


def save_bill_to_db(patient_id, total, deduction, final_amount):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO billing 
        (patient_id, total_amount, insurance_deduction, final_payable, payment_status, payment_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        patient_id,
        total,
        deduction,
        final_amount,
        "Paid",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


# =========================================================
# PDF GENERATION
# =========================================================

def generate_bill_pdf(bill):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>Hospital Billing Receipt</b>", styles["Title"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"Patient Name: {bill['Patient Name']}", styles["Normal"]))
    elements.append(Paragraph(f"Date: {bill['Date']}", styles["Normal"]))
    elements.append(Paragraph(f"Insurance Policy: {bill['Insurance Policy']}", styles["Normal"]))
    elements.append(Paragraph(f"Policy ID: {bill['Policy ID']}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    table_data = [
        ["Description", "Amount (₹)"],
        ["Consultation", bill["Consultation"]],
        ["Blood Test", bill["Blood Test"]],
        ["Urine Test", bill["Urine Test"]],
        ["Medicine", bill["Medicine"]],
        ["Hospital Stay", bill["Hospital Stay"]],
        ["GST (5%)", bill["GST"]],
        ["Total Amount", bill["Total Amount"]],
        ["Insurance Deduction", bill["Insurance Deduction"]],
        ["Final Payable", bill["Final Payable"]],
    ]

    table = Table(table_data, colWidths=[300, 150])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
    ]))

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    return buffer

# BILLING PAGE
def show_billing():
    st.title("💳 Patient Billing System")
    patients = get_patients()
    if patients.empty:
        st.warning("⚠ No patients found in database.")
        return
    # ------------------ Patient Selection ------------------
    selected_id = st.selectbox(
        "Select Patient",
        patients["id"],
        format_func=lambda x: patients.loc[
            patients["id"] == x, "name"
        ].values[0]
    )

    patient = patients[patients["id"] == selected_id].iloc[0]

    # ------------------ Display Patient Info ------------------
    st.info(
        f"""
👤 Name: {patient['name']}  
🎂 Age: {patient['age']}  
⚧ Gender: {patient['gender']}  
🛡 Insurance: {patient['insurance_policy']}  
📄 Policy ID: {patient['policy_id']}  
📊 Coverage: {patient['coverage']}%
"""
    )

    # ------------------ Charges ------------------
    consultation = 500
    st.write("🩺 **Consultation Fee:** ₹500 (Fixed)")

    st.subheader("🧪 Diagnostic Tests")
    blood_test = st.checkbox("Blood Test (₹500)")
    urine_test = st.checkbox("Urine Test (₹500)")

    blood_charge = 500 if blood_test else 0
    urine_charge = 500 if urine_test else 0

    medicine = st.number_input(
        "💊 Medicine Charges (₹)", min_value=0, max_value=15000, value=0
    )

    days = st.number_input(
        "🏥 Hospital Stay (Days)", min_value=0, max_value=30, value=0
    )
    stay_cost = days * 1500

    # ------------------ Calculation ------------------
    subtotal = (
        consultation +
        blood_charge +
        urine_charge +
        medicine +
        stay_cost
    )

    gst = subtotal * 0.05
    total = subtotal + gst

    coverage_percent = patient["coverage"] if patient["coverage"] else 0
    insurance_deduction = (total * float(coverage_percent)) / 100
    final_payable = total - insurance_deduction

    # ------------------ Summary ------------------
    st.subheader("🧾 Bill Summary")

    st.write(f"Subtotal: ₹{subtotal:.2f}")
    st.write(f"GST (5%): ₹{gst:.2f}")
    st.write(f"Total Amount: ₹{total:.2f}")
    st.write(f"Insurance Coverage ({coverage_percent}%): -₹{insurance_deduction:.2f}")
    st.success(f"💰 Final Payable Amount: ₹{final_payable:.2f}")

    # ------------------ Generate & Save ------------------
    if st.button("Generate & Mark as Paid"):

        save_bill_to_db(
            int(patient["id"]),
            total,
            insurance_deduction,
            final_payable
        )

        st.success("✅ Bill Paid & Saved Successfully!")

        st.session_state.bill = {
            "Patient Name": patient["name"],
            "Date": datetime.now().strftime("%d-%m-%Y"),
            "Insurance Policy": patient["insurance_policy"],
            "Policy ID": patient["policy_id"],
            "Consultation": consultation,
            "Blood Test": blood_charge,
            "Urine Test": urine_charge,
            "Medicine": medicine,
            "Hospital Stay": stay_cost,
            "GST": round(gst, 2),
            "Total Amount": round(total, 2),
            "Insurance Deduction": round(insurance_deduction, 2),
            "Final Payable": round(final_payable, 2)
        }

    # ------------------ Display & Download ------------------
    if "bill" in st.session_state:
        st.subheader("✅ Generated Bill")
        st.json(st.session_state.bill)

        pdf_file = generate_bill_pdf(st.session_state.bill)

        st.download_button(
            "⬇️ Download Bill as PDF",
            data=pdf_file,
            file_name=f"Bill_{st.session_state.bill['Patient Name']}.pdf",
            mime="application/pdf"
        )
