from langchain_community.chat_models import ChatLiteLLM
from langchain_core.messages import HumanMessage, SystemMessage

from config import API_BASE_URL, API_KEY


OUTPUT_AGENT_SYSTEM_PROMPT = """
You're an agent responsible for answering the human back based on the response you get from another agent.

Be courteous and helpful in your responses.
"""

output_agent_llm = ChatLiteLLM(model="gpt-4o", api_base=API_BASE_URL, api_key=API_KEY)