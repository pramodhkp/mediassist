import sys
import os
import time
import threading
import schedule
from datetime import datetime

# Add the mediassist-backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.insights_handler import InsightsHandler

class InsightsScheduler:
    def __init__(self):
        self.insights_handler = InsightsHandler()
        self.running = False
        self.scheduler_thread = None
    
    def start(self):
        """
        Start the scheduler in a separate thread.
        """
        if self.running:
            print("Scheduler is already running.")
            return
        
        # Schedule daily insights generation at midnight
        schedule.every().day.at("00:00").do(self._store_daily_insights)
        
        # Schedule weekly insights generation at midnight on Sundays
        schedule.every().sunday.at("00:00").do(self._store_weekly_insights)
        
        # Start the scheduler in a separate thread
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler)
        self.scheduler_thread.daemon = True  # Set as daemon so it will exit when the main program exits
        self.scheduler_thread.start()
        
        print(f"Insights scheduler started at {datetime.now()}")
    
    def stop(self):
        """
        Stop the scheduler.
        """
        if not self.running:
            print("Scheduler is not running.")
            return
        
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=1)
        
        print(f"Insights scheduler stopped at {datetime.now()}")
    
    def _run_scheduler(self):
        """
        Run the scheduler loop.
        """
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def _store_daily_insights(self):
        """
        Store daily insights and log the operation.
        """
        try:
            print(f"Generating and storing daily insights at {datetime.now()}")
            insights_id = self.insights_handler.store_daily_insights()
            print(f"Daily insights stored with ID: {insights_id}")
            return insights_id
        except Exception as e:
            print(f"Error storing daily insights: {e}")
            return None
    
    def _store_weekly_insights(self):
        """
        Store weekly insights and log the operation.
        """
        try:
            print(f"Generating and storing weekly insights at {datetime.now()}")
            insights_id = self.insights_handler.store_weekly_insights()
            print(f"Weekly insights stored with ID: {insights_id}")
            return insights_id
        except Exception as e:
            print(f"Error storing weekly insights: {e}")
            return None
    
    def generate_initial_insights(self):
        """
        Generate and store initial insights if none exist.
        This can be called when the application starts.
        """
        print("Generating initial insights...")
        self._store_daily_insights()
        self._store_weekly_insights()
        print("Initial insights generation complete.")

# Singleton instance
insights_scheduler = InsightsScheduler()