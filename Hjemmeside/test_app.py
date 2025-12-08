import pytest
from unittest.mock import patch, MagicMock
from app import app, get_db_connection, fetch_patient_by_id, fetch_all_patients


@pytest.fixture
def client():
    """Flask test client fixture"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_db_connection():
    """Mock database connection"""
    with patch('app.get_db_connection') as mock_conn:
        yield mock_conn


class TestDatabaseFunctions:
    """Test database interaction functions"""
    
    def test_fetch_patient_by_id_success(self, mock_db_connection):
        """Test fetching a patient successfully"""
        # Setup mock
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1, 'John', 'Doe', 30, 'A+', 'None')
        
        # Execute
        result = fetch_patient_by_id(1)
        
        # Assert
        assert result is not None
        assert result['id'] == 1
        assert result['first_name'] == 'John'
        assert result['last_name'] == 'Doe'
        assert result['age'] == 30
        assert result['blood_type'] == 'A+'
        assert result['allergies'] == 'None'
        
        # Verify cursor was closed
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    def test_fetch_patient_by_id_not_found(self, mock_db_connection):
        """Test fetching a non-existent patient"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        result = fetch_patient_by_id(999)
        
        assert result is None
    
    def test_fetch_patient_by_id_database_error(self, mock_db_connection):
        """Test database error handling"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database error")
        
        result = fetch_patient_by_id(1)
        
        assert result is None
    
    def test_fetch_all_patients_success(self, mock_db_connection):
        """Test fetching all patients successfully"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, 'John', 'Doe', 30, 'A+', 'None'),
            (2, 'Jane', 'Smith', 25, 'B-', 'Penicillin')
        ]
        
        result = fetch_all_patients()
        
        assert len(result) == 2
        assert result[0]['first_name'] == 'John'
        assert result[1]['first_name'] == 'Jane'
    
    def test_fetch_all_patients_empty(self, mock_db_connection):
        """Test fetching patients when database is empty"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        
        result = fetch_all_patients()
        
        assert result == []
    
    def test_fetch_all_patients_database_error(self, mock_db_connection):
        """Test database error when fetching all patients"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Connection lost")
        
        result = fetch_all_patients()
        
        assert result == []


class TestRoutes:
    """Test Flask routes"""
    
    @patch('app.fetch_all_patients')
    def test_index_route(self, mock_fetch_all, client):
        """Test the index route"""
        mock_fetch_all.return_value = [
            {'id': 1, 'first_name': 'John', 'last_name': 'Doe', 'age': 30, 'blood_type': 'A+', 'allergies': 'None'}
        ]
        
        response = client.get('/')
        
        assert response.status_code == 200
        mock_fetch_all.assert_called_once()
    
    @patch('app.fetch_patient_by_id')
    def test_sysinfo_route(self, mock_fetch_patient, client):
        """Test the sysinfo route"""
        mock_fetch_patient.return_value = {
            'id': 1, 'first_name': 'John', 'last_name': 'Doe', 
            'age': 30, 'blood_type': 'A+', 'allergies': 'None'
        }
        
        response = client.get('/sysinfo')
        
        assert response.status_code == 200
        mock_fetch_patient.assert_called_once_with(1)
    
    @patch('app.fetch_all_patients')
    def test_patients_list_route(self, mock_fetch_all, client):
        """Test the patients list route"""
        mock_fetch_all.return_value = [
            {'id': 1, 'first_name': 'John', 'last_name': 'Doe', 'age': 30, 'blood_type': 'A+', 'allergies': 'None'},
            {'id': 2, 'first_name': 'Jane', 'last_name': 'Smith', 'age': 25, 'blood_type': 'B-', 'allergies': 'Penicillin'}
        ]
        
        response = client.get('/patients')
        
        assert response.status_code == 200
        mock_fetch_all.assert_called_once()
    
    @patch('app.fetch_all_patients')
    @patch('app.fetch_patient_by_id')
    def test_patient_detail_route_success(self, mock_fetch_patient, mock_fetch_all, client):
        """Test patient detail route with valid patient"""
        mock_fetch_patient.return_value = {
            'id': 1, 'first_name': 'John', 'last_name': 'Doe', 
            'age': 30, 'blood_type': 'A+', 'allergies': 'None'
        }
        mock_fetch_all.return_value = []
        
        response = client.get('/patient/1')
        
        assert response.status_code == 200
        mock_fetch_patient.assert_called_once_with(1)
    
    @patch('app.fetch_all_patients')
    @patch('app.fetch_patient_by_id')
    def test_patient_detail_route_not_found(self, mock_fetch_patient, mock_fetch_all, client):
        """Test patient detail route with non-existent patient"""
        mock_fetch_patient.return_value = None
        mock_fetch_all.return_value = []
        
        response = client.get('/patient/999')
        
        assert response.status_code == 404
        assert b"Patient not found" in response.data


class TestEdgeCases:
    """Test edge cases and error scenarios"""
    
    def test_fetch_patient_with_null_allergies(self, mock_db_connection):
        """Test patient with NULL allergies field"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1, 'John', 'Doe', 30, 'A+', None)
        
        result = fetch_patient_by_id(1)
        
        assert result is not None
        assert result['allergies'] is None
    
    def test_fetch_patient_with_special_characters(self, mock_db_connection):
        """Test patient name with special characters"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1, "O'Brien", 'José-María', 30, 'A+', 'None')
        
        result = fetch_patient_by_id(1)
        
        assert result['first_name'] == "O'Brien"
        assert result['last_name'] == 'José-María'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])