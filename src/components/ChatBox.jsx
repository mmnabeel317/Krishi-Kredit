import { useRef, useEffect } from 'react';

const ChatBox = ({ messages, isProcessing }) => {
  const chatEndRef = useRef(null);

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="chat-box">
      <div className="messages-container">
        {messages.map((message, index) => (
          <div 
            key={index} 
            className={`message ${message.role === 'assistant' ? 'assistant' : 'user'}`}
          >
            <div className="message-content">
              <p>{message.content}</p>
              {message.audio && message.role === 'assistant' && (
                <div className="audio-controls">
                  <audio controls src={message.audio}>
                    Your browser does not support the audio element.
                  </audio>
                </div>
              )}
            </div>
          </div>
        ))}
        
        {isProcessing && (
          <div className="message assistant">
            <div className="message-content typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        
        <div ref={chatEndRef} />
      </div>
    </div>
  );
};

export default ChatBox;
