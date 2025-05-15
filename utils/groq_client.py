import os
import groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize the Groq client
client = groq.Groq(api_key=GROQ_API_KEY)

# Define language codes and their names
LANGUAGE_CODES = {
    'hi': 'Hindi',
    'bn': 'Bengali',
    'ta': 'Tamil',
    'te': 'Telugu',
    'mr': 'Marathi',
    'gu': 'Gujarati',
    'kn': 'Kannada',
    'ml': 'Malayalam',
    'pa': 'Punjabi',
    'en': 'English'
}

# Define system prompt for the loan assistant
SYSTEM_PROMPT = """
You are a loan assistant for rural Indian users. Your task is to recommend an appropriate loan scheme after asking EXACTLY 3 QUESTIONS in this FIXED ORDER:

1. First question (ALWAYS ASK THIS FIRST): "What do you need the loan for?" (purpose)
2. Second question (ALWAYS ASK THIS SECOND): "How much money do you need?" (amount)
3. Third question (ALWAYS ASK THIS THIRD): "What is your approximate monthly income?" (income)

AFTER THESE 3 QUESTIONS, IMMEDIATELY RECOMMEND ONE OF THESE LOAN TYPES:
- Crop Loan (6.5% interest) - For seasonal agricultural operations
- Kisan Credit Card (7.0% interest) - For cultivation expenses
- Dairy Loan (8.5% interest) - For purchase of milch animals
- Farm Mechanization Loan (9.0% interest) - For tractors and equipment
- Self Help Group Loan (10.0% interest) - For group-based activities
- Microfinance Loan (12.0% interest) - For small business

STRICT RULES:
1. NEVER REPEAT QUESTIONS - Once a question is answered, move immediately to the next question.
2. NEVER ASK FOR CLARIFICATION - Accept whatever answer the user gives and move on.
3. NEVER DEVIATE FROM THE 3-QUESTION SEQUENCE - Do not ask any other questions.
4. NEVER SWITCH LANGUAGES - Stay in the user's selected language.
5. NO GREETINGS OR PLEASANTRIES - Be direct and to the point.
6. KEEP RESPONSES UNDER 50 WORDS - Be extremely concise.
7. AFTER THE 3 QUESTIONS, GIVE A LOAN RECOMMENDATION IMMEDIATELY - Do not ask anything else.

EXAMPLE CONVERSATION:
AI: What do you need the loan for?
User: To buy a tractor
AI: How much money do you need?
User: 500,000 rupees
AI: What is your approximate monthly income?
User: 20,000 rupees
AI: Based on your needs, I recommend a Farm Mechanization Loan with 9.0% interest. This is designed for purchasing tractors and farm equipment. Visit your local bank with ID and income proof to apply.

FOLLOW THIS EXACT PATTERN WITHOUT DEVIATION.
"""

# Define loan types and their typical interest rates
LOAN_TYPES = {
    "crop_loan": {
        "name": "Crop Loan",
        "interest_rate": "6.5%",
        "eligibility": "Farmers with land ownership documents",
        "purpose": "For seasonal agricultural operations"
    },
    "kisan_credit_card": {
        "name": "Kisan Credit Card (KCC)",
        "interest_rate": "7.0%",
        "eligibility": "All farmers with land records",
        "purpose": "For cultivation expenses and allied agricultural activities"
    },
    "dairy_loan": {
        "name": "Dairy Loan",
        "interest_rate": "8.5%",
        "eligibility": "Farmers engaged in dairy farming",
        "purpose": "For purchase of milch animals and dairy equipment"
    },
    "farm_mechanization_loan": {
        "name": "Farm Mechanization Loan",
        "interest_rate": "9.0%",
        "eligibility": "Farmers with regular income",
        "purpose": "For purchase of tractors and farm equipment"
    },
    "self_help_group_loan": {
        "name": "Self Help Group (SHG) Loan",
        "interest_rate": "10.0%",
        "eligibility": "Members of registered SHGs",
        "purpose": "For group-based income generation activities"
    },
    "microfinance_loan": {
        "name": "Microfinance Loan",
        "interest_rate": "12.0%",
        "eligibility": "Low-income individuals",
        "purpose": "For small business and income generation"
    }
}

def get_ai_response(message, conversation_history, language_code):
    """Get AI response using GroqCloud"""
    if not GROQ_API_KEY:
        return "Error: GROQ_API_KEY not found in environment variables. Please set it up."
    
    # Get language name from code
    language_name = LANGUAGE_CODES.get(language_code, "English")
    
    # Count how many assistant messages we have to determine which question to ask next
    assistant_messages = [msg for msg in conversation_history if msg["role"] == "assistant"]
    questions_asked = len(assistant_messages)
    
    # Force the correct next question based on conversation state
    forced_response = None
    if questions_asked == 0:
        # First interaction - ask about loan purpose
        forced_response = f"What do you need the loan for?"
    elif questions_asked == 1:
        # Second interaction - ask about loan amount
        forced_response = f"How much money do you need?"
    elif questions_asked == 2:
        # Third interaction - ask about monthly income
        forced_response = f"What is your approximate monthly income?"
    
    # If we're forcing a specific question, return it immediately
    if forced_response:
        print(f"FORCING QUESTION #{questions_asked + 1}: {forced_response}")
        return forced_response
    
    # Create simple prompt with language instruction
    enhanced_prompt = f"""{SYSTEM_PROMPT}

IMPORTANT: You MUST respond in {language_name} only.
"""
    
    # Debug the conversation history
    print(f"Conversation history length: {len(conversation_history)}")
    for i, msg in enumerate(conversation_history):
        print(f"Message {i}: {msg['role']} - {msg['content'][:30] if len(msg['content']) > 30 else msg['content']}")
    
    # Prepare messages for the API - simple approach
    messages = [
        {"role": "system", "content": enhanced_prompt}
    ]
    
    # Add conversation history
    for msg in conversation_history:
        messages.append(msg)
    
    # Add current message if not already in history
    if not conversation_history or conversation_history[-1]["role"] != "user" or conversation_history[-1]["content"] != message:
        messages.append({"role": "user", "content": message})
        print(f"Added new user message: {message}")
    else:
        print("Current message already in history, not adding again.")
    
    try:
        # Choose model based on availability - LLaMA3 preferred, Mixtral as fallback
        model = "llama3-8b-8192" if os.getenv("USE_LLAMA3", "true").lower() == "true" else "mixtral-8x7b-32768"
        
        # Call the Groq API with lower temperature for more focused responses
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.5,  # Lower temperature for more focused responses
            max_tokens=1024,
        )
        
        # Extract and return the response text
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Error communicating with GroqCloud: {str(e)}"
