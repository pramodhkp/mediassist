from langchain_core.pydantic_v1 import BaseModel, Field
from datetime import datetime

class NutritionData(BaseModel):
    food_name: str
    calories: float
    protein: float
    carbohydrates: float
    fats: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class MedicalConditionData(BaseModel):
    condition_name: str
    symptoms: str
    treatment: str
    prevention: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)