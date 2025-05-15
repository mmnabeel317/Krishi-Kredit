from flask import Blueprint, request, jsonify, session
import os
import tempfile
import uuid
from utils.whisper_transcriber import transcribe_audio
from utils.db_manager import db_manager

transcribe_bp = Blueprint('transcribe', __name__)

@transcribe_bp.route('/transcribe', methods=['POST'])
def transcribe():
    """
    Endpoint to transcribe audio to text using faster-whisper
    Expects:
    - audio file in request.files['audio']
    - language code in request.form['language']
    Returns:
    - transcribed text
    - detected language (if auto-detection was used)
    """
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    audio_file = request.files['audio']
    language = request.form.get('language', None)  # None means auto-detect
    
    # Create a temporary file to store the audio
    temp_dir = os.path.join(os.getcwd(), 'static')
    os.makedirs(temp_dir, exist_ok=True)
    
    temp_file = os.path.join(temp_dir, f"{uuid.uuid4()}.webm")
    audio_file.save(temp_file)
    
    try:
        # Transcribe the audio
        transcription, detected_language = transcribe_audio(temp_file, language)
        
        # Get user_id from session
        user_id = session.get('user_id')
        
        # Get or create a conversation for this user and language
        language_code = language or detected_language
        conversation_id = db_manager.get_or_create_conversation(user_id, language_code)
        
        # Store conversation_id in session
        session['conversation_id'] = conversation_id
        
        # Add user message to database
        db_manager.add_message(conversation_id, "user", transcription)
        
        # Clean up the temporary file
        os.remove(temp_file)
        
        # Get conversation history for context
        conversation_history = db_manager.get_conversation_history(conversation_id)
        
        return jsonify({
            "transcription": transcription,
            "detected_language": detected_language,
            "conversation_id": conversation_id,
            "conversation_history": conversation_history
        })
    
    except Exception as e:
        # Clean up the temporary file in case of error
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return jsonify({"error": str(e)}), 500
