from langchain_community.chat_models import ChatLiteLLM
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Literal

from config import API_BASE_URL, API_KEY

from typing import Optional

class IntentClassification(BaseModel):
    """Classification of user intent for routing in the conversation graph."""
    intent: Literal[
        "user_profile", "nutrition", "medical_conditions", "insights", "general", # Added general from prompt examples
        "ADD_MEDICATION", "LIST_MEDICATIONS", "UPDATE_MEDICATION", 
        "DELETE_MEDICATION", "GET_DUE_MEDICATIONS", "GET_NEXT_DOSE"
    ] = Field(
        description="The classified intent of the user's message"
    )
    medication_name: Optional[str] = Field(
        None, description="The name of the medication, if relevant (e.g., for GET_NEXT_DOSE, UPDATE_MEDICATION, DELETE_MEDICATION)"
    )
    # For ADD_MEDICATION and UPDATE_MEDICATION, full details might be complex.
    # The agent might need to prompt for more info.
    # We can add more entity fields here if the LLM can reliably extract them.
    # For now, medication_name is a start.
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

1.  user_profile: Messages related to the user's profile information (age, gender, height, weight, etc.)
2.  nutrition: Messages related to inputting food information (e.g., meals, snacks, drinks).
3.  medical_conditions: Messages related to general diseases, symptoms, treatments. Note: For specific medication management, use the medication intents below.
4.  insights: Messages asking for analysis, insights, or recommendations based on their data, especially nutrition data over time.
5.  ADD_MEDICATION: Messages indicating the user wants to add a new medication to their list.
    (e.g., "I need to add a new pill called Amoxicillin", "Add a medication")
6.  LIST_MEDICATIONS: Messages asking to list their current medications.
    (e.g., "What medications am I taking?", "Show my pill list")
7.  UPDATE_MEDICATION: Messages indicating a desire to change details of an existing medication.
    (e.g., "Update the dosage for my Metformin", "I need to change my medication schedule for Lisinopril")
    If a medication name is mentioned, extract it into 'medication_name'.
8.  DELETE_MEDICATION: Messages indicating the user wants to remove a medication from their list.
    (e.g., "Remove Ibuprofen from my meds", "I'm no longer taking Aspirin")
    If a medication name is mentioned, extract it into 'medication_name'.
9.  GET_DUE_MEDICATIONS: Messages asking which medications are currently due or need to be taken soon.
    (e.g., "What pills should I take now?", "Are any of my medications due?")
10. GET_NEXT_DOSE: Messages asking about the next scheduled dose for a specific medication.
    (e.g., "When is my next dose of Metformin?", "What time do I take Lipitor next?")
    The medication name MUST be extracted into 'medication_name'. If no medication name is found, this intent should not be chosen.
11. general: Messages that do not fit into any of the above categories, or are general conversation.
    (e.g., "Hello", "How are you?", "What's the weather like?")

Examples:
- "I am 35 years old and weigh 70kg" → intent: user_profile
- "I had a salad for lunch today" → intent: nutrition
- "I have a headache" → intent: medical_conditions
- "How's my food intake looking for the past week?" → intent: insights
- "Add a new medication, it's called Crestor." → intent: ADD_MEDICATION, medication_name: Crestor (Optional for ADD, agent can ask)
- "What pills am I on?" → intent: LIST_MEDICATIONS
- "I need to change the reminder for my Plavix." → intent: UPDATE_MEDICATION, medication_name: Plavix
- "Please remove Warfarin." → intent: DELETE_MEDICATION, medication_name: Warfarin
- "Are any meds due?" → intent: GET_DUE_MEDICATIONS
- "When should I take my Advil next?" → intent: GET_NEXT_DOSE, medication_name: Advil
- "What's the capital of France?" → intent: general

Provide your classification with a confidence score, the extracted 'medication_name' if applicable, and a brief explanation of your reasoning.
If a medication name is clearly part of an ADD, UPDATE, or DELETE intent, extract it.
For GET_NEXT_DOSE, extracting medication_name is mandatory.
"""

intent_classifier_llm = ChatLiteLLM(
    model="gpt-4o", 
    api_base=API_BASE_URL, 
    api_key=API_KEY).with_structured_output(IntentClassification)