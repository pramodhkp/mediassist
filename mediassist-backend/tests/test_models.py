import pytest
import mongoengine
from mongoengine import connect, disconnect
from mongomock import MongoClient
from datetime import datetime, timedelta

# Add the mediassist-backend directory to the Python path for imports
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from storage.models import Medication # Model to test

@pytest.fixture(scope="function", autouse=True)
def setup_teardown_mongo():
    """Connect to mongomock before each test and disconnect after."""
    # Use mongomock as the client for mongoengine
    disconnect() # Disconnect any existing connection
    connect('test_db', mongo_client_class=MongoClient, alias='default')
    yield
    # Teardown: drop the database after each test (mongomock specific)
    # For a real MongoDB, you might clear collections or use a dedicated test DB
    # mongoengine.get_db().client.drop_database('test_db') # This is for real pymongo
    # For mongomock, simply disconnecting and reconnecting effectively clears
    disconnect()

class TestMedicationModel:

    def test_create_medication_valid(self):
        """Test creating a Medication instance with all valid required fields."""
        med_data = {
            "user_id": "test_user_1",
            "medication_name": "Amoxicillin",
            "dosage": "250mg",
            "frequency": "Every 8 hours",
            "start_date": datetime.utcnow(),
            "end_date": datetime.utcnow() + timedelta(days=7),
            "reminder_times": ["08:00", "16:00", "23:59"],
            "notes": "Take with food."
        }
        med = Medication(**med_data)
        med.save()

        retrieved_med = Medication.objects(id=med.id).first()
        assert retrieved_med is not None
        assert retrieved_med.user_id == med_data["user_id"]
        assert retrieved_med.medication_name == med_data["medication_name"]
        assert retrieved_med.dosage == med_data["dosage"]
        assert retrieved_med.frequency == med_data["frequency"]
        assert retrieved_med.start_date.date() == med_data["start_date"].date() # Compare dates
        assert retrieved_med.end_date.date() == med_data["end_date"].date()
        assert retrieved_med.reminder_times == med_data["reminder_times"]
        assert retrieved_med.notes == med_data["notes"]
        assert retrieved_med.id is not None

    def test_create_medication_required_fields_only(self):
        """Test creating a Medication instance with only required fields."""
        med_data = {
            "user_id": "test_user_2",
            "medication_name": "Lisinopril",
            "start_date": datetime.utcnow(),
            # Optional fields (dosage, frequency, end_date, reminder_times, notes) are omitted
        }
        med = Medication(**med_data)
        med.save()
        
        retrieved_med = Medication.objects(id=med.id).first()
        assert retrieved_med is not None
        assert retrieved_med.user_id == med_data["user_id"]
        assert retrieved_med.medication_name == med_data["medication_name"]
        assert retrieved_med.start_date.date() == med_data["start_date"].date()
        assert retrieved_med.dosage is None # Check optional fields are None or default
        assert retrieved_med.frequency is None
        assert retrieved_med.end_date is None
        assert retrieved_med.reminder_times == [] # Default for ListField
        assert retrieved_med.notes is None


    def test_validation_error_missing_user_id(self):
        """Test for ValidationError when 'user_id' is missing."""
        with pytest.raises(mongoengine.ValidationError) as excinfo:
            med = Medication(medication_name="TestMed", start_date=datetime.utcnow())
            med.save()
        assert "Medication.user_id: Field is required" in str(excinfo.value)

    def test_validation_error_missing_medication_name(self):
        """Test for ValidationError when 'medication_name' is missing."""
        with pytest.raises(mongoengine.ValidationError) as excinfo:
            med = Medication(user_id="test_user_3", start_date=datetime.utcnow())
            med.save()
        assert "Medication.medication_name: Field is required" in str(excinfo.value)

    def test_validation_error_missing_start_date(self):
        """Test for ValidationError when 'start_date' is missing."""
        # Note: start_date is implicitly required by mongoengine if not (required=False)
        # However, the model definition `start_date: datetime = mongoengine.DateTimeField()`
        # makes it required by default unless `null=True` or `required=False` is set.
        # Let's confirm if the model definition implies required=True.
        # If `start_date = mongoengine.DateTimeField()` it is indeed required.
        with pytest.raises(mongoengine.ValidationError) as excinfo:
            med = Medication(user_id="test_user_4", medication_name="TestMedNoDate")
            med.save()
        # The error message might vary slightly based on mongoengine version or exact model def.
        # It often looks like: "ValidationError (Medication:...) (Field is required: ['start_date'])"
        assert "start_date" in str(excinfo.value).lower() # Check if 'start_date' is mentioned in the error
        assert "required" in str(excinfo.value).lower()


    def test_optional_fields_default_values(self):
        """Test that optional fields have correct defaults if not provided."""
        med = Medication(
            user_id="test_user_5",
            medication_name="MinimalMed",
            start_date=datetime.utcnow()
        )
        med.save()
        retrieved = Medication.objects.first()
        assert retrieved.dosage is None
        assert retrieved.frequency is None
        assert retrieved.end_date is None
        assert retrieved.reminder_times == [] # Default for ListField(StringField)
        assert retrieved.notes is None

    def test_reminder_times_is_list_of_strings(self):
        """Test reminder_times field stores a list of strings."""
        med_data = {
            "user_id": "test_user_6",
            "medication_name": "TimeMed",
            "start_date": datetime.utcnow(),
            "reminder_times": ["09:00", "17:30"]
        }
        med = Medication(**med_data)
        med.save()
        retrieved = Medication.objects.first()
        assert retrieved.reminder_times == ["09:00", "17:30"]

    def test_end_date_before_start_date_logic(self):
        """Test logic for end_date before start_date (model doesn't enforce, API should)."""
        # The model itself might not have validation for end_date < start_date.
        # This kind of logic is typically handled at the application/API layer.
        # This test just confirms the model can store it if allowed.
        start = datetime.utcnow()
        end = start - timedelta(days=1) # End date is before start date
        
        med = Medication(
            user_id="test_user_7",
            medication_name="DateLogicMed",
            start_date=start,
            end_date=end 
        )
        # No validation error is expected from the model for this unless custom validation is added.
        med.save() 
        retrieved = Medication.objects.first()
        assert retrieved.end_date == end
        assert retrieved.start_date == start
        # The API layer test (test_medication_api.py) should verify that such a case is rejected.

    def test_query_by_user_id(self):
        """Test retrieving medications by user_id."""
        Medication(user_id="userA", medication_name="MedA1", start_date=datetime.utcnow()).save()
        Medication(user_id="userA", medication_name="MedA2", start_date=datetime.utcnow()).save()
        Medication(user_id="userB", medication_name="MedB1", start_date=datetime.utcnow()).save()

        meds_user_a = Medication.objects(user_id="userA")
        assert meds_user_a.count() == 2
        med_names_user_a = sorted([m.medication_name for m in meds_user_a])
        assert med_names_user_a == ["MedA1", "MedA2"]

        meds_user_b = Medication.objects(user_id="userB")
        assert meds_user_b.count() == 1
        assert meds_user_b.first().medication_name == "MedB1"

        meds_user_c = Medication.objects(user_id="userC")
        assert meds_user_c.count() == 0

```
