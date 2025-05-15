import { useState, useRef, useEffect } from 'react';
import axios from 'axios';

const Recorder = ({ 
  selectedLanguage, 
  onNewMessage, 
  onAIResponse, 
  isRecording, 
  setIsRecording,
  isProcessing,
  setIsProcessing
}) => {
  const [error, setError] = useState(null);
  const [conversationId, setConversationId] = useState(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // Start recording audio
  const startRecording = async () => {
    try {
      setError(null);
      
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Create MediaRecorder instance
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      
      // Handle data available event
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      // Handle recording stop event
      mediaRecorder.onstop = handleRecordingStop;
      
      // Start recording
      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      setError(`Microphone access error: ${err.message}`);
      console.error('Error accessing microphone:', err);
    }
  };

  // Stop recording audio
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      // Stop all audio tracks
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
    }
  };

  // Handle recording stop and send audio to backend
  const handleRecordingStop = async () => {
    try {
      setIsProcessing(true);
      
      // Create audio blob from recorded chunks
      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
      
      // Create form data for API request
      const formData = new FormData();
      formData.append('audio', audioBlob);
      formData.append('language', selectedLanguage);
      
      // Send to transcription API
      const transcribeResponse = await axios.post('http://localhost:5000/transcribe', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        withCredentials: true
      });
      
      const { 
        transcription, 
        conversation_id, 
        conversation_history 
      } = transcribeResponse.data;
      
      // Store conversation ID
      setConversationId(conversation_id);
      
      // Update UI with transcribed text
      onNewMessage(transcription);
      
      // Conversation history handling removed
      
      // Send transcribed text to AI for response
      const askResponse = await axios.post('http://localhost:5000/ask', {
        message: transcription,
        language: selectedLanguage
      }, {
        withCredentials: true
      });
      
      const { 
        response, 
        audio_url, 
        conversation_history: updated_history 
      } = askResponse.data;
      
      // Update UI with AI response
      onAIResponse(response, audio_url);
      
      // Updated conversation history handling removed
      
      // Play audio response if available
      if (audio_url) {
        // Make sure we use the full URL for audio files
        const fullAudioUrl = audio_url.startsWith('http') ? audio_url : `http://localhost:5000${audio_url}`;
        const audio = new Audio(fullAudioUrl);
        audio.play();
      }
      
      setIsProcessing(false);
    } catch (err) {
      setError(`Processing error: ${err.message}`);
      console.error('Error processing audio:', err);
      setIsProcessing(false);
    }
  };

  return (
    <div className="recorder">
      {error && <div className="alert alert-danger">{error}</div>}
      
      <button
        className={`record-button ${isRecording ? 'recording' : ''}`}
        onClick={isRecording ? stopRecording : startRecording}
        disabled={isProcessing}
      >
        {isRecording ? 'Stop Recording' : 'Start Recording'}
      </button>
      
      {isProcessing && (
        <div className="processing-indicator">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Processing...</span>
          </div>
          <span>Processing your request...</span>
        </div>
      )}
      
      <div className="recorder-instructions">
        <p>Click the button and speak in your selected language</p>
        <p className="small text-muted">
          {isRecording 
            ? 'Recording... Click again to stop.' 
            : 'Click to start recording your voice'}
        </p>
      </div>
    </div>
  );
};

export default Recorder;
