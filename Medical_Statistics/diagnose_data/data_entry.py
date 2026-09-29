import sqlite3 
import pandas as pd 
import os 
DB_PATH = "C:\\Users\\Atharv\\OneDrive\\Desktop\\Medical_Statistics\\patients.db" 
CSV_PATH = "C:\\Users\\Atharv\\OneDrive\\Desktop\\Medical_Statistics\\disease_data.csv" 

def export_all_recoveries(diagnosis_id): 
    conn = sqlite3.connect(DB_PATH) 
    query = """ SELECT p.age, p.gender, d.disease, d.actual_recovery_time AS recovery_time FROM diagnoses d 
    JOIN patients p ON d.patient_id = p.id WHERE d.id = ? AND d.status = 'Recovered' AND d.actual_recovery_time IS NOT NULL """ 
    new_df = pd.read_sql(query, conn, params=(int(diagnosis_id),)) 
    conn.close() 
    if new_df.empty: 
        return 
    # Force correct column order 
    new_df = new_df[["age", "gender", "disease", "recovery_time"]] # Append only — DO NOT read existing CSV 
    new_df.to_csv( CSV_PATH, mode='a', header=not os.path.exists(CSV_PATH), index=False ) 
    print("Row appended successfully ✅") 