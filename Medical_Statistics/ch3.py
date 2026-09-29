import sqlite3
conn = sqlite3.connect("patients.db")
cursor = conn.cursor()
cursor.execute("""
DROP TABLE billing;""")
conn.commit()
conn.close()