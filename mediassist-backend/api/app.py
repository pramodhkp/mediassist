import sys
import os

# Add the mediassist-backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from .chat import ChatHandler
from .insights_handler import InsightsHandler

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})  # Allow CORS for all routes and origins
insights_handler = InsightsHandler()
chat_handler = ChatHandler()

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

if __name__ == '__main__':
    app.run(debug=True)
