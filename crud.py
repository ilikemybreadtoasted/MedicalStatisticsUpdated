import pandas as pd
from database import get_connection

# ---------- PATIENTS ----------
def add_patient(data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO patients (name, age, gender, status, phone, admission)
        VALUES (?, ?, ?, ?, ?, ?)
    """, tuple(data.values()))

    conn.commit()
    conn.close()

def get_patients():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM patients", conn)
    conn.close()
    return df

# ---------- DIAGNOSIS ----------
def add_diagnosis(data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO diagnoses (patient_id, disease, severity, confidence, date)
        VALUES (?, ?, ?, ?, ?)
    """, tuple(data.values()))

    conn.commit()
    conn.close()

def get_diagnoses():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM diagnoses", conn)
    conn.close()
    return df
