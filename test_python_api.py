import pytest
from python_api import app fetch_from_db

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

def test_insert_into_db(client):
    response = client.post(
        "/add_patient",
        json={
            "first_name": "test",
            "last_name": "test",
            "age": 33,
            "blood_type": "a",
            "allergies": "none"
        }
    )
    assert response.status_code == 201
    assert response.json["message"] == "created"

def test_fetch_from_db(client):
    patient_id = 4
    result_of_function = fetch_from_db(patient_id)
    assert result_of_function is not None