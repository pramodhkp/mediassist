from graphs.user_profile_graph import graph

config = {"configurable": {"thread_id": "user_profile"}}

class UserProfileHandler:
    def __init__(self):
        """
        Initialize the UserProfileHandler.
        """
        pass

    def process_profile_message(self, user_message):
        """
        Process a user message related to profile information.
        
        Args:
            user_message (str): The message from the user containing profile information.
            
        Returns:
            str: The response from the user profile agent.
        """
        # Process the user message using the graph
        response = graph.invoke({"messages": [{"role": "user", "content": user_message}]}, config=config)
        return response['messages'][-1].content