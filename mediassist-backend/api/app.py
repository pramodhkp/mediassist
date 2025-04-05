import sys
import os
import atexit

# Add the mediassist-backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from .scheduler import insights_scheduler
from .chat import ChatHandler
from .insights_handler import InsightsHandler
from storage.client import get_user_profile_data, get_medical_conditions_data, get_nutrition_data_for_period
from datetime import datetime, timedelta

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})  # Allow CORS for all routes and origins
insights_handler = InsightsHandler()
chat_handler = ChatHandler()

# Start the insights scheduler
insights_scheduler.start()

# Register a function to stop the scheduler when the application exits
atexit.register(insights_scheduler.stop)

@app.route('/send_message', methods=['POST'])
def send_message():
    user_message = request.json.get('message', '')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    # Process the message using the ChatHandler
    response = chat_handler.process_message(user_message)
    resp = make_response(jsonify({'response': response}))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route('/daily_insights', methods=['GET'])
def daily_insights():
    # Generate daily insights using the insights handler
    daily_insights = insights_handler.get_daily_insights()
    resp = make_response(jsonify({'response': daily_insights}))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route('/weekly_insights', methods=['GET'])
def weekly_insights():
    # Generate weekly insights using the insights handler
    weekly_insights = insights_handler.get_weekly_insights()

    resp = make_response(jsonify({'response': weekly_insights}))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route('/generate_and_store_insights', methods=['POST'])
def generate_and_store_insights():
    """
    Manually trigger the generation and storage of insights.
    This is useful for testing or initializing the database with insights.
    """
    try:
        insight_type = request.json.get('type', 'both')
        result = {}
        
        if insight_type in ['daily', 'both']:
            daily_id = insights_handler.store_daily_insights()
            result['daily_id'] = str(daily_id)
        
        if insight_type in ['weekly', 'both']:
            weekly_id = insights_handler.store_weekly_insights()
            result['weekly_id'] = str(weekly_id)
        
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/user_profile', methods=['GET'])
def get_user_profile():
    """
    Retrieves the user's profile information.
    """
    try:
        # Get user profile data using the existing function
        profile_data = get_user_profile_data()
        
        # Convert ObjectId to string for JSON serialization
        if profile_data and '_id' in profile_data:
            profile_data['_id'] = str(profile_data['_id'])
        if profile_data and 'timestamp' in profile_data:
            profile_data['timestamp'] = profile_data['timestamp'].isoformat()
            
        resp = make_response(jsonify({'response': profile_data}))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/medical_conditions', methods=['GET'])
def get_medical_conditions():
    """
    Retrieves the user's medical conditions.
    """
    try:
        # Get medical conditions data
        conditions_data = get_medical_conditions_data()
        resp = make_response(jsonify({'response': conditions_data}))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Generate initial insights if needed
    insights_scheduler.generate_initial_insights()
    
    app.run(debug=True)
