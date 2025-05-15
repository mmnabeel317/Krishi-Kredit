from flask import Blueprint, request, jsonify, session
from utils.db_manager import db_manager

history_bp = Blueprint('history', __name__)

@history_bp.route('/conversation/history', methods=['GET'])
def get_conversation_history():
    """
    Endpoint to retrieve conversation history for the current user
    Returns:
    - conversation_id: ID of the current conversation
    - language_code: Language code of the conversation
    - messages: List of messages in the conversation
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User session not found"}), 400
    
    conversation_id = session.get('conversation_id')
    if not conversation_id:
        # Get the latest conversation for this user
        latest = db_manager.get_latest_conversation(user_id)
        if latest:
            conversation_id = latest["conversation_id"]
            session['conversation_id'] = conversation_id
        else:
            # Return an empty conversation structure instead of an error
            return jsonify({
                "conversation_id": None,
                "language_code": None,
                "messages": []
            })
    
    # Get conversation history
    conversation_history = db_manager.get_conversation_history(conversation_id)
    
    # Get conversation details
    try:
        conn = db_manager._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT language_code FROM conversations WHERE conversation_id = ?
        """, (conversation_id,))
        
        result = cursor.fetchone()
        language_code = result[0] if result else None
        
        conn.close()
    except Exception as e:
        print(f"Error getting conversation details: {str(e)}")
        language_code = None
    
    return jsonify({
        "conversation_id": conversation_id,
        "language_code": language_code,
        "messages": conversation_history
    })

@history_bp.route('/conversation/list', methods=['GET'])
def list_conversations():
    """
    Endpoint to list all conversations for the current user
    Returns:
    - conversations: List of conversation objects with id, language, and timestamps
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User session not found"}), 400
    
    conversations = db_manager.get_user_conversations(user_id)
    
    return jsonify({
        "conversations": conversations
    })
