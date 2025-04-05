from langchain_community.chat_models import ChatLiteLLM

from config import API_BASE_URL, API_KEY
from storage.models import NutritionData

NUTRITION_AGENT_SYSTEM_PROMPT = """
You're an agent responsible for deriving nutritional information for the foods mentioned in the input given to you. 
Store the information in a structured format and respond back with an acknowedgement
"""

nutrition_agent_llm = ChatLiteLLM(
    model="gpt-4o", 
    api_base=API_BASE_URL, 
    api_key=API_KEY).with_structured_output(NutritionData)
