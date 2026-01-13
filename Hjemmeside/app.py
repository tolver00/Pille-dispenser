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
        
        result = []
        for row in records:
            row_dict = {}
            columns = ['id', 'first_name', 'last_name', 'age', 'blood_type', 'allergies']

            for i in range(len(columns)):
                column_name = columns[i]
                row_dict[column_name] = row[i]

            result.append(row_dict)

        return result
        
    except Exception as e:
        print(f"Database error: {e}")
        return []
        
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def fetch_docker_by_id(docker_id):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """SELECT time_epoch, container_name, container_status, cpu_usage, ram_usage_bytes, uptime_hours, 
                rx_packets, rx_dropped, rx_errors, tx_packets, tx_dropped, tx_errors
               FROM docker_logs WHERE container_name = %s;""",
            (docker_id,)
        )
        records = cur.fetchone()
        
        if records:
            columns = ['time_epoch', 'container_name', 'container_status', 'cpu_usage', 'ram_usage_bytes', 'uptime_hours',
                      'rx_packets', 'rx_dropped', 'rx_errors', 'tx_packets', 'tx_dropped', 'tx_errors']
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


def fetch_docker_by_name(container_name):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """SELECT time_epoch, container_name, container_status, cpu_usage, ram_usage_bytes, uptime_hours, 
                rx_packets, rx_dropped, rx_errors, tx_packets, tx_dropped, tx_errors
               FROM docker_logs
               WHERE container_name = %s
               ORDER BY time_epoch DESC
               LIMIT 1;""",
            (container_name,)
        )
        records = cur.fetchone()
        
        if records:
            columns = ['time_epoch', 'container_name', 'container_status', 'cpu_usage', 'ram_usage_bytes', 'uptime_hours',
                      'rx_packets', 'rx_dropped', 'rx_errors', 'tx_packets', 'tx_dropped', 'tx_errors']
            row = dict(zip(columns, records))
            row['name'] = row['container_name']
            return row
        return None
        
    except Exception as e:
        print(f"Database error: {e}")
        return None
        
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def fetch_all_dockers():
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""SELECT DISTINCT container_name FROM docker_logs ORDER BY container_name;""")
        records = cur.fetchall()
        
        result = []
        for row in records:
            result.append({'name': row[0]})

        return result
        
    except Exception as e:
        print(f"Database error: {e}")
        return []
        
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

app = Flask(__name__, template_folder='/etc/nginx/templates')


@app.route('/')
def index():
    all_patients = fetch_all_patients()
    return render_template('hovedside.html', patient=None, all_patients=all_patients)


@app.route('/sysinfo')
def sysinfo():
    all_dockers = fetch_all_dockers()
    return render_template('sysinfo.html', docker=None, all_dockers=all_dockers, sysinfo=None)

@app.route('/sysinfo/<docker_name>')
def sysinfo_detail(docker_name):
    docker_data = fetch_docker_by_name(docker_name)
    all_dockers = fetch_all_dockers()
    
    if docker_data:
        return render_template('sysinfo.html', docker=docker_data, all_dockers=all_dockers, sysinfo=docker_data)
    return "Docker not found", 404


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
    app.run(host='0.0.0.0', port=5000)