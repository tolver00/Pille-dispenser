import os
from apiflask import APIFlask, Schema
from apiflask.fields import Integer, String, DateTime
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
from flask import request

load_dotenv()


# VARS
HOST =          os.getenv("HOST") 
DB_NAME =       os.getenv("DB_NAME") 
DB_USER =       os.getenv("DB_USER") 
DB_PASSWORD =   os.getenv("DB_PASSWORD")

# Create initial table if not exists
def create_patients_table():
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


def create_timestamp_table():
    try:
        conn_string = f"host={HOST} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"
        conn = psycopg.connect(conn_string)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS patient_records (
                id SERIAL PRIMARY KEY,

                device_id   TEXT       NOT NULL,
                patient_id  INTEGER    NOT NULL,
                start_date  TIMESTAMP  NOT NULL,
                end_date    TIMESTAMP  NOT NULL,
                timestamps  TEXT    NOT NULL,
                pill_count  INTEGER NOT NULL,

                CONSTRAINT fk_patient
                    FOREIGN KEY (patient_id)
                    REFERENCES patients(id)
                    ON DELETE CASCADE
            );
        """)
        print("Table 'timestamps' Created.")
    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()


# Fetch row/rows from patients table
def fetch_from_db(patient_id):
    conn = None
    cur = None
    try:
        conn_string = f"host={HOST} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"
        conn = psycopg.connect(conn_string)
        cur = conn.cursor(row_factory=dict_row)
        cur.execute("CALL get_patient(%s, %s);", (patient_id, None))
        cur.execute("FETCH ALL FROM patient_cursor;")
        records = cur.fetchone()
        return records
    except Exception as e:
        print(f"database error: {e}")
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()


def fetch_patient_records(patient_id):
    conn = None
    cur = None
    try:
        conn_string = f"host={HOST} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"
        conn = psycopg.connect(conn_string)
        cur = conn.cursor(row_factory=dict_row)
        cur.execute("CALL get_patient_with_records(%s, %s);", (patient_id, None))
        cur.execute("FETCH ALL FROM patient_records_cursor;")
        record = cur.fetchone()
        return record
    except Exception as e:
        print(f"database error: {e}")
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

# Insert into patients table
def insert_into_db(first_name, last_name, age, blood_type, allergies):
    conn = None
    cur = None
    try:
        conn_string = f"host={HOST} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"
        sql_string = "CALL add_patient(%s, %s, %s, %s, %s, %s)"
        conn = psycopg.connect(conn_string)
        cur = conn.cursor()
        cur.execute(sql_string, (first_name, last_name, age, blood_type, allergies, None))
        conn.commit()
    except Exception as e:
        print(f"database error: {e}")
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()


def update_heartbeat(device_id):
    conn = None
    cur = None
    try:
        conn_string = f"host={HOST} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"
        conn = psycopg.connect(conn_string)
        cur = conn.cursor()
        cur.execute("CALL update_device_heartbeat(%s);", (device_id,))
        conn.commit()
    except Exception as e:
        print(f"database error: {e}")
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

# Class for inserting patient data
class PatientIn(Schema):
    first_name = String(required=True)
    last_name = String(required=True)
    age = Integer(required=True)
    blood_type = String(required=True)
    allergies = String(required=True)

# Class for fetching patient
class PatientOut(Schema):
    first_name = String(required=True)
    last_name = String(required=True)
    age = Integer(required=True)
    blood_type = String(required=True)
    allergies = String(required=True)

# class for fetching patient timestamps
class PatientRecordOut(Schema):
    device_id = String(required=True)
    patient_id = Integer(required=True)
    start_date = DateTime(required=True)
    end_date = DateTime(required=True)
    timestamps = String(required=True)
    pill_count = Integer(required=True)

# APIFlask setup
app = APIFlask(__name__)

@app.post('/add_patient')
@app.input(PatientIn)
def add_new_patient(json_data):
    insert_into_db(json_data["first_name"], json_data["last_name"], json_data["age"], json_data["blood_type"], json_data["allergies"])
    return {'message': 'created'}, 201

@app.get('/fetch_patient/<int:patient_id>')
@app.output(PatientOut)
def get_patient_info(patient_id):
    record = fetch_from_db(patient_id)
    if record:
        return dict(record)
    else:
        return {'message': 'not found'}, 404
    
@app.get('/fetch_patient_timestamps/<int:patient_id>')
@app.output(PatientRecordOut)
def get_patient_record(patient_id):
    record = fetch_patient_records(patient_id)
    if record:
        return dict(record)
    else:
        return {'message': 'not found'}, 404

@app.post("/device/heartbeat/<string:device_id>")
def device_heartbeat(device_id):
    update_heartbeat(device_id)
    return {"device_id": device_id, "ok": True}, 200

    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=41000)