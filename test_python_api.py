import pytest
from python_api import app

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
    expected_record = {
        'id': 4,
        'first_name': 'John',
        'last_name': 'Doe',
        'age': 30,
        'blood_type': 'O',
        'allergies': 'none'
    }
    assert response.status_code == 200