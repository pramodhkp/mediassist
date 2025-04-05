from langchain_community.chat_models import ChatLiteLLM

from config import API_BASE_URL, API_KEY

ORCHESTRATOR_SYSTEM_PROMPT = """
You're an orchestrating agent. You redirect request between various other agents and tools depending on the user intent.

You'll recieve an input in the following format:
```
USER_INTENT: "input" || "question" || "greeting"
DETAILS: <user's prompt>
```

You have the following agents to redirect to: [nutrition_agent, medical_conditions_agent, user_profile_agent]

Redirect to `nutrition_agent` if the user intent is "input" and the details are related to food.
Redirect to `medical_conditions_agent` if the user intent is "input" and the details are related to medical history/conditions.
Redirect to `user_profile_agent` if the user intent is "input" and the details are related to user profile information (age, gender, height, weight).

Redirect to `output_agent` if the user intent is "question" or "greeting".

Response format: "nutrition_agent" || "medical_conditions_agent" || "user_profile_agent" || "output_agent"
"""

orchestrator_agent_llm = ChatLiteLLM(model="gpt-4o", api_base=API_BASE_URL, api_key=API_KEY)