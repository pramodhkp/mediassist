import sys
import os
import json
import random
import requests
from datetime import datetime, timedelta

# Add the mediassist-backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from storage.client import get_mongo_client, store_nutrition_data, store_medical_conditions_data, store_user_profile_data
from storage.models import NutritionData, MedicalConditionData, UserProfileData

# Configuration
API_URL = "http://localhost:5000"
DAYS_TO_GENERATE = 14  # Two weeks of data

# Sample food items with nutritional values
FOOD_ITEMS = [
    {"name": "Oatmeal", "calories": 150, "protein": 5, "carbs": 27, "fats": 3},
    {"name": "Scrambled Eggs", "calories": 140, "protein": 12, "carbs": 1, "fats": 10},
    {"name": "Whole Wheat Toast", "calories": 80, "protein": 3, "carbs": 15, "fats": 1},
    {"name": "Banana", "calories": 105, "protein": 1, "carbs": 27, "fats": 0},
    {"name": "Greek Yogurt", "calories": 100, "protein": 17, "carbs": 6, "fats": 0},
    {"name": "Chicken Breast", "calories": 165, "protein": 31, "carbs": 0, "fats": 3.6},
    {"name": "Brown Rice", "calories": 215, "protein": 5, "carbs": 45, "fats": 1.8},
    {"name": "Broccoli", "calories": 55, "protein": 3.7, "carbs": 11, "fats": 0.6},
    {"name": "Salmon", "calories": 206, "protein": 22, "carbs": 0, "fats": 13},
    {"name": "Sweet Potato", "calories": 112, "protein": 2, "carbs": 26, "fats": 0.1},
    {"name": "Quinoa", "calories": 222, "protein": 8, "carbs": 39, "fats": 3.6},
    {"name": "Avocado", "calories": 234, "protein": 2.9, "carbs": 12, "fats": 21},
    {"name": "Almonds", "calories": 164, "protein": 6, "carbs": 6, "fats": 14},
    {"name": "Apple", "calories": 95, "protein": 0.5, "carbs": 25, "fats": 0.3},
    {"name": "Lentil Soup", "calories": 230, "protein": 18, "carbs": 40, "fats": 0.8}
]

# Sample medical conditions
MEDICAL_CONDITIONS = [
    {
        "name": "Common Cold",
        "symptoms": "Runny nose, sore throat, coughing, mild fever",
        "treatment": "Rest, fluids, over-the-counter cold medications",
        "prevention": "Regular handwashing, avoiding close contact with sick individuals",
        "type": "temporary"
    },
    {
        "name": "Seasonal Allergies",
        "symptoms": "Sneezing, itchy eyes, congestion, runny nose",
        "treatment": "Antihistamines, nasal sprays, avoiding allergens",
        "prevention": "Identifying and avoiding triggers, air purifiers",
        "type": "temporary"
    },
    {
        "name": "Hypertension",
        "symptoms": "Usually asymptomatic, occasional headaches, shortness of breath",
        "treatment": "Medication, lifestyle changes, regular monitoring",
        "prevention": "Low-sodium diet, regular exercise, stress management",
        "type": "chronic"
    },
    {
        "name": "Type 2 Diabetes",
        "symptoms": "Increased thirst, frequent urination, fatigue, blurred vision",
        "treatment": "Medication, insulin therapy, blood sugar monitoring, diet management",
        "prevention": "Healthy diet, regular exercise, weight management",
        "type": "chronic"
    }
]

def generate_user_profile():
    """Generate a mock user profile"""
    print("Generating user profile...")
    
    user_profile = UserProfileData(
        age=35,
        gender="male",
        height=175.0,  # cm
        weight=70.0,   # kg
        timestamp=datetime.utcnow()
    )
    
    # Store the user profile
    store_user_profile_data(user_profile.dict())
    print("User profile generated and stored.")
    
    return user_profile

def generate_nutrition_data(days):
    """Generate mock nutrition data for the specified number of days"""
    print(f"Generating nutrition data for the past {days} days...")
    
    nutrition_data = []
    
    for day in range(days, 0, -1):
        # Generate data for this day
        date = datetime.utcnow() - timedelta(days=day)
        
        # Generate 3-5 food items for this day
        num_items = random.randint(3, 5)
        for _ in range(num_items):
            food = random.choice(FOOD_ITEMS)
            
            # Add some randomness to the nutritional values
            variation = random.uniform(0.9, 1.1)  # +/- 10%
            
            data = NutritionData(
                food_name=food["name"],
                calories=food["calories"] * variation,
                protein=food["protein"] * variation,
                carbohydrates=food["carbs"] * variation,
                fats=food["fats"] * variation,
                timestamp=date.replace(
                    hour=random.randint(6, 20),
                    minute=random.randint(0, 59)
                )
            )
            
            # Store the nutrition data
            store_nutrition_data(data.dict())
            nutrition_data.append(data)
    
    print(f"Generated and stored {len(nutrition_data)} nutrition data entries.")
    return nutrition_data

def generate_medical_conditions(days):
    """Generate mock medical condition data for the specified number of days"""
    print(f"Generating medical condition data for the past {days} days...")
    
    medical_data = []
    
    # Add one chronic condition at the beginning
    chronic_condition = next(c for c in MEDICAL_CONDITIONS if c["type"] == "chronic")
    date = datetime.utcnow() - timedelta(days=days)
    
    data = MedicalConditionData(
        condition_name=chronic_condition["name"],
        symptoms=chronic_condition["symptoms"],
        treatment=chronic_condition["treatment"],
        prevention=chronic_condition["prevention"],
        timestamp=date
    )
    
    # Store the medical condition data
    store_medical_conditions_data(data.dict())
    medical_data.append(data)
    
    # Add 1-2 temporary conditions randomly throughout the period
    num_temp_conditions = random.randint(1, 2)
    temp_conditions = [c for c in MEDICAL_CONDITIONS if c["type"] == "temporary"]
    
    for _ in range(num_temp_conditions):
        day = random.randint(1, days-1)
        date = datetime.utcnow() - timedelta(days=day)
        condition = random.choice(temp_conditions)
        
        data = MedicalConditionData(
            condition_name=condition["name"],
            symptoms=condition["symptoms"],
            treatment=condition["treatment"],
            prevention=condition["prevention"],
            timestamp=date
        )
        
        # Store the medical condition data
        store_medical_conditions_data(data.dict())
        medical_data.append(data)
    
    print(f"Generated and stored {len(medical_data)} medical condition entries.")
    return medical_data

def generate_insights():
    """Generate and store insights based on the mock data"""
    print("Generating insights based on mock data...")
    
    try:
        # Call the API to generate and store insights
        response = requests.post(
            f"{API_URL}/generate_and_store_insights",
            json={"type": "both"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Successfully generated insights: {json.dumps(result, indent=2)}")
            return result
        else:
            print(f"Failed to generate insights. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error generating insights: {e}")
        return None

def main():
    """Main function to generate all mock data and insights"""
    print("Starting demo data generation...")
    
    # Generate user profile
    user_profile = generate_user_profile()
    
    # Generate nutrition data for the past two weeks
    nutrition_data = generate_nutrition_data(DAYS_TO_GENERATE)
    
    # Generate medical condition data
    medical_data = generate_medical_conditions(DAYS_TO_GENERATE)
    
    # Generate insights based on the mock data
    insights_result = generate_insights()
    
    print("\nDemo data generation complete!")
    print(f"- User profile created: Age {user_profile.age}, Gender {user_profile.gender}")
    print(f"- {len(nutrition_data)} nutrition entries created")
    print(f"- {len(medical_data)} medical condition entries created")
    
    if insights_result and insights_result.get("success"):
        print("- Insights successfully generated and stored")
    else:
        print("- Failed to generate insights")
    
    print("\nYou can now access the insights through the API endpoints:")
    print(f"- Daily insights: {API_URL}/daily_insights")
    print(f"- Weekly insights: {API_URL}/weekly_insights")

if __name__ == "__main__":
    main()