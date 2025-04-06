from langchain_core.pydantic_v1 import BaseModel, Field
from datetime import datetime
from typing import Optional

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

class UserProfileData(BaseModel):
    age: int = None
    gender: str = None
    height: float = None  # in cm
    weight: float = None  # in kg
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class InsightsData(BaseModel):
    analysis_type: str  # "daily" or "weekly"
    content: str  # The actual insights content
    date: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = {}  # Optional metadata about the insights

class MedicalReportData(BaseModel):
    filename: str
    file_type: str
    file_size: int
    description: Optional[str] = None
    uploadDate: datetime = Field(default_factory=datetime.utcnow)