from langchain_community.chat_models import ChatLiteLLM

from config import API_BASE_URL, API_KEY

MEDICAL_CONDITIONS_AGENT_SYSTEM_PROMPT = """
You're an agent responsible for providing information about medical conditions based on the user's input.
"""

medical_conditions_agent_llm = ChatLiteLLM(model="gpt-4o", api_base=API_BASE_URL, api_key=API_KEY)