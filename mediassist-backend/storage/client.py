from pymongo import MongoClient
from datetime import datetime, timedelta
import os
import shutil
import uuid
from bson.objectid import ObjectId

# Connect to MongoDB

def get_mongo_client():
    """
    Returns a MongoDB client instance.
    """
    # Replace with your MongoDB connection string if needed
    return MongoClient("mongodb://localhost:27017/")

def store_nutrition_data(data):
    """
    Stores nutrition data in MongoDB.
    """
    client = get_mongo_client()
    db = client["nutrition_db"]
    collection = db["nutrition_data"]
    
    # Insert the data into the collection
    result = collection.insert_one(data)
    
    return result.inserted_id

def store_medical_conditions_data(data):
    """
    Stores medical conditions data in MongoDB.
    """
    client = get_mongo_client()
    db = client["medical_conditions_db"]
    collection = db["medical_conditions_data"]
    
    # Insert the data into the collection
    result = collection.insert_one(data)
    
    return result.inserted_id

def store_user_profile_data(data):
    """
    Stores or updates user profile data in MongoDB.
    If a profile already exists, it updates only the fields that are provided in the new data.
    If no profile exists, it creates a new one.
    """
    client = get_mongo_client()
    db = client["user_profile_db"]
    collection = db["user_profile_data"]
    
    # Get the most recent profile data
    existing_profile = collection.find_one(sort=[("timestamp", -1)])
    
    if existing_profile:
        # Update only the fields that are provided in the new data
        update_data = {}
        if 'age' in data and data['age'] is not None:
            update_data['age'] = data['age']
        if 'gender' in data and data['gender'] is not None:
            update_data['gender'] = data['gender']
        if 'height' in data and data['height'] is not None:
            update_data['height'] = data['height']
        if 'weight' in data and data['weight'] is not None:
            update_data['weight'] = data['weight']
        
        # Add timestamp
        update_data['timestamp'] = data['timestamp']
        
        # Update the existing profile
        result = collection.update_one(
            {'_id': existing_profile['_id']},
            {'$set': update_data}
        )
        
        return existing_profile['_id']
    else:
        # Insert the data into the collection
        result = collection.insert_one(data)
        
        return result.inserted_id

def get_user_profile_data():
    """
    Retrieves the latest user profile data from MongoDB.
    """
    client = get_mongo_client()
    db = client["user_profile_db"]
    collection = db["user_profile_data"]
    
    # Get the most recent profile data
    profile_data = collection.find_one(sort=[("timestamp", -1)])
    
    return profile_data

def store_insights_data(data):
    """
    Stores insights data in MongoDB.
    
    Args:
        data (dict): A dictionary containing insights data with the following keys:
            - analysis_type: "daily" or "weekly"
            - content: The actual insights content
            - date: The date of the insights
            - metadata: Optional metadata about the insights
    
    Returns:
        The ID of the inserted document
    """
    client = get_mongo_client()
    db = client["insights_db"]
    collection = db["insights_data"]
    
    # Insert the data into the collection
    result = collection.insert_one(data)
    
    return result.inserted_id

def get_daily_insights_for_range(start_date, end_date):
    """
    Retrieves daily insights for a specific date range.
    
    Args:
        start_date (datetime): The start date of the range
        end_date (datetime): The end date of the range
    
    Returns:
        A list of daily insights within the specified date range
    """
    client = get_mongo_client()
    db = client["insights_db"]
    collection = db["insights_data"]
    
    # Get insights within the date range
    insights = collection.find({
        "analysis_type": "daily",
        "date": {"$gte": start_date, "$lte": end_date}
    }).sort("date", 1)
    
    return list(insights)

def get_most_recent_daily_insights():
    """
    Retrieves the most recent daily insights from MongoDB.
    
    Returns:
        The most recent daily insights document, or None if no insights exist
    """
    client = get_mongo_client()
    db = client["insights_db"]
    collection = db["insights_data"]
    
    # Get the most recent daily insights
    insights = collection.find_one(
        {"analysis_type": "daily"},
        sort=[("date", -1)]
    )
    
    return insights

def get_medical_conditions_data():
    """
    Retrieves the medical conditions data from MongoDB.
    """
    client = get_mongo_client()
    db = client["medical_conditions_db"]
    collection = db["medical_conditions_data"]
    
    # Get all medical conditions
    conditions = list(collection.find())
    
    # Convert ObjectId to string for JSON serialization
    for condition in conditions:
        if '_id' in condition:
            condition['_id'] = str(condition['_id'])
        if 'timestamp' in condition:
            condition['timestamp'] = condition['timestamp'].isoformat()
    
    return conditions

def get_nutrition_data_for_period(start_date, end_date):
    """
    Retrieves nutrition data for a specific date range.
    
    Args:
        start_date (datetime): The start date of the range
        end_date (datetime): The end date of the range
    
    Returns:
        A list of nutrition data entries within the specified date range
    """
    client = get_mongo_client()
    db = client["nutrition_db"]
    collection = db["nutrition_data"]
    
    # Get nutrition data within the date range
    nutrition_data = collection.find({
        "timestamp": {"$gte": start_date, "$lte": end_date}
    }).sort("timestamp", 1)
    
    # Convert ObjectId to string for JSON serialization
    result = list(nutrition_data)
    for entry in result:
        if '_id' in entry:
            entry['_id'] = str(entry['_id'])
        if 'timestamp' in entry:
            entry['timestamp'] = entry['timestamp'].isoformat()
    
    return result

def analyze_nutrition_data(data):
    """
    Analyzes nutrition data and provides insights.
    
    Args:
        data (list): List of nutrition data entries
    
    Returns:
        A dictionary containing the analysis results
    """
    if not data:
        return {"message": "No nutrition data available for the specified period."}
    
    # Extract dates for grouping
    for entry in data:
        if 'timestamp' in entry and isinstance(entry['timestamp'], str):
            entry['date'] = entry['timestamp'].split('T')[0]
    
    # Group by date
    dates = {}
    for entry in data:
        date = entry.get('date')
        if date:
            if date not in dates:
                dates[date] = []
            dates[date].append(entry)
    
    # Calculate daily totals
    daily_totals = {}
    for date, entries in dates.items():
        daily_totals[date] = {
            'calories': sum(entry.get('calories', 0) for entry in entries),
            'protein': sum(entry.get('protein', 0) for entry in entries),
            'carbohydrates': sum(entry.get('carbohydrates', 0) for entry in entries),
            'fats': sum(entry.get('fats', 0) for entry in entries),
            'entries': len(entries)
        }
    
    # Calculate overall statistics
    total_days = len(daily_totals)
    if total_days == 0:
        return {"message": "No nutrition data available for the specified period."}
    
    avg_calories = sum(day['calories'] for day in daily_totals.values()) / total_days
    avg_protein = sum(day['protein'] for day in daily_totals.values()) / total_days
    avg_carbs = sum(day['carbohydrates'] for day in daily_totals.values()) / total_days
    avg_fats = sum(day['fats'] for day in daily_totals.values()) / total_days
    
    return {
        "total_entries": len(data),
        "total_days": total_days,
        "daily_totals": daily_totals,
        "average_daily": {
            "calories": avg_calories,
            "protein": avg_protein,
            "carbohydrates": avg_carbs,
            "fats": avg_fats
        }
    }

def ensure_upload_dir():
    """
    Ensures that the uploads directory exists.
    
    Returns:
        The path to the uploads directory
    """
    # Create uploads directory in the root of the project if it doesn't exist
    uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../uploads'))
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
    return uploads_dir

def store_medical_report(file_data, filename, file_type, file_size, description=None):
    """
    Stores a medical report file in the filesystem and metadata in MongoDB.
    
    Args:
        file_data (bytes or file-like object): The file data or file object
        filename (str): The name of the file
        file_type (str): The MIME type of the file
        file_size (int): The size of the file in bytes
        description (str, optional): A description of the file
    
    Returns:
        The ID of the inserted metadata record
    """
    # Generate a unique filename to avoid collisions
    unique_filename = f"{uuid.uuid4()}_{filename}"
    
    # Ensure uploads directory exists
    uploads_dir = ensure_upload_dir()
    file_path = os.path.join(uploads_dir, unique_filename)
    
    # Save the file to the filesystem
    if hasattr(file_data, 'read'):
        # If file_data is a file-like object
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(file_data, f)
    else:
        # If file_data is bytes
        with open(file_path, 'wb') as f:
            f.write(file_data)
    
    # Store metadata in MongoDB
    client = get_mongo_client()
    db = client["medical_reports_db"]
    collection = db["medical_reports_metadata"]
    
    metadata = {
        "filename": filename,
        "stored_filename": unique_filename,
        "file_type": file_type,
        "file_size": file_size,
        "description": description,
        "uploadDate": datetime.utcnow()
    }
    
    result = collection.insert_one(metadata)
    return result.inserted_id

def get_medical_reports():
    """
    Retrieves a list of all medical reports metadata.
    
    Returns:
        A list of medical report metadata
    """
    client = get_mongo_client()
    db = client["medical_reports_db"]
    collection = db["medical_reports_metadata"]
    
    # Get all metadata records
    reports = collection.find().sort("uploadDate", -1)
    
    # Convert to list and format for JSON serialization
    result = []
    for report in reports:
        result.append({
            "_id": str(report["_id"]),
            "filename": report["filename"],
            "file_type": report["file_type"],
            "file_size": report["file_size"],
            "description": report.get("description"),
            "uploadDate": report["uploadDate"].isoformat()
        })
    
    return result

def get_medical_report(file_id):
    """
    Retrieves a specific medical report file.
    
    Args:
        file_id (str): The ID of the metadata record
    
    Returns:
        A tuple containing (file_path, filename, content_type)
    """
    from bson.objectid import ObjectId
    
    client = get_mongo_client()
    db = client["medical_reports_db"]
    collection = db["medical_reports_metadata"]
    
    # Get the metadata record
    metadata = collection.find_one({"_id": ObjectId(file_id)})
    if not metadata:
        return None, None, None
    
    # Get the file path
    uploads_dir = ensure_upload_dir()
    file_path = os.path.join(uploads_dir, metadata["stored_filename"])
    
    # Check if file exists
    if not os.path.exists(file_path):
        return None, None, None
    
    return file_path, metadata["filename"], metadata["file_type"]

def delete_medical_report(file_id):
    """
    Deletes a specific medical report file.
    
    Args:
        file_id (str): The ID of the metadata record
    
    Returns:
        True if the file was deleted, False otherwise
    """
    client = get_mongo_client()
    db = client["medical_reports_db"]
    collection = db["medical_reports_metadata"]
    
    # Get the metadata record
    metadata = collection.find_one({"_id": ObjectId(file_id)})
    if not metadata:
        return False
    
    # Get the file path
    uploads_dir = ensure_upload_dir()
    file_path = os.path.join(uploads_dir, metadata["stored_filename"])
    
    # Delete the file if it exists
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Delete the metadata record
    collection.delete_one({"_id": ObjectId(file_id)})
    
    return True

# Medication-related functions

def get_medications():
    """
    Retrieves all medications from the database.
    
    Returns:
        A list of medication records
    """
    # Mock data for testing
    result = [
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
    
    return result

def add_medication(medication_data):
    """
    Adds a new medication to the database.
    
    Args:
        medication_data (dict): The medication data to add
    
    Returns:
        The ID of the inserted record
    """
    client = get_mongo_client()
    db = client["medications_db"]
    collection = db["medications"]
    
    # Insert the medication record
    result = collection.insert_one(medication_data)
    return result.inserted_id

def update_medication(medication_id, medication_data):
    """
    Updates an existing medication in the database.
    
    Args:
        medication_id (str): The ID of the medication to update
        medication_data (dict): The updated medication data
    
    Returns:
        True if the update was successful, False otherwise
    """
    client = get_mongo_client()
    db = client["medications_db"]
    collection = db["medications"]
    
    # Update the medication record
    result = collection.update_one(
        {"_id": ObjectId(medication_id)},
        {"$set": medication_data}
    )
    
    return result.modified_count > 0

def delete_medication(medication_id):
    """
    Deletes a medication from the database.
    
    Args:
        medication_id (str): The ID of the medication to delete
    
    Returns:
        True if the deletion was successful, False otherwise
    """
    # Mock implementation for testing
    return True

def get_due_medications(end_date):
    """
    Retrieves medications that are due before the specified end date.
    
    Args:
        end_date (datetime): The end date to check for due medications
    
    Returns:
        A list of due medication records
    """
    # Mock data for testing
    result = [
        {
            "_id": "1",
            "name": "Aspirin",
            "dosage": "100mg",
            "frequency": "Daily",
            "time_of_day": ["Morning"],
            "start_date": "2025-05-01T00:00:00.000Z",
            "end_date": "2025-06-01T00:00:00.000Z",
            "notes": "Take with food"
        },
        {
            "_id": "2",
            "name": "Vitamin D",
            "dosage": "1000 IU",
            "frequency": "Daily",
            "time_of_day": ["Morning", "Evening"],
            "start_date": "2025-04-15T00:00:00.000Z",
            "notes": "For bone health"
        }
    ]
    
    return result

def get_medication_by_id(medication_id):
    """
    Retrieves a specific medication by ID.
    
    Args:
        medication_id (str): The ID of the medication to retrieve
    
    Returns:
        The medication record, or None if not found
    """
    client = get_mongo_client()
    db = client["medications_db"]
    collection = db["medications"]
    
    # Get the medication record
    medication = collection.find_one({"_id": ObjectId(medication_id)})
    
    if medication:
        # Format for JSON serialization
        medication["_id"] = str(medication["_id"])
        if "start_date" in medication and medication["start_date"]:
            medication["start_date"] = medication["start_date"].isoformat()
        if "end_date" in medication and medication["end_date"]:
            medication["end_date"] = medication["end_date"].isoformat()
        if "created_at" in medication and medication["created_at"]:
            medication["created_at"] = medication["created_at"].isoformat()
    
    return medication

def get_due_medications(end_date):
    """
    Retrieves medications that are due by the specified end date.
    
    Args:
        end_date (datetime): The end date to check for due medications
    
    Returns:
        A list of due medication records
    """
    client = get_mongo_client()
    db = client["medications_db"]
    collection = db["medications"]
    
    # Get medications that are active (start_date <= now and (end_date is null or end_date >= now))
    now = datetime.now()
    medications = collection.find({
        "start_date": {"$lte": now},
        "$or": [
            {"end_date": None},
            {"end_date": {"$gte": now}}
        ]
    })
    
    # Convert to list and format for JSON serialization
    result = []
    for med in medications:
        result.append({
            "_id": str(med["_id"]),
            "name": med["name"],
            "dosage": med["dosage"],
            "frequency": med["frequency"],
            "start_date": med["start_date"].isoformat() if med.get("start_date") else None,
            "end_date": med["end_date"].isoformat() if med.get("end_date") else None,
            "time_of_day": med.get("time_of_day", []),
            "notes": med.get("notes", ""),
            "created_at": med["created_at"].isoformat() if med.get("created_at") else None
        })
    
    return result