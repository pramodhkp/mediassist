from flask import Blueprint, request, jsonify
from mediassist_backend.storage.models import Medication # Corrected import path
from datetime import datetime, time
import mongoengine
import re # For HH:MM validation

medication_bp = Blueprint('medication_bp', __name__, url_prefix='/api') # Added url_prefix

def is_valid_time_format(time_str):
    """Validates HH:MM format."""
    return bool(re.match(r'^([01]\d|2[0-3]):([0-5]\d)$', time_str))

@medication_bp.route('/medications', methods=['POST'])
def add_medication():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    # Required fields validation
    required_fields = ['user_id', 'medication_name', 'start_date']
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    user_id = data['user_id']
    medication_name = data['medication_name']
    
    # Date validation and conversion
    try:
        start_date_str = data['start_date']
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD."}), 400

    end_date = None
    if 'end_date' in data and data['end_date']:
        try:
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD."}), 400
        if end_date < start_date:
            return jsonify({"error": "end_date cannot be before start_date."}), 400

    # Reminder times validation
    reminder_times = data.get('reminder_times', [])
    if not isinstance(reminder_times, list):
        return jsonify({"error": "reminder_times must be a list."}), 400
    for t in reminder_times:
        if not isinstance(t, str) or not is_valid_time_format(t):
            return jsonify({"error": f"Invalid time format in reminder_times: '{t}'. Use HH:MM."}), 400

    try:
        medication = Medication(
            user_id=user_id,
            medication_name=medication_name,
            dosage=data.get('dosage'),
            frequency=data.get('frequency'),
            start_date=start_date,
            end_date=end_date,
            reminder_times=reminder_times,
            notes=data.get('notes')
        )
        medication.save()
        # Convert ObjectId to string for the response
        med_id = str(medication.id)
        response_data = medication.to_mongo().to_dict()
        response_data['_id'] = med_id # mongoengine uses 'id', but to_mongo has '_id'
        if 'id' in response_data: # clean up if 'id' field also exists
            del response_data['id']

        # Ensure dates are in ISO format for the response
        if isinstance(response_data.get('start_date'), datetime):
            response_data['start_date'] = response_data['start_date'].isoformat()
        if isinstance(response_data.get('end_date'), datetime):
            response_data['end_date'] = response_data['end_date'].isoformat()
            
        return jsonify({"message": "Medication added successfully", "medication": response_data}), 201
    except mongoengine.ValidationError as e:
        return jsonify({"error": "Validation error", "details": e.to_dict()}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

def serialize_medication(med):
    """Helper function to serialize a Medication object to a dictionary."""
    data = med.to_mongo().to_dict()
    data['_id'] = str(med.id)
    if 'id' in data: # clean up if 'id' field also exists
        del data['id']
    if isinstance(data.get('start_date'), datetime):
        data['start_date'] = data['start_date'].isoformat()
    if isinstance(data.get('end_date'), datetime):
        data['end_date'] = data['end_date'].isoformat()
    return data

@medication_bp.route('/medications/<user_id>', methods=['GET'])
def list_medications(user_id):
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    try:
        medications = Medication.objects(user_id=user_id)
        if not medications:
            return jsonify([]), 200 # Return empty list if no medications found
            
        result = [serialize_medication(med) for med in medications]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@medication_bp.route('/medications/<medication_id>', methods=['PUT'])
def update_medication(medication_id):
    if not medication_id:
        return jsonify({"error": "medication_id is required"}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload or no data to update"}), 400

    try:
        medication = Medication.objects(id=medication_id).first()
        if not medication:
            return jsonify({"error": "Medication not found"}), 404

        # Update fields one by one, with validation where necessary
        if 'user_id' in data: # Generally, user_id should not be updated, but if allowed:
            if not data['user_id']:
                return jsonify({"error": "user_id cannot be empty"}), 400
            medication.user_id = data['user_id']
        
        if 'medication_name' in data:
            if not data['medication_name']:
                return jsonify({"error": "medication_name cannot be empty"}), 400
            medication.medication_name = data['medication_name']

        if 'dosage' in data:
            medication.dosage = data['dosage']
        
        if 'frequency' in data:
            medication.frequency = data['frequency']

        # Date validation for start_date
        if 'start_date' in data:
            if not data['start_date']:
                 return jsonify({"error": "start_date cannot be empty if provided"}), 400
            try:
                medication.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
            except ValueError:
                return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD."}), 400
        
        # Date validation for end_date
        if 'end_date' in data:
            if data['end_date']: # Allow setting end_date to null/empty
                try:
                    medication.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
                except ValueError:
                    return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD."}), 400
            else:
                medication.end_date = None # Explicitly set to None if empty string or null passed

        # Ensure end_date is not before start_date
        if medication.end_date and medication.start_date and medication.end_date < medication.start_date:
            return jsonify({"error": "end_date cannot be before start_date."}), 400

        # Reminder times validation
        if 'reminder_times' in data:
            reminder_times = data['reminder_times']
            if not isinstance(reminder_times, list):
                return jsonify({"error": "reminder_times must be a list."}), 400
            for t in reminder_times:
                if not isinstance(t, str) or not is_valid_time_format(t):
                    return jsonify({"error": f"Invalid time format in reminder_times: '{t}'. Use HH:MM."}), 400
            medication.reminder_times = reminder_times
        
        if 'notes' in data:
            medication.notes = data['notes']

        medication.save()
        return jsonify({"message": "Medication updated successfully", "medication": serialize_medication(medication)}), 200
    except mongoengine.DoesNotExist:
        return jsonify({"error": "Medication not found"}), 404
    except mongoengine.ValidationError as e:
        return jsonify({"error": "Validation error", "details": e.to_dict()}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@medication_bp.route('/medications/<medication_id>', methods=['DELETE'])
def delete_medication(medication_id):
    if not medication_id:
        return jsonify({"error": "medication_id is required"}), 400
    
    try:
        medication = Medication.objects(id=medication_id).first()
        if not medication:
            return jsonify({"error": "Medication not found"}), 404
        
        medication.delete()
        return jsonify({"message": "Medication deleted successfully"}), 200
    except mongoengine.DoesNotExist: # Should be caught by .first() returning None, but as a safeguard
        return jsonify({"error": "Medication not found"}), 404
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@medication_bp.route('/medications/due/<user_id>', methods=['GET'])
def get_due_medications(user_id):
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    try:
        today = datetime.utcnow().date() # Use date for comparison against start_date and end_date parts
        
        # Construct the query
        query_params = {
            "user_id": user_id,
            "reminder_times__exists": True, # Ensures reminder_times field exists
            "reminder_times__ne": [],       # Ensures reminder_times list is not empty
            "start_date__lte": datetime.combine(today, datetime.min.time()) # Medication should have started
        }
        
        # Medications that are either not ended or ended today or in the future
        # mongoengine.Q supports OR operations
        # Q(end_date__exists=False) | Q(end_date__gte=datetime.combine(today, datetime.min.time()))
        # However, mongoengine seems to handle None for dates in a way that this might be simpler:
        # if a medication has no end_date, it's considered ongoing.
        # If it has an end_date, it must be >= today.

        medications = Medication.objects(**query_params)
        
        due_medications = []
        for med in medications:
            # Further filter by end_date if it exists
            if med.end_date:
                if med.end_date.date() >= today:
                    due_medications.append(serialize_medication(med))
            else: # No end_date means it's ongoing
                due_medications.append(serialize_medication(med))
                
        return jsonify(due_medications), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
