import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta, time

# Add the mediassist-backend directory to the Python path for imports
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.medication_agent import MedicationAgent

# Base URL used by the agent
BASE_URL = "http://localhost:5000/api"
USER_ID = "test_agent_user"

@pytest.fixture
def agent():
    """Fixture to create a MedicationAgent instance."""
    return MedicationAgent(user_id=USER_ID, base_url=BASE_URL)

def mock_response(status_code=200, json_data=None, text_data=None, raise_for_status_error=None):
    """Helper to create a mock HTTP response object."""
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    if json_data is not None:
        mock_resp.json = MagicMock(return_value=json_data)
    # If json_data is None and no specific text_data, make .json() raise an error
    elif text_data is None:
        mock_resp.json = MagicMock(side_effect=ValueError("No JSON data"))

    mock_resp.text = text_data if text_data is not None else json.dumps(json_data) if json_data else ""
    
    if raise_for_status_error:
        mock_resp.raise_for_status = MagicMock(side_effect=raise_for_status_error)
    else:
        mock_resp.raise_for_status = MagicMock()
        
    return mock_resp

class TestMedicationAgent:

    @patch('requests.request')
    def test_add_medication_success(self, mock_request, agent):
        med_details = {
            "medication_name": "Amoxicillin", "dosage": "250mg", "start_date": "2024-01-01",
            "frequency": "tid", "reminder_times": ["08:00", "14:00", "20:00"]
        }
        # API includes user_id in the response medication object
        response_med_data = {**med_details, "_id": "med123", "user_id": USER_ID}

        mock_request.return_value = mock_response(
            status_code=201, 
            json_data={"message": "Medication added successfully", "medication": response_med_data}
        )
        
        result_message = agent.add_medication(med_details)
        
        mock_request.assert_called_once_with(
            "POST", f"{BASE_URL}/medications", 
            headers={"Content-Type": "application/json"}, 
            json={**med_details, "user_id": USER_ID}, # Agent adds user_id
            params=None
        )
        assert "Medication 'Amoxicillin' added successfully." in result_message

    @patch('requests.request')
    def test_add_medication_failure_api_error(self, mock_request, agent):
        med_details = {"medication_name": "ErrorMed", "start_date": "2024-01-01"}
        mock_request.return_value = mock_response(
            status_code=400, 
            json_data={"error": "Missing required field: dosage"}
        )
        
        result_message = agent.add_medication(med_details)
        mock_request.assert_called_once()
        assert "Failed to add medication. Error 400: Missing required field: dosage" in result_message

    @patch('requests.request')
    def test_list_medications_success_with_meds(self, mock_request, agent):
        api_response_data = [
            {"_id": "med1", "medication_name": "MedA", "dosage": "10mg", "start_date": "2024-01-01T00:00:00"},
            {"_id": "med2", "medication_name": "MedB", "frequency": "daily", "start_date": "2024-02-01T00:00:00", "reminder_times": ["09:00"]}
        ]
        mock_request.return_value = mock_response(status_code=200, json_data=api_response_data)
        
        result = agent.list_medications()
        
        mock_request.assert_called_once_with("GET", f"{BASE_URL}/medications/{USER_ID}", headers=agent.headers, params=None)
        assert "Your medications:" in result
        assert "Name: MedA (ID: med1)" in result
        assert "Dosage: 10mg" in result
        assert "Name: MedB (ID: med2)" in result
        assert "Frequency: daily" in result
        assert "Reminders: 09:00" in result

    @patch('requests.request')
    def test_list_medications_success_no_meds(self, mock_request, agent):
        mock_request.return_value = mock_response(status_code=200, json_data=[]) # Empty list
        
        result = agent.list_medications()
        mock_request.assert_called_once()
        assert "You have no medications listed." == result

    @patch('requests.request')
    def test_update_medication_success(self, mock_request, agent):
        med_id = "med_to_update_123"
        updates = {"notes": "Take after food."}
        response_med_data = {"_id": med_id, "medication_name": "UpdatedMed", "notes": "Take after food."}
        mock_request.return_value = mock_response(
            status_code=200,
            json_data={"message": "Medication updated successfully", "medication": response_med_data}
        )
        
        result = agent.update_medication(med_id, updates)
        mock_request.assert_called_once_with(
            "PUT", f"{BASE_URL}/medications/{med_id}",
            headers=agent.headers, json=updates, params=None
        )
        assert "Medication 'UpdatedMed' updated successfully." in result

    @patch('requests.request')
    def test_delete_medication_success(self, mock_request, agent):
        med_id = "med_to_delete_456"
        mock_request.return_value = mock_response(
            status_code=200,
            json_data={"message": "Medication deleted successfully"}
        )
        
        result = agent.delete_medication(med_id)
        mock_request.assert_called_once_with(
            "DELETE", f"{BASE_URL}/medications/{med_id}",
            headers=agent.headers, params=None
        )
        assert "Medication deleted successfully" == result

    @patch('requests.request')
    def test_get_due_medications_success(self, mock_request, agent):
        api_response_data = [
            {"medication_name": "DueMed1", "dosage": "1 pill", "reminder_times": ["08:00", "12:00"]},
            {"medication_name": "DueMed2", "frequency": "nightly", "reminder_times": ["21:00"]}
        ]
        mock_request.return_value = mock_response(status_code=200, json_data=api_response_data)
        
        result = agent.get_due_medications()
        mock_request.assert_called_once_with("GET", f"{BASE_URL}/medications/due/{USER_ID}", headers=agent.headers, params=None)
        assert "Medications due based on schedule:" in result
        assert "Name: DueMed1" in result
        assert "Reminders: 08:00, 12:00" in result
        assert "Name: DueMed2" in result

    @patch('requests.request')
    def test_get_due_medications_none_due(self, mock_request, agent):
        mock_request.return_value = mock_response(status_code=200, json_data=[])
        result = agent.get_due_medications()
        assert "You have no medications due currently based on your schedule." == result

    # Tests for get_next_dose_info - more complex due to internal logic and time dependency
    @patch('agents.medication_agent.datetime') # Mock datetime inside the agent module
    @patch('requests.request') # Mock requests call made by list_medications
    def test_get_next_dose_info_due_today(self, mock_requests_get, mock_datetime, agent):
        med_name = "Lipitor"
        # Mock current time to be 10:00 AM
        mock_datetime.now.return_value = datetime(2024, 1, 1, 10, 0, 0)
        mock_datetime.strptime = datetime.strptime # Keep original strptime for time parsing
        mock_datetime.time = time
        mock_datetime.date = datetime.date


        api_med_list = [
            {"_id": "lip1", "medication_name": med_name, "start_date": "2023-12-01T00:00:00", 
             "reminder_times": ["09:00", "11:00", "18:00"]}
        ]
        mock_requests_get.return_value = mock_response(status_code=200, json_data=api_med_list)
        
        result = agent.get_next_dose_info(med_name)
        # Expected: Next dose at 11:00 today
        assert f"Your next dose of '{med_name}' is at 11:00 today." == result

    @patch('agents.medication_agent.datetime')
    @patch('requests.request')
    def test_get_next_dose_info_all_passed_today_due_tomorrow(self, mock_requests_get, mock_datetime, agent):
        med_name = "Metformin"
        # Mock current time to be 19:00 PM
        mock_datetime.now.return_value = datetime(2024, 1, 1, 19, 0, 0)
        mock_datetime.strptime = datetime.strptime
        mock_datetime.time = time
        mock_datetime.date = datetime.date
        mock_datetime.timedelta = timedelta # Ensure timedelta is also available if used by agent

        api_med_list = [
            {"_id": "met1", "medication_name": med_name, "start_date": "2023-12-01T00:00:00", 
             "reminder_times": ["08:00", "17:00"]} # Last dose at 17:00, already passed
        ]
        mock_requests_get.return_value = mock_response(status_code=200, json_data=api_med_list)
        
        result = agent.get_next_dose_info(med_name)
        # Expected: Next dose at 08:00 tomorrow
        assert f"Your next dose of '{med_name}' is at 08:00 tomorrow." == result

    @patch('requests.request')
    def test_get_next_dose_info_med_not_found(self, mock_requests_get, agent):
        med_name = "NonExistentMed"
        mock_requests_get.return_value = mock_response(status_code=200, json_data=[]) # No meds found
        
        result = agent.get_next_dose_info(med_name)
        assert f"You don't seem to be taking a medication named '{med_name}'." == result

    @patch('agents.medication_agent.datetime')
    @patch('requests.request')
    def test_get_next_dose_info_no_reminders_set(self, mock_requests_get, mock_datetime, agent):
        med_name = "NoReminderMed"
        mock_datetime.now.return_value = datetime(2024, 1, 1, 10, 0, 0) # Current time doesn't matter much here
        mock_datetime.strptime = datetime.strptime
        mock_datetime.time = time
        mock_datetime.date = datetime.date


        api_med_list = [
            {"_id": "nr1", "medication_name": med_name, "start_date": "2023-12-01T00:00:00", "reminder_times": []} # No reminders
        ]
        mock_requests_get.return_value = mock_response(status_code=200, json_data=api_med_list)
        
        result = agent.get_next_dose_info(med_name)
        assert f"Medication '{med_name}' does not have any reminder times set." == result

    @patch('agents.medication_agent.datetime')
    @patch('requests.request')
    def test_get_next_dose_info_course_ended(self, mock_requests_get, mock_datetime, agent):
        med_name = "PastMed"
        mock_datetime.now.return_value = datetime(2024, 1, 1, 10, 0, 0) # Today is Jan 1, 2024
        mock_datetime.strptime = datetime.strptime
        mock_datetime.time = time
        mock_datetime.date = datetime.date
        mock_datetime.fromisoformat = datetime.fromisoformat


        api_med_list = [
            {"_id": "pm1", "medication_name": med_name, 
             "start_date": "2023-11-01T00:00:00", 
             "end_date": "2023-12-15T00:00:00", # Ended last month
             "reminder_times": ["09:00"]}
        ]
        mock_requests_get.return_value = mock_response(status_code=200, json_data=api_med_list)
        
        result = agent.get_next_dose_info(med_name)
        assert f"You have finished your course of '{med_name}' on 2023-12-15." == result

    @patch('agents.medication_agent.datetime')
    @patch('requests.request')
    def test_get_next_dose_info_not_started_yet(self, mock_requests_get, mock_datetime, agent):
        med_name = "FutureMed"
        mock_datetime.now.return_value = datetime(2024, 1, 1, 10, 0, 0) # Today is Jan 1, 2024
        mock_datetime.strptime = datetime.strptime
        mock_datetime.time = time
        mock_datetime.date = datetime.date
        mock_datetime.fromisoformat = datetime.fromisoformat

        api_med_list = [
            {"_id": "fm1", "medication_name": med_name, 
             "start_date": "2024-02-01T00:00:00", # Starts next month
             "reminder_times": ["09:00"]}
        ]
        mock_requests_get.return_value = mock_response(status_code=200, json_data=api_med_list)
        
        result = agent.get_next_dose_info(med_name)
        assert f"You are scheduled to start taking '{med_name}' on 2024-02-01." == result

    @patch('requests.request')
    def test_get_next_dose_info_api_call_fails(self, mock_requests_get, agent):
        med_name = "AnyMed"
        # Simulate requests.get raising an exception or returning bad status
        mock_requests_get.return_value = mock_response(status_code=500, json_data={"error": "Server exploded"})
        
        result = agent.get_next_dose_info(med_name)
        assert f"Could not fetch medication list to find {med_name}. Error: Server exploded" in result

    # Helper for importing json when it's not automatically available in the test scope for mock_response
    import json
```
