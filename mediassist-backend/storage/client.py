from pymongo import MongoClient
from datetime import datetime, timedelta
import os
import shutil
import uuid

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
    from bson.objectid import ObjectId
    
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