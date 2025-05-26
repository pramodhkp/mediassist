from .intent_classifier_agent import IntentClassification # To understand the input
from .medication_agent import MedicationAgent
# Import other agents if they exist and are to be used by this orchestrator
# from .nutrition_agent import NutritionAgent # Example
# from .user_profile_agent import UserProfileAgent # Example
# from .medical_conditions_agent import MedicalConditionsAgent # Example

class OrchestratorAgent:
    def __init__(self, user_id: str):
        self.user_id = user_id
        # Initialize other agents if they are stateful and reused across requests for the same user.
        # MedicationAgent is instantiated per call as it's lightweight and uses user_id in its calls.

    def _get_medication_id_from_name(self, med_agent: MedicationAgent, medication_name: str) -> str | None:
        """
        Helper to try and find a medication ID by its name.
        This is a placeholder for a more robust lookup.
        It assumes names are unique for simplicity or takes the first match.
        IMPORTANT: This helper is currently INEFFECTIVE because med_agent.list_medications() returns a string,
        not structured data. This needs to be addressed for robust ID lookup.
        """
        # print(f"[Orchestrator Helper] _get_medication_id_from_name: Called for '{medication_name}'.")
        # print(f"[Orchestrator Helper] Current MedicationAgent.list_medications() returns a string, making ID lookup by name unreliable here.")
        # To make this work, MedicationAgent would need a method like get_medications_structured()
        # or list_medications() would need an optional parameter to return structured data.
        # For now, this will not work as intended.
        return None


    def route_request(self, classified_intent: IntentClassification, user_message: str) -> str:
        """
        Routes the user's request to the appropriate agent based on the classified intent.
        
        Args:
            classified_intent: The output from the IntentClassifierAgent.
            user_message: The original message from the user. (Currently unused, but could be useful)
            
        Returns:
            A string response from the called agent.
        """
        intent = classified_intent.intent
        medication_name_from_intent = classified_intent.medication_name
        
        response = f"Debug: Orchestrator for user '{self.user_id}' received intent '{intent}'."

        # Instantiate MedicationAgent here to be used by medication-related intents
        med_agent = MedicationAgent(user_id=self.user_id)

        if intent == "ADD_MEDICATION":
            # The MedicationAgent.add_medication expects a dictionary with details.
            # The IntentClassifierAgent currently only extracts medication_name (optional).
            # 'start_date' is a required field for the Medication model.
            # This implies a multi-step process or more advanced entity extraction.
            if medication_name_from_intent:
                response = (f"Okay, you want to add '{medication_name_from_intent}'. "
                            "To do this, I need some more details like the dosage, frequency, and especially the start date (YYYY-MM-DD). "
                            "Can you please provide these details?")
            else:
                response = ("You want to add a new medication. "
                            "What is the name of the medication? "
                            "Please also include its dosage, frequency, and start date (YYYY-MM-DD).")
            # Actual call to med_agent.add_medication(med_details_dict) would happen
            # after gathering all required details, possibly in a subsequent turn.

        elif intent == "LIST_MEDICATIONS":
            response = med_agent.list_medications()
            
        elif intent == "UPDATE_MEDICATION":
            # UPDATE requires medication_id and a dictionary of updates.
            # The IntentClassifier provides medication_name. An ID lookup is needed.
            if not medication_name_from_intent:
                response = "Please specify which medication you want to update (e.g., by name) and what the changes are."
            else:
                # medication_id = self._get_medication_id_from_name(med_agent, medication_name_from_intent) # Ineffective
                # As _get_medication_id_from_name is not functional, we guide the user:
                response = (f"You want to update '{medication_name_from_intent}'. "
                            "I'll need its specific ID from your medication list and the details of the changes "
                            "(e.g., new dosage, frequency). "
                            "You can use 'list medications' to find the ID. "
                            "What is the ID and what are the changes you'd like to make?")
                # If ID were available:
                # response = f"What specific details of {medication_name_from_intent} (ID: {medication_id}) would you like to update, and what are the new values?"
                # Then, after getting update details: med_agent.update_medication(medication_id, updates_dict)

        elif intent == "DELETE_MEDICATION":
            if not medication_name_from_intent:
                response = "Please specify which medication you want to delete, for example, by its name."
            else:
                # medication_id = self._get_medication_id_from_name(med_agent, medication_name_from_intent) # Ineffective
                # As _get_medication_id_from_name is not functional:
                response = (f"You want to delete '{medication_name_from_intent}'. "
                            "To confirm this, I need its specific ID from your medication list. "
                            "You can use 'list medications' to find the ID. "
                            "Once you have the ID, please confirm if you want to delete it.")
                # If ID were available: med_agent.delete_medication(medication_id)

        elif intent == "GET_DUE_MEDICATIONS":
            response = med_agent.get_due_medications()
            
        elif intent == "GET_NEXT_DOSE":
            if medication_name_from_intent:
                response = med_agent.get_next_dose_info(medication_name_from_intent)
            else:
                response = "Please tell me the name of the medication to check its next dose."
                
        # Handling for other intents (non-medication related)
        elif intent == "user_profile":
            response = f"User Profile intent for user '{self.user_id}' received. Agent/handler for this is not fully implemented in this orchestrator."
        elif intent == "nutrition":
            response = f"Nutrition intent for user '{self.user_id}' received. Agent/handler for this is not fully implemented in this orchestrator."
        elif intent == "medical_conditions":
            response = f"Medical Conditions intent for user '{self.user_id}' received. Agent/handler for this is not fully implemented in this orchestrator."
        elif intent == "insights":
            response = f"Insights intent for user '{self.user_id}' received. Agent/handler for this is not fully implemented in this orchestrator."
        elif intent == "general":
            response = "Thanks for your message. How can I assist you today with your health, nutrition, or medication management?"
        else:
            # This case should ideally not be reached if IntentClassifierAgent is comprehensive
            response = f"The intent '{intent}' is recognized but no specific handler is available."
            
        return response

# Conceptual example (not executed by the tool environment)
# if __name__ == '__main__':
#     # This block is for illustration.
#     # Assume user_id is known, and IntentClassifierAgent has run.
#     current_user_id = "test_user_123"
#     orchestrator = OrchestratorAgent(user_id=current_user_id)

#     # --- Scenario 1: Get Next Dose ---
#     mock_intent_next_dose = IntentClassification(
#         intent="GET_NEXT_DOSE",
#         medication_name="Lipitor", # Extracted by IntentClassifier
#         confidence=0.98,
#         explanation="User wants to know next dose time for Lipitor."
#     )
#     response_next_dose = orchestrator.route_request(mock_intent_next_dose, "When is my next Lipitor?")
#     print(f"Response for GET_NEXT_DOSE ('Lipitor'):\n{response_next_dose}\n")
#     # Expected: Something like "Your next dose of 'Lipitor' is at HH:MM today/tomorrow." or "Medication 'Lipitor' not found."

#     # --- Scenario 2: Add Medication (initial query) ---
#     mock_intent_add = IntentClassification(
#         intent="ADD_MEDICATION",
#         medication_name="Metformin", # Optionally extracted
#         confidence=0.92,
#         explanation="User wants to add Metformin."
#     )
#     response_add = orchestrator.route_request(mock_intent_add, "I need to add Metformin.")
#     print(f"Response for ADD_MEDICATION ('Metformin'):\n{response_add}\n")
#     # Expected: A message asking for more details (dosage, frequency, start_date) for Metformin.
    
#     # --- Scenario 3: List Medications ---
#     mock_intent_list = IntentClassification(
#         intent="LIST_MEDICATIONS",
#         confidence=0.99,
#         explanation="User wants to list their medications."
#     )
#     response_list = orchestrator.route_request(mock_intent_list, "Show my pills.")
#     print(f"Response for LIST_MEDICATIONS:\n{response_list}\n")
#     # Expected: A formatted string of medications or "You have no medications listed."

#     # --- Scenario 4: Update Medication (initial query) ---
#     mock_intent_update = IntentClassification(
#         intent="UPDATE_MEDICATION",
#         medication_name="Lisinopril", # Optionally extracted
#         confidence=0.88,
#         explanation="User wants to update Lisinopril."
#     )
#     response_update = orchestrator.route_request(mock_intent_update, "I need to change my Lisinopril.")
#     print(f"Response for UPDATE_MEDICATION ('Lisinopril'):\n{response_update}\n")
#     # Expected: A message asking for the medication ID and specific changes for Lisinopril.
```
