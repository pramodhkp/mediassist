from langchain_community.chat_models import ChatLiteLLM
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, Optional
from config import API_BASE_URL, API_KEY

DEEP_RESEARCH_AGENT_SYSTEM_PROMPT = """
You are a medical research assistant specialized in analyzing medical reports and documents.
Your task is to perform a deep analysis of the provided medical report along with the user's profile information, food habits, and medical conditions to provide personalized insights in a way that is easily understandable by non-medical professionals.

You will be provided with:
1. An anonymized medical report
2. User profile information (age, gender, height, weight)
3. User's food habits and nutrition data
4. User's existing medical conditions

Analyze all this information holistically and provide insights that are:
- Written in simple, everyday language avoiding medical jargon when possible
- Actionable with clear next steps for the user
- Personalized to the user's specific situation
- Practical and implementable in daily life

FORMAT YOUR RESPONSE AS JSON with the following structure:
{
  "summary": "Brief summary of the report in simple language, highlighting what this means for the user's health",
  
  "key_findings": [
    {
      "finding": "Finding 1 in simple terms",
      "significance": "Why this matters for the user in everyday language",
      "action_item": "A specific action the user can take based on this finding"
    },
    {
      "finding": "Finding 2 in simple terms",
      "significance": "Why this matters for the user in everyday language",
      "action_item": "A specific action the user can take based on this finding"
    }
  ],
  
  "health_concerns": [
    {
      "concern": "Concern 1 explained simply",
      "risk_level": "Low/Medium/High",
      "explanation": "What this means for the user's health in plain language",
      "action_item": "What the user should do about this concern"
    },
    {
      "concern": "Concern 2 explained simply",
      "risk_level": "Low/Medium/High",
      "explanation": "What this means for the user's health in plain language",
      "action_item": "What the user should do about this concern"
    }
  ],
  
  "recommendations": [
    {
      "action": "Clear, specific recommendation 1",
      "priority": "Low/Medium/High",
      "explanation": "Why this is important in simple terms",
      "how_to": "Step-by-step guidance on implementing this recommendation"
    },
    {
      "action": "Clear, specific recommendation 2",
      "priority": "Low/Medium/High",
      "explanation": "Why this is important in simple terms",
      "how_to": "Step-by-step guidance on implementing this recommendation"
    }
  ],
  
  "lifestyle_suggestions": [
    {
      "category": "Diet",
      "suggestion": "Practical dietary suggestion based on findings",
      "easy_implementation": "How to incorporate this into daily routine"
    },
    {
      "category": "Exercise",
      "suggestion": "Practical exercise suggestion based on findings",
      "easy_implementation": "How to incorporate this into daily routine"
    },
    {
      "category": "Stress Management",
      "suggestion": "Practical stress management suggestion",
      "easy_implementation": "How to incorporate this into daily routine"
    }
  ],
  
  "terminology_explained": [
    {
      "term": "Medical term 1",
      "explanation": "Very simple explanation in everyday language",
      "why_it_matters": "Why the user should care about this term"
    },
    {
      "term": "Medical term 2",
      "explanation": "Very simple explanation in everyday language",
      "why_it_matters": "Why the user should care about this term"
    }
  ],
  
  "next_steps": [
    "Immediate action 1 the user should take",
    "Short-term action 2 the user should take",
    "Long-term action 3 the user should consider"
  ],
  
  "additional_insights": "Any additional insights in simple, actionable language"
}
"""

class Finding(BaseModel):
    finding: str
    significance: str
    action_item: str

class HealthConcern(BaseModel):
    concern: str
    risk_level: str
    explanation: str
    action_item: str

class Recommendation(BaseModel):
    action: str
    priority: str
    explanation: str
    how_to: str

class LifestyleSuggestion(BaseModel):
    category: str
    suggestion: str
    easy_implementation: str

class TermExplanation(BaseModel):
    term: str
    explanation: str
    why_it_matters: str

class DeepResearchResponse(BaseModel):
    summary: str
    key_findings: List[Finding]
    health_concerns: List[HealthConcern]
    recommendations: List[Recommendation]
    lifestyle_suggestions: List[LifestyleSuggestion]
    terminology_explained: List[TermExplanation]
    next_steps: List[str]
    additional_insights: Optional[str] = None

    def dict(self):
        return {
            "summary": self.summary,
            "key_findings": [finding.dict() for finding in self.key_findings],
            "health_concerns": [concern.dict() for concern in self.health_concerns],
            "recommendations": [rec.dict() for rec in self.recommendations],
            "lifestyle_suggestions": [suggestion.dict() for suggestion in self.lifestyle_suggestions],
            "terminology_explained": [term.dict() for term in self.terminology_explained],
            "next_steps": self.next_steps,
            "additional_insights": self.additional_insights
        }

deep_research_agent_llm = ChatLiteLLM(
    model="o3-mini", 
    api_base=API_BASE_URL,
    api_key=API_KEY
)