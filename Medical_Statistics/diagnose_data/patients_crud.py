import sqlite3
import pandas as pd
import streamlit as st

@st.cache_data
def load_patients_basic():
    try:
        conn = sqlite3.connect("C:\\Users\\Atharv\\OneDrive\\Desktop\\Medical_Statistics\\patients.db")
        df = pd.read_sql(
            "SELECT id, name, age, gender FROM patients",
            conn
        )
        conn.close()
        return df
    except Exception as e:
        st.error(f"Patient DB error: {e}")
        return pd.DataFrame(columns=["name", "age", "gender"])
    

conn=sqlite3.connect("C:\\Users\\Atharv\\OneDrive\\Desktop\\Medical_Statistics\\patients.db", check_same_thread=False)
cursor=conn.execute("""SELECT patient_id,typeof(patient_id) FROM diagnoses;""")
data=cursor.fetchall()
print(data)