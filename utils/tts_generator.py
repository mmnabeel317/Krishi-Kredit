from gtts import gTTS
import os

# List of languages supported by gTTS
# This is not exhaustive but includes many Indian languages
SUPPORTED_LANGUAGES = {
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

def is_language_supported(language_code):
    """Check if the language is supported by gTTS"""
    return language_code in SUPPORTED_LANGUAGES

def generate_speech(text, language_code, output_path):
    """
    Generate speech from text using gTTS
    
    Args:
        text: Text to convert to speech
        language_code: ISO language code (e.g., 'hi' for Hindi)
        output_path: Path to save the audio file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if language is supported
        if not is_language_supported(language_code):
            print(f"Language {language_code} is not supported by gTTS. Falling back to text only.")
            return False
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Generate speech
        tts = gTTS(text=text, lang=language_code, slow=False)
        tts.save(output_path)
        
        return True
    
    except Exception as e:
        print(f"Error generating speech: {str(e)}")
        return False
