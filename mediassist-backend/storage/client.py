from pymongo import MongoClient

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