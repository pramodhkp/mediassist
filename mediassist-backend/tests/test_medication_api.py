import pytest
import json
from datetime import datetime, timedelta
import mongoengine
from mongoengine import connect, disconnect
from mongomock import MongoClient

# Add the mediassist-backend directory to the Python path for imports
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.app import app as flask_app # The Flask app instance
from storage.models import Medication # The Medication model

@pytest.fixture(scope="function")
def client():
    """Configures the Flask app for testing and yields a test client."""
    flask_app.config['TESTING'] = True
    # Establish a connection to mongomock BEFORE the app context is used by requests
    disconnect(alias='default') # Disconnect any previous real connection
    connect('test_api_db', mongo_client_class=MongoClient, alias='default')

    with flask_app.test_client() as client:
        yield client

    # Teardown: Clean up the mock database
    # mongoengine.get_db(alias='default').client.drop_database('test_api_db') # For real pymongo
    disconnect(alias='default')


@pytest.fixture(scope="function", autouse=True)
def clean_medication_collection():
    """Ensure Medication collection is empty before each test in this file."""
    Medication.objects.delete() # Deletes all Medication objects
    yield
    Medication.objects.delete()


class TestMedicationAPI:

    def test_add_medication_success(self, client):
        """Test POST /api/medications with valid data."""
        payload = {
            "user_id": "api_user_1",
            "medication_name": "TestMed API",
            "dosage": "10mg",
            "frequency": "daily",
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "reminder_times": ["08:00", "20:00"],
            "notes": "Take with water"
        }
        response = client.post('/api/medications', json=payload)
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == "Medication added successfully"
        assert 'medication' in data
        assert data['medication']['medication_name'] == "TestMed API"
        assert data['medication']['user_id'] == "api_user_1"
        assert Medication.objects(user_id="api_user_1").count() == 1

    def test_add_medication_missing_required_field(self, client):
        """Test POST /api/medications with missing medication_name."""
        payload = {
            "user_id": "api_user_2",
            # "medication_name": "Missing Name Med", # Missing
            "start_date": "2024-02-01"
        }
        response = client.post('/api/medications', json=payload)
        assert response.status_code == 400
        data = response.get_json()
        assert "Missing required fields" in data['error']
        assert "medication_name" in data['error']

    def test_add_medication_invalid_date_format(self, client):
        """Test POST /api/medications with invalid date format."""
        payload = {
            "user_id": "api_user_3",
            "medication_name": "Bad Date Med",
            "start_date": "01/03/2024" # Invalid format, expecting YYYY-MM-DD
        }
        response = client.post('/api/medications', json=payload)
        assert response.status_code == 400
        data = response.get_json()
        assert "Invalid start_date format" in data['error']

    def test_add_medication_invalid_reminder_time_format(self, client):
        """Test POST /api/medications with invalid reminder time format."""
        payload = {
            "user_id": "api_user_4",
            "medication_name": "Bad Time Med",
            "start_date": "2024-03-01",
            "reminder_times": ["08:00", "25:00"] # Invalid time
        }
        response = client.post('/api/medications', json=payload)
        assert response.status_code == 400
        data = response.get_json()
        assert "Invalid time format in reminder_times" in data['error']

    def test_add_medication_end_date_before_start_date(self, client):
        """Test POST /api/medications with end_date before start_date."""
        payload = {
            "user_id": "api_user_5",
            "medication_name": "Date Order Med",
            "start_date": "2024-03-10",
            "end_date": "2024-03-01" # end_date before start_date
        }
        response = client.post('/api/medications', json=payload)
        assert response.status_code == 400
        data = response.get_json()
        assert "end_date cannot be before start_date" in data['error']


    def test_list_medications_for_user(self, client):
        """Test GET /api/medications/<user_id> for a user with medications."""
        Medication(user_id="list_user_1", medication_name="Med1", start_date=datetime(2024,1,1)).save()
        Medication(user_id="list_user_1", medication_name="Med2", start_date=datetime(2024,1,5)).save()
        
        response = client.get('/api/medications/list_user_1')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 2
        med_names = sorted([m['medication_name'] for m in data])
        assert med_names == ["Med1", "Med2"]

    def test_list_medications_for_user_no_medications(self, client):
        """Test GET /api/medications/<user_id> for a user with no medications."""
        response = client.get('/api/medications/list_user_no_meds')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0
        
    def test_update_medication_success(self, client):
        """Test PUT /api/medications/<medication_id> with valid data."""
        med = Medication(user_id="update_user_1", medication_name="InitialName", start_date=datetime(2024,4,1), dosage="5mg").save()
        med_id = str(med.id)
        
        update_payload = {
            "medication_name": "UpdatedName",
            "dosage": "10mg",
            "notes": "Updated notes"
        }
        response = client.put(f'/api/medications/{med_id}', json=update_payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Medication updated successfully"
        assert data['medication']['medication_name'] == "UpdatedName"
        assert data['medication']['dosage'] == "10mg"
        assert data['medication']['notes'] == "Updated notes"

        updated_med_db = Medication.objects(id=med_id).first()
        assert updated_med_db.medication_name == "UpdatedName"
        assert updated_med_db.dosage == "10mg"

    def test_update_medication_not_found(self, client):
        """Test PUT /api/medications/<medication_id> for a non-existent medication."""
        non_existent_id = "60c72b2f9b1e8b3b2c8d5e6f" # Example of a valid ObjectId format but non-existent
        response = client.put(f'/api/medications/{non_existent_id}', json={"notes": "Test"})
        assert response.status_code == 404 # Assuming your API returns 404
        data = response.get_json()
        assert "Medication not found" in data['error']

    def test_update_medication_invalid_data(self, client):
        """Test PUT /api/medications/<medication_id> with invalid data (e.g. bad date)."""
        med = Medication(user_id="update_user_2", medication_name="BadUpdateMed", start_date=datetime(2024,5,1)).save()
        med_id = str(med.id)
        
        update_payload = {"start_date": "invalid-date-format"}
        response = client.put(f'/api/medications/{med_id}', json=update_payload)
        assert response.status_code == 400
        data = response.get_json()
        assert "Invalid start_date format" in data['error']


    def test_delete_medication_success(self, client):
        """Test DELETE /api/medications/<medication_id> for an existing medication."""
        med = Medication(user_id="delete_user_1", medication_name="ToDelete", start_date=datetime(2024,6,1)).save()
        med_id = str(med.id)
        
        assert Medication.objects(id=med_id).count() == 1
        response = client.delete(f'/api/medications/{med_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Medication deleted successfully"
        assert Medication.objects(id=med_id).count() == 0

    def test_delete_medication_not_found(self, client):
        """Test DELETE /api/medications/<medication_id> for a non-existent medication."""
        non_existent_id = "60c72b2f9b1e8b3b2c8d5e60"
        response = client.delete(f'/api/medications/{non_existent_id}')
        assert response.status_code == 404
        data = response.get_json()
        assert "Medication not found" in data['error']


    def test_get_due_medications(self, client):
        """Test GET /api/medications/due/<user_id>."""
        user_id_due = "due_user_1"
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        current_time_str = now.strftime("%H:%M")
        
        # Medication due now
        Medication(
            user_id=user_id_due, medication_name="DueNowMed", 
            start_date=now - timedelta(days=1), 
            reminder_times=[current_time_str, (now + timedelta(hours=2)).strftime("%H:%M")]
        ).save()
        
        # Medication not due (reminder time passed)
        Medication(
            user_id=user_id_due, medication_name="DuePassedMed", 
            start_date=now - timedelta(days=1), 
            reminder_times=[(now - timedelta(hours=1)).strftime("%H:%M")]
        ).save()

        # Medication not due (starts tomorrow)
        Medication(
            user_id=user_id_due, medication_name="StartsTomorrowMed", 
            start_date=now + timedelta(days=1), 
            reminder_times=[current_time_str]
        ).save()
        
        # Medication due (no end date)
        Medication(
            user_id=user_id_due, medication_name="DueNoEnd", 
            start_date=now - timedelta(days=5), 
            reminder_times=[current_time_str]
        ).save()

        # Medication ended yesterday
        Medication(
            user_id=user_id_due, medication_name="EndedYesterdayMed", 
            start_date=now - timedelta(days=5), 
            end_date=now - timedelta(days=1),
            reminder_times=[current_time_str]
        ).save()

        # Medication with no reminder times
        Medication(
            user_id=user_id_due, medication_name="NoRemindersMed", 
            start_date=now - timedelta(days=1), 
            reminder_times=[]
        ).save()

        response = client.get(f'/api/medications/due/{user_id_due}')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        
        # This is tricky because the `get_due_medications` endpoint in medication_handler.py
        # doesn't filter by current time, only by date and presence of reminder_times.
        # The subtask description for the API endpoint says:
        # "The subtask simplifies the "due" logic: for now, it's not about matching current time with reminder_times, 
        # but just filtering by date range and presence of reminders."
        # So, we expect medications that are active today and have reminders.
        
        due_med_names = sorted([m['medication_name'] for m in data])
        
        # Expected based on simplified logic (active today and has reminders):
        # - DueNowMed (active, has reminders)
        # - DuePassedMed (active, has reminders)
        # - DueNoEnd (active, has reminders)
        # Not expected:
        # - StartsTomorrowMed (not active yet)
        # - EndedYesterdayMed (not active anymore)
        # - NoRemindersMed (does not have reminders)
        
        # If the API logic was more precise about time:
        # We would only expect "DueNowMed" and "DueNoEnd" if current_time_str matches.
        # But the API's GET /due endpoint is simpler.
        # The test must match the actual implementation of the /due endpoint.
        # The current implementation of `/medications/due/<user_id>`:
        # query_params = {
        #     "user_id": user_id,
        #     "reminder_times__exists": True, 
        #     "reminder_times__ne": [],       
        #     "start_date__lte": datetime.combine(today, datetime.min.time()) 
        # }
        # Then iterates and checks `med.end_date.date() >= today` if `med.end_date` exists.

        # Based on THIS logic, the expected medications are:
        # DueNowMed (active, has reminders)
        # DuePassedMed (active, has reminders)
        # DueNoEnd (active, has reminders)
        expected_due_meds = ["DueNowMed", "DueNoEnd", "DuePassedMed"]
        assert sorted(due_med_names) == sorted(expected_due_meds)
        assert len(data) == 3

```
