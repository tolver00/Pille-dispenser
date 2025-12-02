import os
import psutil
import psycopg
import time
from dotenv import load_dotenv
load_dotenv()


HOST=       os.getenv('HOST') 
DB_NAME=    os.getenv('DB_NAME') 
DB_USER=    os.getenv('DB_USER') 
DB_PASSWORD=os.getenv('DB_PASSWORD')


def resource_utilization():
    try:
        current_time = time.time()
#        while True:
        cpu_usage = psutil.cpu_percent(interval=1)
        mem_usage = psutil.virtual_memory().percent
        free_disk = psutil.disk_usage('/').percent
#        users = psutil.users()
        pids = len(psutil.pids())
        boot_time = psutil.boot_time()
        uptime_seconds = current_time - boot_time
        uptime_hours = uptime_seconds / 3600
        time.sleep(1)
#        print(f"CPU Percent:    {cpu_usage}\nMEM Usage:     {mem_usage}\nDISK Partitions:       {disk_drives}\nDISK Utilization:      {free_disk}\n")
        return cpu_usage, mem_usage, free_disk, pids, uptime_hours
    except Exception as e:
        print(f"Error encountered {e}")


def create_sys_info_table():
    try:
        conn_string = f"host={HOST} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"
        conn = psycopg.connect(conn_string)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("""
                CREATE TABLE system_stats (
                    id SERIAL PRIMARY KEY,
                    cpu_usage NUMERIC(5,2),
                    mem_usage NUMERIC(5,2),
                    free_disk NUMERIC(5,2),
                    pids INTEGER,
                    uptime_hours NUMERIC(10,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("Table 'system_info' Created.")
    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

# create_sys_info_table()

def insert_sys_info(cpu_usage, mem_usage, free_disk, pids, uptime_hours):
    conn = None
    cur = None
    try:
        conn_string = f"host={HOST} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"
        sql_string = """
        INSERT INTO system_stats
            (cpu_usage, mem_usage, free_disk, pids, uptime_hours)
        VALUES (%s, %s, %s, %s, %s);
        """
        conn = psycopg.connect(conn_string)
        cur = conn.cursor()
        cur.execute(sql_string, (cpu_usage, mem_usage, free_disk, pids, uptime_hours))
        conn.commit()
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()


while True:
    cpu_usage, mem_usage, free_disk, pids, uptime_hours = resource_utilization()
    insert_sys_info(cpu_usage, mem_usage, free_disk, pids, uptime_hours)
    time.sleep(5)