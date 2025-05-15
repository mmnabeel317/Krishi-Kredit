# Smart Loan Helper

An AI-powered loan assistant web app designed to help rural Indian users, especially farmers, apply for loans using a friendly, speech-based assistant in their local language.

## Features

- **Multilingual Speech Input (STT)**: Record and transcribe audio in various Indian languages using faster-whisper
- **Conversational AI via GroqCloud**: Friendly AI loan officer powered by LLaMA3 or Mixtral models
- **Loan Recommendation**: Get personalized loan suggestions based on your conversation
- **Text-to-Speech Response**: Hear responses in your local language using gTTS

## Tech Stack

- **Backend**: Python Flask
- **Frontend**: React with Vite
- **AI Model**: GroqCloud (Mixtral or LLaMA3)
- **Speech-to-Text**: faster-whisper for multilingual transcription
- **Text-to-Speech**: gTTS for voice output in Indian local languages

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- GroqCloud API key

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/smart-loan-helper.git
cd smart-loan-helper
```

### 2. Backend Setup

Create a `.env` file in the root directory with your GroqCloud API key:

```
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=your_secret_key_for_flask_sessions
USE_LLAMA3=true
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Start the Flask server:

```bash
cd backend
python app.py
```

The backend server will run on http://localhost:5000

### 3. Frontend Setup

Install Node.js dependencies:

```bash
cd frontend
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend will run on http://localhost:3000

## Usage

1. Open http://localhost:3000 in your web browser
2. Select your preferred Indian language from the dropdown
3. Click the "Start Recording" button and speak
4. The AI will transcribe your speech, process it, and respond in your language
5. Continue the conversation to get a personalized loan recommendation

## Supported Languages

- Hindi
- Bengali
- Tamil
- Telugu
- Marathi
- Gujarati
- Kannada
- Malayalam
- Punjabi
- English

## Sample Conversation Flow

1. **Language Selection**: User picks their preferred language (e.g., Kannada)
2. **AI**: Greets in Kannada and asks: "ನೀವು ಸಾಲವನ್ನು ಏಕೆ ಬೇಕು?" ("Why do you need a loan?")
3. **User speaks answer**
4. **AI**: Asks follow-up questions in Kannada
5. **User responds to each question**
6. **AI compiles response**: Provides loan recommendation with interest rate and next steps

## License

MIT

## Acknowledgements

- GroqCloud for providing the AI model API
- faster-whisper for the speech-to-text capabilities
- gTTS for the text-to-speech functionality
