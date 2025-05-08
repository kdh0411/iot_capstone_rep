# DB/init_db.py
import os
import sqlite3

def init_sensor_db(db_path='DB/sensor_data.db'):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            A REAL,
            G REAL,
            N1 REAL,
            N2 REAL,
            M INTEGER,
            T REAL,
            L1 REAL,
            L2 REAL
        )
    """)

    conn.commit()
    conn.close()
    print("[✅] sensor_data.db 초기화 완료")

if __name__ == "__main__":
    init_sensor_db()
