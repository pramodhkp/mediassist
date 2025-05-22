"""
Mock implementations of database functions for testing without MongoDB.
"""
from datetime import datetime

# Mock medication data
MOCK_MEDICATIONS = [
    {
        "_id": "1",
        "name": "Aspirin",
        "dosage": "100mg",
        "frequency": "Daily",
        "time_of_day": ["Morning"],
        "start_date": "2025-05-01T00:00:00.000Z",
        "end_date": "2025-06-01T00:00:00.000Z",
        "notes": "Take with food",
        "created_at": "2025-05-01T00:00:00.000Z"
    },
    {
        "_id": "2",
        "name": "Vitamin D",
        "dosage": "1000 IU",
        "frequency": "Daily",
        "time_of_day": ["Morning", "Evening"],
        "start_date": "2025-04-15T00:00:00.000Z",
        "end_date": None,
        "notes": "For bone health",
        "created_at": "2025-04-15T00:00:00.000Z"
    },
    {
        "_id": "3",
        "name": "Ibuprofen",
        "dosage": "200mg",
        "frequency": "As Needed",
        "time_of_day": [],
        "start_date": "2025-05-10T00:00:00.000Z",
        "end_date": None,
        "notes": "For pain relief",
        "created_at": "2025-05-10T00:00:00.000Z"
    }
]

def get_medications():
    """
    Retrieves all medications from the database.
    
    Returns:
        A list of medication records
    """
    return MOCK_MEDICATIONS.copy()

def add_medication(medication_data):
    """
    Adds a new medication to the database.
    
    Args:
        medication_data (dict): The medication data to add
    
    Returns:
        The ID of the inserted record
    """
    # Generate a mock ID
    new_id = str(len(MOCK_MEDICATIONS) + 1)
    
    # Convert datetime objects to ISO strings for consistency
    if 'start_date' in medication_data and medication_data['start_date']:
        if isinstance(medication_data['start_date'], datetime):
            medication_data['start_date'] = medication_data['start_date'].isoformat()
    
    if 'end_date' in medication_data and medication_data['end_date']:
        if isinstance(medication_data['end_date'], datetime):
            medication_data['end_date'] = medication_data['end_date'].isoformat()
    
    if 'created_at' in medication_data and medication_data['created_at']:
        if isinstance(medication_data['created_at'], datetime):
            medication_data['created_at'] = medication_data['created_at'].isoformat()
    
    # Create a new medication record
    new_medication = {
        "_id": new_id,
        **medication_data
    }
    
    # Add to the mock database
    MOCK_MEDICATIONS.append(new_medication)
    
    return new_id

def update_medication(medication_id, medication_data):
    """
    Updates an existing medication in the database.
    
    Args:
        medication_id (str): The ID of the medication to update
        medication_data (dict): The updated medication data
    
    Returns:
        True if the update was successful, False otherwise
    """
    for i, medication in enumerate(MOCK_MEDICATIONS):
        if medication["_id"] == medication_id:
            # Convert datetime objects to ISO strings for consistency
            if 'start_date' in medication_data and medication_data['start_date']:
                if isinstance(medication_data['start_date'], datetime):
                    medication_data['start_date'] = medication_data['start_date'].isoformat()
            
            if 'end_date' in medication_data and medication_data['end_date']:
                if isinstance(medication_data['end_date'], datetime):
                    medication_data['end_date'] = medication_data['end_date'].isoformat()
            
            # Update the medication
            MOCK_MEDICATIONS[i] = {
                **MOCK_MEDICATIONS[i],
                **medication_data
            }
            return True
    
    return False

def delete_medication(medication_id):
    """
    Deletes a medication from the database.
    
    Args:
        medication_id (str): The ID of the medication to delete
    
    Returns:
        True if the deletion was successful, False otherwise
    """
    for i, medication in enumerate(MOCK_MEDICATIONS):
        if medication["_id"] == medication_id:
            MOCK_MEDICATIONS.pop(i)
            return True
    
    return False

def get_medication_by_id(medication_id):
    """
    Retrieves a specific medication by ID.
    
    Args:
        medication_id (str): The ID of the medication to retrieve
    
    Returns:
        The medication record, or None if not found
    """
    for medication in MOCK_MEDICATIONS:
        if medication["_id"] == medication_id:
            return medication.copy()
    
    return None

def get_due_medications(end_date):
    """
    Retrieves medications that are due before the specified end date.
    
    Args:
        end_date (datetime): The end date to check for due medications
    
    Returns:
        A list of due medication records
    """
    # For mock purposes, just return the first two medications
    return MOCK_MEDICATIONS[:2]