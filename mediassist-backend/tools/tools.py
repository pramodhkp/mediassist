import json
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

from datetime import datetime, timedelta
from storage.client import get_mongo_client

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

tools = [get_nutritional_info]
tool_node = ToolNode(tools)
