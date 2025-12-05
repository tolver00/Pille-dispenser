from flask import Flask, render_template
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import numpy as np
from dotenv import load_dotenv
import os
import psycopg

load_dotenv()


# VARS
HOST =          os.getenv("HOST") 
DB_NAME =       os.getenv("DB_NAME") 
DB_USER =       os.getenv("DB_USER") 
DB_PASSWORD =   os.getenv("DB_PASSWORD")
DB_PORT =       os.getenv("DB_PORT")

def create_patients_table():
    cur = None
    conn = None
    try:
        conn_string = f"host={HOST} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"
        conn = psycopg.connect(conn_string)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                age INTEGER,
                blood_type VARCHAR(10) NOT NULL,
                allergies TEXT NOT NULL
            );
        """)
        print("Table 'patients' Created.")
    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

#create_patients_table()

def fetch_from_db(patient_id):
    conn = None
    cur = None
    try:
        conn_string = f"host={HOST} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} port={DB_PORT}"
        conn = psycopg.connect(conn_string)
        cur = conn.cursor()
        cur.execute("CALL get_patient(%s);", (patient_id))
        #cur.execute("FETCH ALL FROM patient_cursor;")
        records = cur.fetchone()
        print("fetch db:  ",records)
        return records
    except Exception as e:
        print(f"database error: {e}")
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()


get_patient_proc_sql = """DROP PROCEDURE IF EXISTS get_patient;

CREATE OR REPLACE PROCEDURE get_patient(
    IN p_id INTEGER,
    INOUT p_cursor REFCURSOR
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_cursor IS NULL THEN
        p_cursor := 'patient_cursor';
    END IF;

    OPEN p_cursor FOR
        SELECT id AS patient_id,
               first_name,
               last_name
        FROM patients
        WHERE id = p_id;
END;
$$;
"""

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    patient_data = fetch_from_db(1)
    print("patient data:  ",patient_data)
    return render_template('hovedside.html', patient=patient_data)


@app.route('/sysinfo')
def sysinfo():
	patient_data = fetch_from_db(1)
	return render_template('sysinfo.html', patient=patient_data)

if __name__ == '__main__':
	app.run(debug=True)
