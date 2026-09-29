import sqlite3
import pandas as pd
import os

DB_PATH = "C:\\Users\\Atharv\\OneDrive\\Desktop\\Medical_Statistics\\patients.db"
CSV_PATH = "C:\\Users\\Atharv\\OneDrive\\Desktop\\Medical_Statistics\\recovery_time.csv"
def export_recover_time(diagnosis_id):
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT 
            d.disease AS "Disease",
            d.expected_recovery_time AS "Expected Recovery Time",
            d.actual_recovery_time AS "Actual Recovery Time"
        FROM diagnoses d
        WHERE d.id = ?
        AND d.status = 'Recovered'
        AND d.actual_recovery_time IS NOT NULL
    """

    new_df = pd.read_sql(query, conn, params=(int(diagnosis_id),))
    conn.close()

    if new_df.empty:
        return

    if os.path.exists(CSV_PATH):
        new_df.to_csv(CSV_PATH, mode="a", header=False, index=False)
    else:
        new_df.to_csv(CSV_PATH, index=False)

    print("Row appended successfully ✅")
