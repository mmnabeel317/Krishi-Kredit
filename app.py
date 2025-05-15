from flask import Flask, session, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import uuid
from dotenv import load_dotenv

# Import route modules
from routes.transcribe import transcribe_bp
from routes.ask import ask_bp
from routes.history import history_bp

# Import database manager
from utils.db_manager import db_manager

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='static')
CORS(app, supports_credentials=True)

# Configure session
app.secret_key = os.getenv('SECRET_KEY', str(uuid.uuid4()))
app.config['SESSION_TYPE'] = 'filesystem'

# Register blueprints
app.register_blueprint(transcribe_bp)
app.register_blueprint(ask_bp)
app.register_blueprint(history_bp)

# Initialize user session
@app.before_request
def initialize_session():
    if 'user_id' not in session:
        # Create a new user in the database
        user_id = db_manager.create_user()
        session['user_id'] = user_id

# Serve static files
@app.route('/audio/<path:filename>')
def serve_audio(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/health')
def health_check():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    # Create static folder if it doesn't exist
    os.makedirs(app.static_folder, exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)
