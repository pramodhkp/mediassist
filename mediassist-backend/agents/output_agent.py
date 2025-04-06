from langchain_community.chat_models import ChatLiteLLM
from langchain_core.messages import HumanMessage, SystemMessage

from config import API_BASE_URL, API_KEY


OUTPUT_AGENT_SYSTEM_PROMPT = """
You're an agent responsible for answering the human back based on the response you get from various agents.

Based on the context of messages you have, summarize what action was taken for the input given by the user.
Then, respond back to the user with the information you have.
"""

output_agent_llm = ChatLiteLLM(model="gpt-4o", api_base=API_BASE_URL, api_key=API_KEY)