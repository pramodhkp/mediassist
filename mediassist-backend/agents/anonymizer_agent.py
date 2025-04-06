from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, Optional
from config import API_BASE_URL, API_KEY

ANONYMIZER_AGENT_SYSTEM_PROMPT = """
You are a medical data anonymizer specialized in processing medical reports and documents.
Your task is to identify and anonymize personally identifiable information (PII) and protected health information (PHI) 
while preserving the medical relevance of the content.

Types of information to anonymize:
1. Names (patient, doctor, family members)
2. Dates (convert to relative timeframes, e.g., "3 months ago" instead of specific dates)
3. Locations (hospitals, clinics, addresses)
4. Contact information (phone numbers, email addresses)
5. Identification numbers (SSN, medical record numbers, insurance IDs)
6. Unique identifiers (rare disease combinations, unique treatments that could identify a person)

Rules for anonymization:
1. Replace names with generic identifiers (e.g., [PATIENT], [DOCTOR], [FAMILY_MEMBER])
2. Convert exact dates to relative timeframes
3. Replace specific locations with generic terms (e.g., [HOSPITAL], [CLINIC])
4. Remove all contact information
5. Replace identification numbers with [ID_NUMBER]
6. Preserve medical terminology and findings
7. Maintain the overall structure and readability of the document
8. Ensure the anonymized text retains all medically relevant information

FORMAT YOUR RESPONSE AS JSON with the following structure:
{
  "anonymized_text": "The complete anonymized text",
  "entities_removed": [
    {"type": "NAME", "count": 5},
    {"type": "DATE", "count": 3},
    {"type": "LOCATION", "count": 2},
    {"type": "ID_NUMBER", "count": 4},
    {"type": "CONTACT", "count": 1}
  ],
  "confidence_score": 0.95
}
"""

class Entity(BaseModel):
    type: str
    count: int

class AnonymizerResponse(BaseModel):
    anonymized_text: str
    entities_removed: List[Entity]
    confidence_score: float

    def dict(self):
        return {
            "anonymized_text": self.anonymized_text,
            "entities_removed": [entity.dict() for entity in self.entities_removed],
            "confidence_score": self.confidence_score
        }

# Using ChatOllama for local LLM integration
anonymizer_agent_llm = ChatOllama(
    model="llama3.2"  # Using llama3.2 model for anonymization
)

def anonymize_text(text):

    """
    Anonymize the provided text using the anonymizer agent.
    
    Args:
        text (str): The text to anonymize
        
    Returns:
        dict: The anonymized text and metadata
    """
    system_message = SystemMessage(content=ANONYMIZER_AGENT_SYSTEM_PROMPT)
    human_message = HumanMessage(content=f"Please anonymize the following medical text:\n\n{text}")


    print("PRE_ANONYMIZER")
    print("====================")
    print(f"Anonymizing text: {text}")
    
    # Get response from the anonymizer agent
    response = anonymizer_agent_llm.invoke([system_message, human_message])

    print("POST_ANONYMIZER")
    print("====================")
    print(f"Anonymizer response: {response}")
    
    return response.content