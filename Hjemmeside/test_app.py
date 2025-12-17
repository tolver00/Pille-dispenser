import os
import sys
import types
import importlib.util

def _load_app_module(path):
    spec = importlib.util.spec_from_file_location("app", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["app"] = mod
    spec.loader.exec_module(mod)
    return mod

def test_get_db_connection_calls_psycopg_connect():
    # sæt env vars før import
    os.environ["HOST"] = "dbhost"
    os.environ["DB_NAME"] = "mydb"
    os.environ["DB_USER"] = "user1"
    os.environ["DB_PASSWORD"] = "secret"
    os.environ["DB_PORT"] = "5432"

    # fake psycopg for at fange conn-string
    called = {}
    sentinel_conn = object()
    def fake_connect(conn_string):
        called["conn_string"] = conn_string
        return sentinel_conn

    fake_psycopg = types.ModuleType("psycopg")
    fake_psycopg.connect = fake_connect
    sys.modules["psycopg"] = fake_psycopg

    app_path = os.path.join(os.path.dirname(__file__), "app.py")
    app = _load_app_module(app_path)

    conn = app.get_db_connection()
    assert conn is sentinel_conn
    assert called.get("conn_string") == "host=dbhost dbname=mydb user=user1 password=secret port=5432"

    # cleanup
    sys.modules.pop("psycopg", None)
    sys.modules.pop("app", None)