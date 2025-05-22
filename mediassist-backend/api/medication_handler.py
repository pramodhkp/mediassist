import sys
import os
from datetime import datetime, timedelta

# Add the mediassist-backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Use mock client instead of the real MongoDB client
from storage.mock_client import (
    get_medications, add_medication, update_medication, delete_medication,
    get_medication_by_id, get_due_medications
)

class MedicationHandler:
    """
    Handler for medication-related operations.
    """
    
    def get_all_medications(self):
        """
        Retrieves all medications for the user.
        """
        try:
            medications = get_medications()
            return medications
        except Exception as e:
            print(f"Error retrieving medications: {str(e)}")
            return []
    
    def add_new_medication(self, medication_data):
        """
        Adds a new medication to the database.
        
        Args:
            medication_data (dict): The medication data to add.
                {
                    "name": str,
                    "dosage": str,
                    "frequency": str,
                    "start_date": str (ISO format),
                    "end_date": str (ISO format, optional),
                    "time_of_day": list[str],
                    "notes": str (optional)
                }
        
        Returns:
            str: The ID of the newly added medication.
        """
        try:
            # Convert string dates to datetime objects
            if 'start_date' in medication_data and medication_data['start_date']:
                medication_data['start_date'] = datetime.fromisoformat(medication_data['start_date'])
            else:
                medication_data['start_date'] = datetime.now()
                
            if 'end_date' in medication_data and medication_data['end_date']:
                medication_data['end_date'] = datetime.fromisoformat(medication_data['end_date'])
            
            # Add created_at timestamp
            medication_data['created_at'] = datetime.now()
            
            # Add the medication to the database
            medication_id = add_medication(medication_data)
            return str(medication_id)
        except Exception as e:
            print(f"Error adding medication: {str(e)}")
            raise
    
    def update_existing_medication(self, medication_id, medication_data):
        """
        Updates an existing medication in the database.
        
        Args:
            medication_id (str): The ID of the medication to update.
            medication_data (dict): The updated medication data.
        
        Returns:
            bool: True if the update was successful, False otherwise.
        """
        try:
            # Convert string dates to datetime objects
            if 'start_date' in medication_data and medication_data['start_date']:
                medication_data['start_date'] = datetime.fromisoformat(medication_data['start_date'])
                
            if 'end_date' in medication_data and medication_data['end_date']:
                medication_data['end_date'] = datetime.fromisoformat(medication_data['end_date'])
            
            # Update the medication in the database
            success = update_medication(medication_id, medication_data)
            return success
        except Exception as e:
            print(f"Error updating medication: {str(e)}")
            raise
    
    def delete_existing_medication(self, medication_id):
        """
        Deletes a medication from the database.
        
        Args:
            medication_id (str): The ID of the medication to delete.
        
        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        try:
            success = delete_medication(medication_id)
            return success
        except Exception as e:
            print(f"Error deleting medication: {str(e)}")
            raise
    
    def get_medication_details(self, medication_id):
        """
        Retrieves details for a specific medication.
        
        Args:
            medication_id (str): The ID of the medication to retrieve.
        
        Returns:
            dict: The medication details.
        """
        try:
            medication = get_medication_by_id(medication_id)
            return medication
        except Exception as e:
            print(f"Error retrieving medication details: {str(e)}")
            raise
    
    def get_medication_reminders(self, days=1):
        """
        Retrieves medications that are due in the next specified number of days.
        
        Args:
            days (int): Number of days to look ahead for due medications.
        
        Returns:
            list: List of medications due in the specified time period.
        """
        try:
            end_date = datetime.now() + timedelta(days=days)
            due_medications = get_due_medications(end_date)
            return due_medications
        except Exception as e:
            print(f"Error retrieving medication reminders: {str(e)}")
            return []