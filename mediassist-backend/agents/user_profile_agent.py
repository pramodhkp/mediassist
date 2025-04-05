from langchain_community.chat_models import ChatLiteLLM

from config import API_BASE_URL, API_KEY
from storage.models import UserProfileData


USER_PROFILE_AGENT_SYSTEM_PROMPT = """
You're an agent responsible for extracting user profile information from conversational inputs.
Extract the following information if available:
- Age (in years)
- Gender (male, female, or other)
- Height (in cm)
- Weight (in kg)

Only extract the information that is explicitly mentioned in the user's message.
If a field is not mentioned, return null for that field.
For example, if the user only mentions their age and height, only extract those values and leave gender and weight as null.

Convert any units as needed (e.g., if height is given in feet and inches, convert to cm).
Store the information in a structured format and respond with a friendly acknowledgment.
"""

user_profile_agent_llm = ChatLiteLLM(
    model="gpt-4o", 
    api_base=API_BASE_URL, 
    api_key=API_KEY).with_structured_output(UserProfileData)