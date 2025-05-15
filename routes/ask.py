from flask import Blueprint, request, jsonify, session, current_app
import os
import uuid
from utils.groq_client import get_ai_response
from utils.tts_generator import generate_speech
from utils.db_manager import db_manager

ask_bp = Blueprint('ask', __name__)

@ask_bp.route('/ask', methods=['POST'])
def ask():
    """
    Endpoint to get AI response using GroqCloud
    Expects:
    - message in request.json['message']
    - language code in request.json['language']
    Returns:
    - AI response text
    - URL to audio file of the response
    - Conversation history
    """
    data = request.json
    if not data or 'message' not in data or 'language' not in data:
        return jsonify({"error": "Message and language are required"}), 400
    
    message = data['message']
    language = data['language']
    
    # Get user_id from session
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User session not found"}), 400
    
    # Get conversation_id from session or create a new conversation
    conversation_id = session.get('conversation_id')
    if not conversation_id:
        conversation_id = db_manager.get_or_create_conversation(user_id, language)
        session['conversation_id'] = conversation_id
    
    # Add user message to database first
    db_manager.add_message(conversation_id, "user", message)
    
    # Then get updated conversation history from database
    conversation = db_manager.get_conversation_for_ai(conversation_id)
    
    # Get AI response
    try:
        print(f"Sending message to AI: {message}")
        print(f"Conversation history has {len(conversation)} messages")
        
        # Count how many questions have been asked so far
        assistant_messages = [msg for msg in conversation if msg["role"] == "assistant"]
        questions_asked = len(assistant_messages)
        print(f"Questions asked so far: {questions_asked}")
        
        # Determine which question to ask next based on the number of questions already asked
        if questions_asked == 0:
            # First question: What do you need the loan for?
            next_question = 1
        elif questions_asked == 1:
            # Second question: How much money do you need?
            next_question = 2
        else:
            # Third question: What is your monthly income?
            next_question = 3
            
        print(f"Next question should be question #{next_question}")
        
        # Get AI response
        ai_response = get_ai_response(message, conversation, language)
        
        # Generate speech from AI response
        audio_filename = f"{uuid.uuid4()}.mp3"
        audio_path = os.path.join(current_app.static_folder, audio_filename)
        
        speech_success = generate_speech(ai_response, language, audio_path)
        audio_url = f"/audio/{audio_filename}" if speech_success else None
        
        # Add AI response to database
        db_manager.add_message(conversation_id, "assistant", ai_response, audio_url)
        
        # Get updated conversation history
        conversation_history = db_manager.get_conversation_history(conversation_id)
        
        # Return response
        response_data = {
            "response": ai_response,
            "audio_url": audio_url,
            "conversation_id": conversation_id,
            "conversation_history": conversation_history
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
