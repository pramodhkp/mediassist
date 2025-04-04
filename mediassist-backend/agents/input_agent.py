from langchain_community.chat_models import ChatLiteLLM
from langchain_core.messages import HumanMessage, SystemMessage

from config import API_BASE_URL, API_KEY

INPUT_AGENT_SYSTEM_PROMPT = """
You're responsible for taking inputs from the user and understand the intent behind it.

A user can have a input or question for you. Respond in the following format: 

USER_INTENT: "input" || "question"
DETAILS: <user's prompt>

"""

input_agent_llm = ChatLiteLLM(model="gpt-4o", api_base=API_BASE_URL, api_key=API_KEY)