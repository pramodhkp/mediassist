from langchain_community.chat_models import ChatLiteLLM
from tools.tools import get_nutritional_info

from config import API_BASE_URL, API_KEY

DATA_FETCHER_AGENT_SYSTEM_PROMPT = """
You are an insights agent responsible for retrieving insights from a database. 

You have the following responsibilities:
- If the user asks for daily insights, you should fetch the insights from the database.
- Summarize it in a clear and concise manner.

Respond in the following format ONLY:
FORMAT:

Daily insights:
===============
<daily_insights>

Weekly insights:
===============
<weekly_insights>
"""

data_fetcher_agent_llm = ChatLiteLLM(
    model="gpt-4o", 
    api_base=API_BASE_URL, 
    api_key=API_KEY).bind_tools([get_nutritional_info])

