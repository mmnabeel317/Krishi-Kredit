import { useState, useEffect } from 'react';
import LanguageSelector from './components/LanguageSelector';
import Recorder from './components/Recorder';
import ChatBox from './components/ChatBox';
import './styles/app.css';

function App() {
  const [selectedLanguage, setSelectedLanguage] = useState('hi'); // Default to Hindi
  const [messages, setMessages] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  // Add initial welcome message when app loads
  useEffect(() => {
    // Add a welcome message when the component mounts
    setMessages([
      {
        role: 'assistant',
        content: 'Welcome to Krishi Kredit! Please select your preferred language and start speaking.',
        audio: null
      }
    ]);
  }, []);

  // Handle language change
  const handleLanguageChange = (language) => {
    setSelectedLanguage(language);
  };

  // Handle new user message
  const handleNewMessage = (message, audio = null) => {
    // Add user message to chat
    setMessages(prev => [...prev, { role: 'user', content: message, audio }]);
  };

  // Handle AI response
  const handleAIResponse = (response, audioUrl = null) => {
    // Add AI response to chat
    setMessages(prev => [...prev, { role: 'assistant', content: response, audio: audioUrl }]);
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Krishi Kredit</h1>
        <p>Your AI-powered loan assistant for rural India</p>
      </header>

      <main className="app-main">
        <div className="language-container">
          <LanguageSelector 
            selectedLanguage={selectedLanguage} 
            onLanguageChange={handleLanguageChange} 
          />
        </div>

        <div className="chat-container">
          <ChatBox 
            messages={messages} 
            isProcessing={isProcessing}
          />
        </div>

        <div className="recorder-container">
          <Recorder 
            selectedLanguage={selectedLanguage}
            onNewMessage={handleNewMessage}
            onAIResponse={handleAIResponse}
            isRecording={isRecording}
            setIsRecording={setIsRecording}
            isProcessing={isProcessing}
            setIsProcessing={setIsProcessing}
          />
        </div>
      </main>

      <footer className="app-footer">
        <p>© 2025 Krishi Kredit - Powered by GroqCloud and Whisper</p>
      </footer>
    </div>
  );
}

export default App;
