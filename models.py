from database import get_connection

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        gender TEXT,
        status TEXT,
        phone TEXT,
        admission DATE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS diagnoses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        disease TEXT,
        severity TEXT,
        confidence INTEGER,
        date DATE
    )
    """)

    conn.commit()
    conn.close()
