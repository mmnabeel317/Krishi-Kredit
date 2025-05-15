import sqlite3
import json
import os
import uuid
from datetime import datetime

class DatabaseManager:
    """
    SQLite database manager for storing and retrieving conversation history
    """
    def __init__(self, db_path="conversation_history.db"):
        """Initialize the database manager with the path to the SQLite database"""
        # Use absolute path if db_path is not absolute
        if not os.path.isabs(db_path):
            db_path = os.path.join(os.getcwd(), db_path)
            
        self.db_path = db_path
        self._create_tables()
        
    def _get_connection(self):
        """Get a connection to the SQLite database"""
        return sqlite3.connect(self.db_path)
    
    def _create_tables(self):
        """Create the necessary tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create conversations table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            conversation_id TEXT PRIMARY KEY,
            user_id TEXT,
            language_code TEXT,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        ''')
        
        # Create messages table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            message_id TEXT PRIMARY KEY,
            conversation_id TEXT,
            role TEXT,
            content TEXT,
            audio_url TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations (conversation_id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_user(self):
        """Create a new user and return the user_id"""
        user_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO users (user_id) VALUES (?)
        ''', (user_id,))
        
        conn.commit()
        conn.close()
        
        return user_id
    
    def create_conversation(self, user_id, language_code):
        """Create a new conversation and return the conversation_id"""
        conversation_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO conversations (conversation_id, user_id, language_code)
        VALUES (?, ?, ?)
        ''', (conversation_id, user_id, language_code))
        
        conn.commit()
        conn.close()
        
        return conversation_id
    
    def add_message(self, conversation_id, role, content, audio_url=None):
        """Add a message to a conversation"""
        message_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Add the message
        cursor.execute('''
        INSERT INTO messages (message_id, conversation_id, role, content, audio_url)
        VALUES (?, ?, ?, ?, ?)
        ''', (message_id, conversation_id, role, content, audio_url))
        
        # Update the conversation's last_updated_at timestamp
        cursor.execute('''
        UPDATE conversations
        SET last_updated_at = CURRENT_TIMESTAMP
        WHERE conversation_id = ?
        ''', (conversation_id,))
        
        conn.commit()
        conn.close()
        
        return message_id
    
    def get_conversation_history(self, conversation_id, limit=None):
        """Get the message history for a conversation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if limit:
            cursor.execute('''
            SELECT role, content, audio_url, timestamp
            FROM messages
            WHERE conversation_id = ?
            ORDER BY timestamp ASC
            LIMIT ?
            ''', (conversation_id, limit))
        else:
            cursor.execute('''
            SELECT role, content, audio_url, timestamp
            FROM messages
            WHERE conversation_id = ?
            ORDER BY timestamp ASC
            ''', (conversation_id,))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                "role": row[0],
                "content": row[1],
                "audio_url": row[2],
                "timestamp": row[3]
            })
        
        conn.close()
        
        return messages
    
    def get_conversation_for_ai(self, conversation_id):
        """Get the conversation history formatted for AI context"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT role, content, timestamp
        FROM messages
        WHERE conversation_id = ?
        ORDER BY timestamp ASC
        ''', (conversation_id,))
        
        messages = []
        for row in cursor.fetchall():
            # Only include messages that have content
            if row[1] and row[1].strip():
                messages.append({
                    "role": row[0],
                    "content": row[1]
                })
        
        conn.close()
        
        # Debug output
        print(f"Retrieved {len(messages)} messages from database for conversation {conversation_id}")
        for i, msg in enumerate(messages):
            print(f"DB Message {i}: {msg['role']} - {msg['content']}")
        
        # Ensure we have a clean conversation history
        # If we have an odd number of messages and the last one is from the assistant,
        # remove it to ensure we're not repeating questions
        if len(messages) % 2 != 0 and len(messages) > 0 and messages[-1]['role'] == 'assistant':
            print("Removing last assistant message to prevent repetition")
            messages = messages[:-1]
        
        return messages
    
    def get_user_conversations(self, user_id):
        """Get all conversations for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT conversation_id, language_code, started_at, last_updated_at
        FROM conversations
        WHERE user_id = ?
        ORDER BY last_updated_at DESC
        ''', (user_id,))
        
        conversations = []
        for row in cursor.fetchall():
            conversations.append({
                "conversation_id": row[0],
                "language_code": row[1],
                "started_at": row[2],
                "last_updated_at": row[3]
            })
        
        conn.close()
        
        return conversations
    
    def get_latest_conversation(self, user_id):
        """Get the most recent conversation for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT conversation_id, language_code
        FROM conversations
        WHERE user_id = ?
        ORDER BY last_updated_at DESC
        LIMIT 1
        ''', (user_id,))
        
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return {
                "conversation_id": result[0],
                "language_code": result[1]
            }
        return None
    
    def get_or_create_conversation(self, user_id, language_code):
        """Get the latest conversation or create a new one if none exists"""
        latest = self.get_latest_conversation(user_id)
        
        if latest:
            # Check if the conversation is recent (within 24 hours)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT last_updated_at
            FROM conversations
            WHERE conversation_id = ?
            ''', (latest["conversation_id"],))
            
            last_updated = cursor.fetchone()[0]
            conn.close()
            
            # If language changed or conversation is old, create a new one
            if latest["language_code"] != language_code:
                return self.create_conversation(user_id, language_code)
            
            return latest["conversation_id"]
        
        # No conversation exists, create a new one
        return self.create_conversation(user_id, language_code)

# Create a singleton instance
db_manager = DatabaseManager()
