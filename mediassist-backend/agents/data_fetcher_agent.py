from langchain_community.chat_models import ChatLiteLLM
from tools.tools import get_nutritional_info, get_user_profile, get_medical_conditions

from config import API_BASE_URL, API_KEY

DATA_FETCHER_AGENT_SYSTEM_PROMPT = """
You are an insights agent responsible for retrieving insights from a database.

You have the following responsibilities:
- If the user asks for daily insights, you should fetch the insights from the database.
- You should also fetch the user profile information to provide personalized insights.
- You should fetch medical conditions information to provide relevant health insights.
- Summarize it in a clear and concise manner.

Respond in the following format ONLY:
FORMAT:

User Profile:
===============
<user_profile>

Medical Conditions:
===============
<medical_conditions>

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
    api_key=API_KEY).bind_tools([get_nutritional_info, get_user_profile, get_medical_conditions])

