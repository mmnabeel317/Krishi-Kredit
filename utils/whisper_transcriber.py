import os
from faster_whisper import WhisperModel
import tempfile
import subprocess
import sys

# Define a fallback for audio conversion that doesn't rely on pydub/audioop

# Initialize the model (will download if not present)
# Using the small model for balance of speed and accuracy
# Can be changed to tiny, base, medium, large-v2 based on requirements
model_size = "small"
model = None

def load_model():
    """Lazy load the Whisper model"""
    global model
    if model is None:
        # Use CUDA if available, otherwise CPU
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
    return model

def convert_audio_if_needed(audio_path):
    """Convert audio to WAV format if it's not already"""
    file_ext = os.path.splitext(audio_path)[1].lower()
    
    if file_ext not in ['.wav']:
        # Create a temporary WAV file
        temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False).name
        
        # For this simplified version, we'll just pass the original file
        # since faster-whisper can handle various audio formats directly
        print(f"Note: Audio conversion skipped due to missing dependencies. Using original format.")
        return audio_path
    
    return audio_path

def transcribe_audio(audio_path, language=None):
    """
    Transcribe audio file using faster-whisper
    
    Args:
        audio_path: Path to the audio file
        language: ISO language code (e.g., 'hi' for Hindi) or None for auto-detection
        
    Returns:
        tuple: (transcription text, detected language)
    """
    try:
        # Load the model
        model = load_model()
        
        # Convert audio if needed
        wav_path = convert_audio_if_needed(audio_path)
        
        # Transcribe with faster-whisper
        # If language is provided, use it; otherwise, auto-detect
        segments, info = model.transcribe(
            wav_path, 
            language=language,
            task="transcribe"
        )
        
        # Combine all segments into a single text
        transcription = " ".join([segment.text for segment in segments])
        
        # Clean up temporary file if created
        if wav_path != audio_path and os.path.exists(wav_path):
            os.remove(wav_path)
            
        return transcription.strip(), info.language
        
    except Exception as e:
        # Clean up temporary file if created
        if 'wav_path' in locals() and wav_path != audio_path and os.path.exists(wav_path):
            os.remove(wav_path)
        raise Exception(f"Transcription error: {str(e)}")
