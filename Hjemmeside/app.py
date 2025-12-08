from flask import Flask, render_template
from dotenv import load_dotenv
import os
import psycopg

load_dotenv()

# Database config
HOST = os.getenv("HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")


def get_db_connection():
    conn_string = f"host={HOST} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} port={DB_PORT}"
    return psycopg.connect(conn_string)


def fetch_patient_by_id(patient_id):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, first_name, last_name, age, blood_type, allergies FROM patients WHERE id = %s;",
            (patient_id,)
        )
        records = cur.fetchone()
        
        if records:
            columns = ['id', 'first_name', 'last_name', 'age', 'blood_type', 'allergies']
            return dict(zip(columns, records))
        return None
        
    except Exception as e:
        print(f"Database error: {e}")
        return None
        
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def fetch_all_patients():
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, first_name, last_name, age, blood_type, allergies FROM patients ORDER BY id;")
        records = cur.fetchall()
        
        columns = ['id', 'first_name', 'last_name', 'age', 'blood_type', 'allergies']
        return [dict(zip(columns, row)) for row in records]
        
    except Exception as e:
        print(f"Database error: {e}")
        return []
        
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


app = Flask(__name__, template_folder='templates')


@app.route('/')
def index():
    all_patients = fetch_all_patients()
    return render_template('hovedside.html', patient=None, all_patients=all_patients)


@app.route('/sysinfo')
def sysinfo():
    patient_data = fetch_patient_by_id(1)
    return render_template('sysinfo.html', patient=patient_data)


@app.route('/patients')
def patients_list():
    all_patients = fetch_all_patients()
    return render_template('patients.html', patients=all_patients, all_patients=all_patients)


@app.route('/patient/<int:patient_id>')
def patient_detail(patient_id):
    patient_data = fetch_patient_by_id(patient_id)
    all_patients = fetch_all_patients()
    
    if patient_data:
        return render_template('hovedside.html', patient=patient_data, all_patients=all_patients)
    return "Patient not found", 404


if __name__ == '__main__':
    app.run(debug=True)