import json
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

from datetime import datetime, timedelta
from storage.client import get_mongo_client, get_user_profile_data

@tool(parse_docstring=True)
def get_nutritional_info(time_range: str) -> str:
    """Fetches nutritional information from the DB

    Args:
        time_range: daily or weekly
    """
    # MongoDB connection setup
    client = get_mongo_client()
    db = client["nutrition_db"]
    collection = db["nutrition_data"]
    # Fetch data from the collection
    if time_range == "daily":
        data = collection.find({"timestamp": {"$gte": datetime.utcnow() - timedelta(days=1)}})
        return json.dumps(list(data), default=str)
    elif time_range == "weekly":
        data = collection.find({"timestamp": {"$gte": datetime.utcnow() - timedelta(weeks=1)}})
        return json.dumps(list(data), default=str)
    else:
        return "Invalid time range. Please specify 'daily' or 'weekly'."

@tool(parse_docstring=True)
def get_user_profile() -> str:
    """Fetches the user profile information from the DB
    """
    # Get user profile data
    profile_data = get_user_profile_data()
    return json.dumps(profile_data, default=str) if profile_data else "{}"

@tool(parse_docstring=True)
def get_medical_conditions(condition_type: str = None) -> str:
    """Fetches medical conditions information from the DB

    Args:
        condition_type: Optional. Filter by 'temporary' or 'chronic'. If not provided, returns all conditions.
    """
    # MongoDB connection setup
    client = get_mongo_client()
    db = client["medical_conditions_db"]
    collection = db["medical_conditions_data"]
    
    # Fetch data from the collection
    if condition_type and condition_type.lower() in ['temporary', 'chronic']:
        # If condition_type is provided, filter by it
        data = collection.find({"condition_type": condition_type.lower()})
    else:
        # Otherwise, return all conditions
        data = collection.find({})
    
    return json.dumps(list(data), default=str)

tools = [get_nutritional_info, get_user_profile, get_medical_conditions]
tool_node = ToolNode(tools)
