# DB/db_insert.py
import sqlite3

def insert_sensor_data(data, db_path='DB/sensor_data.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO sensor_data (
            A, G, N1, N2, M, T, L1, L2
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['A'],
        data['G'],
        data['N'][0], data['N'][1],
        data['M'],
        data['T'],
        data['L'][0], data['L'][1]
    ))

    conn.commit()
    conn.close()
