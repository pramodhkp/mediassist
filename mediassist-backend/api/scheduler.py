import sys
import os
import time
import threading
import schedule
from datetime import datetime, time as dt_time # Renamed to avoid conflict with time module
from apscheduler.schedulers.background import BackgroundScheduler
from mongoengine.queryset.visitor import Q


# Add the mediassist-backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.insights_handler import InsightsHandler
# Assuming models.py is in storage, and client.py sets up connection
from storage.models import Medication # Adjusted import path

# --- Medication Reminder Scheduler (APScheduler) ---

def check_medication_reminders():
    """
    Checks for medications that are due at the current time and logs reminders.
    """
    try:
        now = datetime.now()
        current_time_str = now.strftime("%H:%M") # "HH:MM" format for matching reminder_times
        # current_date_obj = now.date() # This is not used in the revised query directly
        
        # Query using mongoengine syntax
        # start_date is stored as DateTimeField, so direct comparison with now() works if we only care about the date part.
        # For start_date__lte=now, it means it could have started any time before or exactly now.
        # For end_date__gte=now, it means it could end any time after or exactly now.
        # reminder_times contains strings like "08:00", "14:30"
        
        due_medications = Medication.objects(
            start_date__lte=now, # Medication period has started
            reminder_times=current_time_str # Matches one of the HH:MM reminder times
        ).filter(
            Q(end_date__exists=False) | Q(end_date__gte=now) # Medication period has not ended
        )

        if due_medications.count() > 0:
            print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Found {due_medications.count()} due medication(s) for time {current_time_str}:")
            for med in due_medications:
                # Log to console
                print(f"REMINDER: User '{med.user_id}' take '{med.medication_name}' at {current_time_str}")
                # Here, you could add logic to send actual notifications (email, push, etc.)
        # else:
            # print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] No medications due at {current_time_str}.")

    except Exception as e:
        print(f"Error in check_medication_reminders: {e}")

# Initialize APScheduler for medication reminders
medication_reminder_scheduler = BackgroundScheduler(daemon=True)
medication_reminder_scheduler.add_job(check_medication_reminders, 'interval', minutes=1)


# --- Existing Insights Scheduler (schedule library) ---
class InsightsScheduler:
    def __init__(self):
        self.insights_handler = InsightsHandler()
        self.running = False
        self.scheduler_thread = None
        # Keep track of the APScheduler instance as well, or manage it globally
        self.med_reminder_scheduler_instance = medication_reminder_scheduler 
    
    def start_all_schedulers(self):
        """
        Start both Insights scheduler and Medication Reminder scheduler.
        """
        # Start Insights Scheduler (using 'schedule' library)
        if self.running:
            print("Insights Scheduler is already running.")
        else:
            schedule.every().day.at("00:00").do(self._store_daily_insights)
            schedule.every().sunday.at("00:00").do(self._store_weekly_insights)
            self.running = True
            self.scheduler_thread = threading.Thread(target=self._run_insights_scheduler_loop)
            self.scheduler_thread.daemon = True
            self.scheduler_thread.start()
            print(f"Insights scheduler (schedule lib) started at {datetime.now()}")

        # Start Medication Reminder Scheduler (APScheduler)
        try:
            if not self.med_reminder_scheduler_instance.running:
                self.med_reminder_scheduler_instance.start()
                print(f"Medication Reminder scheduler (APScheduler) started at {datetime.now()}")
            else:
                print("Medication Reminder scheduler (APScheduler) is already running.")
        except Exception as e:
            print(f"Failed to start Medication Reminder scheduler (APScheduler): {e}")
    
    def stop_all_schedulers(self):
        """
        Stop both schedulers.
        """
        # Stop Insights Scheduler
        if not self.running:
            print("Insights Scheduler is not running.")
        else:
            self.running = False
            if self.scheduler_thread:
                self.scheduler_thread.join(timeout=1)
            print(f"Insights scheduler (schedule lib) stopped at {datetime.now()}")
        
        # Stop Medication Reminder Scheduler
        try:
            if self.med_reminder_scheduler_instance.running:
                self.med_reminder_scheduler_instance.shutdown()
                print(f"Medication Reminder scheduler (APScheduler) stopped at {datetime.now()}")
            else:
                print("Medication Reminder scheduler (APScheduler) is not running.")
        except Exception as e:
            print(f"Failed to stop Medication Reminder scheduler (APScheduler): {e}")
    
    def _run_insights_scheduler_loop(self):
        """
        Run the insights scheduler loop.
        """
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute for insights
    
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
# The class name is still InsightsScheduler, but it now manages both.
# Consider renaming to AppScheduler or similar if this becomes confusing.
app_scheduler = InsightsScheduler()