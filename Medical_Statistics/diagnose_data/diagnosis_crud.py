from database import get_connection

conn= get_connection()
cursoor = conn.cursor()
cursoor.execute("")

def save_diagnosis(
    patient_id,
    disease,
    status,
    symptoms,
    expected_recovery_time,
    date_of_diagnosis,
    date_of_recoveryordischarge,
    actual_recovery_time
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO diagnoses (
            patient_id,
            disease,
            status,
            symptoms,
            expected_recovery_time,
            date_of_diagnosis,
            date_of_recoveryordischarge,
            actual_recovery_time
        )
        VALUES (?,?,?,?, ?,?,?,?)
    """, (
        int(patient_id),
        disease,
        status,
        ", ".join(symptoms),
        expected_recovery_time,
        date_of_diagnosis,
        date_of_recoveryordischarge,
        actual_recovery_time
    ))
    conn.commit()
    conn.close()

def add_diagnosis(
    patient_id,
    disease,
    status,
    symptoms,
    expected_recovery_time,
    date_of_diagnosis,
    date_of_recoveryordischarge,
    actual_recovery_time
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO diagnoses (
            patient_id,
            disease,
            status,
            symptoms,
            expected_recovery_time,
            date_of_diagnosis,
            date_of_recoveryordischarge,
            actual_recovery_time
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        int(patient_id),
        disease,
        status,
        symptoms,
        expected_recovery_time,
        date_of_diagnosis,
        date_of_recoveryordischarge,
        actual_recovery_time
    ))

    conn.commit()
    conn.close()

def get_all_diagnoses():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            d.id,
            p.patient_name,
            d.disease,
            d.status,
            d.symptoms,
            d.expected_recovery_time,
            d.date_of_diagnosis,
            d.date_of_recoveryordischarge,
            d.actual_recovery_time
        FROM diagnoses d
        JOIN patients p ON d.patient_id = p.id
        ORDER BY d.date_of_diagnosis DESC
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows

def get_diagnoses_by_patient(patient_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM diagnoses
        WHERE patient_id = ?
        ORDER BY date_of_diagnosis DESC
    """, (patient_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def discharge_patient(diagnosis_id, recovery_date, status="Recovered"):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE diagnoses
        SET
            date_of_recoveryordischarge = ?,
            status = ?,
            actual_recovery_time =
                CAST(
                    julianday(?) - julianday(date_of_diagnosis)
                    AS INTEGER
                )
        WHERE id = ?
    """, (recovery_date, status, recovery_date, diagnosis_id))

    conn.commit()
    conn.close()

def update_diagnosis_status(diagnosis_id, status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE diagnoses
        SET status = ?
        WHERE id = ?
    """, (status, diagnosis_id))

    conn.commit()
    conn.close()

def delete_diagnosis(diagnosis_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM diagnoses WHERE id = ?", (diagnosis_id,))
    conn.commit()
    conn.close()

