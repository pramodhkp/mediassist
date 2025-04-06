from langchain_community.chat_models import ChatLiteLLM
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Literal

from config import API_BASE_URL, API_KEY

class IntentClassification(BaseModel):
    """Classification of user intent for routing in the conversation graph."""
    intent: Literal["user_profile", "nutrition", "medical_conditions", "insights"] = Field(
        description="The classified intent of the user's message"
    )
    confidence: float = Field(
        description="Confidence score for the classification (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    explanation: str = Field(
        description="Brief explanation of why this intent was chosen"
    )

INTENT_CLASSIFIER_SYSTEM_PROMPT = """
You are an intent classification agent responsible for determining the user's intent from their message.
Your task is to classify the intent into one of the following categories:

1. user_profile: Messages related to the user's profile information (age, gender, height, weight, etc.)
2. nutrition: Messages related to inputting food information (e.g., meals, snacks, drinks)
3. medical_conditions: Messages related to diseases, symptoms, treatments, medications, etc.
4. data_fetcher: Messages asking for analysis, insights, or recommendations based on their data, especially nutrition data over time

Examples:
- "I am 35 years old and weigh 70kg" → user_profile
- "I had a salad for lunch today" → nutrition
- "I have diabetes" → medical_conditions
- "How's my food intake looking for the past week?" → insights
- "What's the weather like today?" → general

Provide your classification with a confidence score and a brief explanation of your reasoning.
"""

intent_classifier_llm = ChatLiteLLM(
    model="gpt-4o", 
    api_base=API_BASE_URL, 
    api_key=API_KEY).with_structured_output(IntentClassification)