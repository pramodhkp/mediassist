from graphs.background_graph import graph
from storage.client import store_insights_data, get_daily_insights_for_range
from datetime import datetime, timedelta

config = {"configurable": {"thread_id": "1"}}

class InsightsHandler:
    def __init__(self):
        # Initialize any necessary components here
        pass

    def get_daily_insights(self):
        """
        Generates daily insights.
        
        Returns:
            str: The daily insights content
        """
        # Invoke the graph with a prompt for daily analysis
        response = graph.invoke({"messages": [{"role": "user", "content": "Provide personal daily analysis"}]}, config=config)
        return response['messages'][-1].content if response['messages'] else "No daily insights available."

    def get_weekly_insights(self):
        """
        Generates weekly insights, potentially using stored daily insights from the past week.
        
        Returns:
            str: The weekly insights content
        """
        # Get daily insights for the past week
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        daily_insights = get_daily_insights_for_range(start_date, end_date)
        
        # If we have daily insights, use them to generate weekly insights
        if daily_insights:
            # Prepare a prompt that includes the daily insights
            daily_insights_text = "\n\n".join([insight["content"] for insight in daily_insights])
            prompt = f"Generate weekly insights based on the following daily insights from the past week:\n\n{daily_insights_text}"
            
            # Invoke the graph with the prepared prompt
            response = graph.invoke({"messages": [{"role": "user", "content": prompt}]}, config=config)
        else:
            # If no daily insights are available, generate weekly insights directly
            response = graph.invoke({"messages": [{"role": "user", "content": "Provide personal weekly analysis"}]}, config=config)
        
        return response['messages'][-1].content if response['messages'] else "No weekly insights available."
    
    def store_daily_insights(self):
        """
        Generates and stores daily insights in the database.
        This method is intended to be called by a scheduler, not directly by API routes.
        
        Returns:
            str: The ID of the stored insights document
        """
        # Generate daily insights
        content = self.get_daily_insights()
        
        # Store the daily insights in the database
        insights_data = {
            "analysis_type": "daily",
            "content": content,
            "date": datetime.utcnow(),
            "metadata": {}
        }
        return store_insights_data(insights_data)
    
    def store_weekly_insights(self):
        """
        Generates and stores weekly insights in the database.
        This method is intended to be called by a scheduler, not directly by API routes.
        
        Returns:
            str: The ID of the stored insights document
        """
        # Generate weekly insights
        content = self.get_weekly_insights()
        
        # Store the weekly insights in the database
        insights_data = {
            "analysis_type": "weekly",
            "content": content,
            "date": datetime.utcnow(),
            "metadata": {}
        }
        return store_insights_data(insights_data)
