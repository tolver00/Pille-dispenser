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

assert HOST is not None, "HOST environment variable is not set"
assert DB_NAME is not None, "DB_NAME environment variable is not set"
assert DB_USER is not None, "DB_USER environment variable is not set"
assert DB_PASSWORD is not None, "DB_PASSWORD environment variable is not set"
assert DB_PORT is not None, "DB_PORT environment variable is not set"


def get_db_connection():
    conn_string = f"host={HOST} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} port={DB_PORT}"
    conn = psycopg.connect(conn_string)
    assert conn is not None, "Database connection failed"
    return conn


def fetch_patient_by_id(patient_id):
    assert isinstance(patient_id, int), "patient_id must be an integer"
    assert patient_id > 0, "patient_id must be positive"
    
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        assert cur is not None, "Failed to create cursor"
        
        cur.execute(
            "SELECT id, first_name, last_name, age, blood_type, allergies FROM patients WHERE id = %s;",
            (patient_id,)
        )
        records = cur.fetchone()
        
        if records:
            assert len(records) == 6, "Expected 6 columns in patient record"
            columns = ['id', 'first_name', 'last_name', 'age', 'blood_type', 'allergies']
            patient_dict = dict(zip(columns, records))
            
            assert 'id' in patient_dict, "Patient record missing 'id'"
            assert 'first_name' in patient_dict, "Patient record missing 'first_name'"
            assert 'last_name' in patient_dict, "Patient record missing 'last_name'"
            
            return patient_dict
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
        assert cur is not None, "Failed to create cursor"
        
        cur.execute("SELECT id, first_name, last_name, age, blood_type, allergies FROM patients ORDER BY id;")
        records = cur.fetchall()
        
        assert isinstance(records, list), "Expected list of records"
        
        columns = ['id', 'first_name', 'last_name', 'age', 'blood_type', 'allergies']
        patients = [dict(zip(columns, row)) for row in records]
        
        for patient in patients:
            assert len(patient) == 6, f"Patient record has incorrect number of fields: {len(patient)}"
            assert 'id' in patient, "Patient record missing 'id'"
        
        return patients
        
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
    assert isinstance(all_patients, list), "all_patients must be a list"
    return render_template('hovedside.html', patient=None, all_patients=all_patients)


@app.route('/sysinfo')
def sysinfo():
    patient_data = fetch_patient_by_id(1)
    
    return render_template('sysinfo.html', patient=patient_data)


@app.route('/patients')
def patients_list():
    all_patients = fetch_all_patients()
    assert isinstance(all_patients, list), "all_patients must be a list"
    return render_template('patients.html', patients=all_patients, all_patients=all_patients)


@app.route('/patient/<int:patient_id>')
def patient_detail(patient_id):
    assert isinstance(patient_id, int), "patient_id must be an integer"
    assert patient_id > 0, "patient_id must be positive"
    
    patient_data = fetch_patient_by_id(patient_id)
    all_patients = fetch_all_patients()
    
    assert isinstance(all_patients, list), "all_patients must be a list"
    
    if patient_data:
        assert isinstance(patient_data, dict), "patient_data must be a dictionary"
        return render_template('hovedside.html', patient=patient_data, all_patients=all_patients)
    return "Patient not found", 404


if __name__ == '__main__':
    app.run(debug=True)