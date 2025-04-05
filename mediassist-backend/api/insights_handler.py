from graphs.background_graph import graph

config = {"configurable": {"thread_id": "1"}}

class InsightsHandler:
    def __init__(self):
        # Initialize any necessary components here
        pass

    def get_daily_insights(self):
        # Invoke the graph with a prompt for daily analysis
        response = graph.invoke({"messages": [{"role": "user", "content": "Provide personal daily analysis"}]}, config=config)
        return response['messages'][-1].content if response['messages'] else "No daily insights available."

    def get_weekly_insights(self):
        # Invoke the graph with a prompt for weekly analysis
        response = graph.invoke({"messages": [{"role": "user", "content": "Provide personal weekly analysis"}]}, config=config)
        return response['messages'][-1].content if response['messages'] else "No weekly insights available."
