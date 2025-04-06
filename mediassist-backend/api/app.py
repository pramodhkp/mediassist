import sys
import os
import atexit
import tempfile
import uuid
import json
from datetime import datetime
import threading

# Add the mediassist-backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, jsonify, make_response, send_file
from utils import parse_pdf
from werkzeug.utils import secure_filename
from flask_cors import CORS
from litellm import transcription
from .scheduler import insights_scheduler
from .chat import ChatHandler
from .insights_handler import InsightsHandler
from storage.client import (
    get_user_profile_data, get_medical_conditions_data, get_nutrition_data_for_period,
    store_medical_report, get_medical_reports, get_medical_report, delete_medical_report
)
from graphs.deep_analysis_graph import graph as deep_analysis_graph
from datetime import datetime, timedelta
from config import API_BASE_URL, API_KEY

# Dictionary to track analysis status
analysis_status = {}
analysis_status_lock = threading.Lock()

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

@app.route('/transcribe_audio', methods=['POST'])
def transcribe_audio():
    """
    Transcribe audio using gpt-4o-mini-transcribe via LiteLLM.
    """
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
            
        audio_file = request.files['audio']
        
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400
            
        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_file:
            audio_path = temp_file.name
            audio_file.save(audio_path)
        
        try:
            # Use LiteLLM's transcription function with gpt-4o-mini-transcribe
            with open(audio_path, 'rb') as audio_file_obj:
                response = transcription(
                    model="gpt-4o-mini-transcribe",
                    file=audio_file_obj,
                    api_key=API_KEY,
                    api_base=API_BASE_URL
                )
            
            transcribed_text = response.text
            
            # Return the transcribed text
            resp = make_response(jsonify({'text': transcribed_text}))
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp
                
        except Exception as e:
            print(f"Transcription error: {str(e)}")
            return jsonify({'error': f'Transcription failed: {str(e)}'}), 500
        finally:
            # Clean up the temporary file
            if os.path.exists(audio_path):
                os.remove(audio_path)
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/medical_reports', methods=['GET'])
def get_all_medical_reports():
    """
    Retrieves a list of all medical reports.
    """
    try:
        reports = get_medical_reports()
        resp = make_response(jsonify({'reports': reports}))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload_medical_report', methods=['POST'])
def upload_medical_report():
    """
    Uploads a medical report file.
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get file details
        filename = file.filename
        file_type = file.content_type
        file_size = 0  # Will be calculated after reading the file
        description = request.form.get('description', None)
        
        # Read the file data
        file_data = file.read()
        file_size = len(file_data)
        
        # Store the file
        file_id = store_medical_report(file_data, filename, file_type, file_size, description)
        
        return jsonify({
            'success': True,
            'file_id': str(file_id),
            'filename': filename,
            'file_type': file_type,
            'file_size': file_size
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_medical_report/<file_id>', methods=['GET'])
def download_medical_report(file_id):
    """
    Downloads a specific medical report file.
    """
    try:
        file_path, filename, content_type = get_medical_report(file_id)
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            file_path,
            mimetype=content_type,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete_medical_report/<file_id>', methods=['DELETE'])
def delete_medical_report_endpoint(file_id):
    """
    Deletes a specific medical report file.
    """
    try:
        success = delete_medical_report(file_id)
        
        if not success:
            return jsonify({'error': 'File not found'}), 404
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/deep_analysis', methods=['POST'])
def trigger_deep_analysis():
    """
    Triggers a deep analysis of all medical reports.
    """
    try:
        # Get all medical reports
        reports = get_medical_reports()
        
        if not reports:
            return jsonify({'error': 'No medical reports found'}), 404
            
        # Combined report content
        combined_report_content = ""
        file_ids = []
        filenames = []
        
        # Process each report
        for report in reports:
            file_id = report.get('_id')
            filename = report.get('filename')
            
            # Skip if file_id is missing
            if not file_id:
                continue
                
            file_ids.append(str(file_id))
            filenames.append(filename)
            
            # Get the file
            file_path, _, content_type = get_medical_report(str(file_id))
            
            if not file_path or not os.path.exists(file_path):
                continue
            
            # Read the file content
            with open(file_path, 'rb') as f:
                file_content = f.read()
                # Handle different file types
                if 'pdf' in content_type.lower():
                    # Use the PDF parser for PDF files
                    report_text = parse_pdf(file_path)
                elif 'text' in content_type:
                    # For text files, decode directly
                    try:
                        report_text = file_content.decode('utf-8')
                    except UnicodeDecodeError:
                        report_text = f"[Binary file content of type {content_type}]"
                else:
                    # For other binary formats, use a placeholder
                    report_text = f"[Binary file content of type {content_type}]"
                
                # Add to combined content with separator
                combined_report_content += f"\n\n--- REPORT: {filename} ---\n\n{report_text}"
        # Initialize the state for the graph
        initial_state = {
            "messages": [],
            "report_content": combined_report_content,
            "file_ids": file_ids,
            "filenames": filenames
        }
        
        # Run the graph asynchronously
        config = {"configurable": {"thread_id": "combined_analysis"}}
        
        # Generate a unique analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Set initial status
        with analysis_status_lock:
            analysis_status[analysis_id] = {
                'status': 'running',
                'timestamp': datetime.now().isoformat(),
                'file_count': len(file_ids)
            }
        
        # Start the analysis in a separate thread
        def run_analysis():
            try:
                result = deep_analysis_graph.invoke(initial_state, config=config)
                
                # Store the result in a file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_filename = f"deep_analysis_{timestamp}.json"
                report_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), 'reports', report_filename)
                
                # Extract the content from the AIMessage
                if result and 'messages' in result and len(result['messages']) > 0:
                    analysis_content = result['messages'][-1].content
                    
                    # Create a report object
                    report_data = {
                        'timestamp': datetime.now().isoformat(),
                        'file_ids': file_ids,
                        'filenames': filenames,
                        'content': analysis_content,
                        'report_id': timestamp
                    }
                    
                    # Write to file
                    with open(report_path, 'w') as f:
                        json.dump(report_data, f, indent=2)
                    
                    print(f"Deep analysis completed and saved to {report_path}")
                    
                    # Update status to completed
                    with analysis_status_lock:
                        if analysis_id in analysis_status:
                            analysis_status[analysis_id]['status'] = 'completed'
                            analysis_status[analysis_id]['report_id'] = timestamp
                else:
                    print("Deep analysis completed but no content was returned")
                    
                    # Update status to completed with error
                    with analysis_status_lock:
                        if analysis_id in analysis_status:
                            analysis_status[analysis_id]['status'] = 'completed_no_content'
            except Exception as e:
                print(f"Error in deep analysis: {str(e)}")
                
                # Update status to error
                with analysis_status_lock:
                    if analysis_id in analysis_status:
                        analysis_status[analysis_id]['status'] = 'error'
                        analysis_status[analysis_id]['error'] = str(e)
        
        thread = threading.Thread(target=run_analysis)
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Deep analysis started',
            'file_count': len(file_ids),
            'filenames': filenames,
            'analysis_id': analysis_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analysis_status/<analysis_id>', methods=['GET'])
def get_analysis_status(analysis_id):
    """
    Checks the status of a specific analysis.
    """
    try:
        with analysis_status_lock:
            if analysis_id in analysis_status:
                return jsonify(analysis_status[analysis_id])
            else:
                return jsonify({'error': 'Analysis ID not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analysis_reports', methods=['GET'])
def get_analysis_reports():
    """
    Retrieves a list of all deep analysis reports.
    """
    try:
        reports_dir = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), 'reports')
        
        # Create the directory if it doesn't exist
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
            
        # Get all JSON files in the reports directory
        report_files = [f for f in os.listdir(reports_dir) if f.endswith('.json')]
        
        reports = []
        for filename in report_files:
            file_path = os.path.join(reports_dir, filename)
            try:
                with open(file_path, 'r') as f:
                    report_data = json.load(f)
                    # Add basic info to the list
                    reports.append({
                        'report_id': report_data.get('report_id', ''),
                        'timestamp': report_data.get('timestamp', ''),
                        'filenames': report_data.get('filenames', []),
                        'file_count': len(report_data.get('filenames', []))
                    })
            except Exception as e:
                print(f"Error reading report file {filename}: {str(e)}")
        
        # Sort reports by timestamp (newest first)
        reports.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return jsonify({'reports': reports})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analysis_report/<report_id>', methods=['GET'])
def get_analysis_report(report_id):
    """
    Retrieves a specific deep analysis report.
    """
    try:
        reports_dir = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), 'reports')
        
        # Look for the report file
        report_files = [f for f in os.listdir(reports_dir) if f.endswith('.json') and report_id in f]
        
        if not report_files:
            return jsonify({'error': 'Report not found'}), 404
            
        # Use the first matching file
        file_path = os.path.join(reports_dir, report_files[0])
        
        with open(file_path, 'r') as f:
            report_data = json.load(f)
            
        return jsonify({'report': report_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Generate initial insights if needed
    insights_scheduler.generate_initial_insights()
    
    app.run(debug=True)
