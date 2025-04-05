from langchain_community.chat_models import ChatLiteLLM
from tools.tools import get_nutritional_info

from config import API_BASE_URL, API_KEY

INSIGHTS_AGENT_SYSTEM_PROMPT = """
You are an insights agent responsible for retrieving insights from a database. 
Your task is to process user queries, make appropriate database calls to fetch the required insights, and return the results in a clear and concise manner.
Ensure accuracy and relevance in your responses.

Respond in the following format ONLY:
FORMAT:

Daily insights:
===============
<daily_insights>

Weekly insights:
===============
<weekly_insights>
"""

insights_agent_llm = ChatLiteLLM(
    model="gpt-4o", 
    api_base=API_BASE_URL, 
    api_key=API_KEY).bind_tools([get_nutritional_info])

