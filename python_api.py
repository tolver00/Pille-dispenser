import os
from apiflask import APIFlask, Schema
from apiflask.fields import Integer, String, DateTime
import psycopg2
from psycopg2 import extras
from dotenv import load_dotenv

load_dotenv()


# VARS
HOST =          os.getenv("HOST") 
DB_NAME =       os.getenv("DB_NAME") 
DB_USER =       os.getenv("DB_USER") 
DB_PASSWORD =   os.getenv("DB_PASSWORD")


def create_patients_table():
    try:
        conn_string = f"host={HOST} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"
        conn = psycopg2.connect(conn_string)
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
 
# create_patients_table()

def fetch_from_db():
    conn = None
    cur = None
    try:
        conn_string = f"host={HOST} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"
        conn = psycopg2.connect(conn_string)
        cur = conn.cursor()
        cur.execute("SELECT * FROM patients;")
        records = cur.fetchall()
        return records
    except Exception as e:
        print(f"database error: {e}")
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

print(fetch_from_db())

def insert_into_db(first_name, last_name, age, blood_type, allergies):
    conn = None
    cur = None
    try:
        conn_string = f"host={HOST} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"
        sql_string = ("""
            INSERT INTO patients (first_name, last_name, age, blood_type, allergies)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
                    """)
        conn = psycopg2.connect(conn_string)
        cur = conn.cursor()
        cur.execute(sql_string, (first_name, last_name, age, blood_type, allergies))
        conn.commit()
    except Exception as e:
        print(f"database error: {e}")
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

# insert_into_db("lars", "larsen", 22, "a", "different allergy")


""" app = APIFlask(__name__)
class Patient(Schema):
    first_name = String(required=True)
    last_name = String(required=True)
    age = Column 
    blood_type = String(required=True)
    allergies = String(required=True)

@app.post('/add_patient')
@app.input(PatientIn)
def add_new_patient(json_data):
    return {'message': 'created'}, 201

@app.get('/health_data')
def get_health_data():
    return 
 """