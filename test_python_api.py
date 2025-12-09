import pytest
from unittest.mock import patch
from python_api import app

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

def test_add_patient_success():
    client = app.test_client()

    with patch("python_api.insert_into_db") as mock_insert:
        response = client.post("/add_patient", json={
            "first_name": "Peter",
            "last_name": "Petersen",
            "age": 33,
            "blood_type": "A",
            "allergies": "Nuts"
        })

    assert response.status_code == 201
    assert response.json == {"message": "created"}

    # Check DB function called correctly
    mock_insert.assert_called_once_with("Peter", "Petersen", 33, "A", "Nuts")

def test_fetch_patient_found():
    client = app.test_client()

    fake_record = {
        "first_name": "Alice",
        "last_name": "Smith",
        "age": 28,
        "blood_type": "B",
        "allergies": "Dust"
    }

    with patch("python_api.fetch_from_db", return_value=fake_record):
        response = client.get("/fetch_patient/1")

    assert response.status_code == 200
    assert response.json == fake_record