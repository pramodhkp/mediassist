from graphs.frontend_graph import graph

config = {"configurable": {"thread_id": "1"}}

class ChatHandler:
    def __init__(self):
        # Initialize any necessary components here
        pass

    def process_message(self, user_message):
        # Process the user message using the graph and filter for output_agent messages
        response = graph.invoke({"messages": [{"role": "user", "content": user_message}]}, config=config)
        return response['messages'][-1].content
