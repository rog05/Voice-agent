# Riya - AI Medical Receptionist

**Riya** is a multilingual AI medical receptionist that handles appointment scheduling in English, Hindi, and Marathi with strict safety controls to prevent any medical advice.

## 🎯 Features

- **Multilingual Support**: Automatically detects and responds in English, Hindi, or Marathi
- **Voice Interaction**: Microphone-based speech input and audio output
- **Safety-First**: Multiple validation layers prevent any medical advice
- **Local Deployment**: Runs entirely on your local machine
- **Call Logging**: SQLite database tracks all interactions
- **Professional Persona**: Polite, empathetic Indian receptionist voice

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Microphone for voice input
- Google Gemini API key

### Installation

1. **Clone or download this project**

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API key**:
   - Copy `.env.example` to `.env`:
     ```bash
     copy .env.example .env
     ```
   - Edit `.env` and add your Google Gemini API key:
     ```
     GOOGLE_API_KEY=your_actual_api_key_here
     ```
   - Get your Google API key from: https://makersuite.google.com/app/apikey

5. **Configure clinic information** (optional):
   - Edit `clinic_config.json` with your clinic's details

### Running Riya

#### Option 1: Web Interface (Recommended)

1. Start the API server:
   ```bash
   python api.py
   ```

2. Open your browser and go to:
   http://localhost:8000

#### Option 2: Command Line Interface

```bash
python main.py
```

The system will:
1. Initialize all components (STT, TTS, AI agent)
2. Greet you with "Namaste!"
3. Listen for your voice input
4. Respond appropriately in your language
5. Log all interactions to `calls.db`

### Stopping Riya

- Press `Ctrl+C` to gracefully shut down
- Or say "exit", "quit", "goodbye", or "bye"

## 📋 What Riya Can Do

### ✅ Allowed Scope

- **Appointment booking**: Schedule new appointments
- **Appointment rescheduling**: Change existing appointments
- **Appointment cancellation**: Cancel appointments
- **Clinic information**:
  - Working hours
  - Location/address
  - Consultation fees
  - Doctor availability

### ❌ Strictly Forbidden

Riya will **NEVER**:
- Give medical advice
- Discuss symptoms
- Suggest medicines
- Explain diseases
- Interpret medical reports
- Provide home remedies
- Answer health-related questions

If you ask anything medical, Riya will politely redirect you to consult the doctor directly.

## 🗣️ Language Support

Riya automatically detects and responds in:
- **English** (with Indian accent)
- **Hindi** (हिंदी)
- **Marathi** (मराठी)

Simply speak in your preferred language, and Riya will respond in the same language.

## 🏗️ Project Structure

```
Riya-ai/
├── main.py              # Main event loop and orchestration
├── agents.py            # CrewAI agent with Gemini 1.5 Flash
├── audio_engine.py      # Speech-to-Text, Text-to-Speech, VAD
├── database.py          # SQLite logging and summaries
├── clinic_config.json   # Clinic information
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
├── .env                 # Your API key (create this)
└── calls.db            # SQLite database (auto-created)
```

## 🧪 Testing

### Test Individual Components

1. **Test Database**:
   ```bash
   python database.py
   ```

2. **Test Audio Engine**:
   ```bash
   python audio_engine.py
   ```

3. **Test Agent**:
   ```bash
   python agents.py
   ```

### Test Conversations

Try these test scenarios:

**English:**
- "I want to book an appointment"
- "What are your working hours?"
- "I have a headache" (should trigger safety fallback)

**Hindi:**
- "मुझे अपॉइंटमेंट बुक करना है"
- "आपके क्लिनिक का समय क्या है?"

**Marathi:**
- "मला अपॉइंटमेंट बुक करायचे आहे"
- "तुमचे क्लिनिक कुठे आहे?"

## 🔧 Troubleshooting

### PyAudio Installation Issues

**Windows:**
```bash
pip install pipwin
pipwin install pyaudio
```

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**Linux:**
```bash
sudo apt-get install portaudio19-dev
pip install pyaudio
```

### Microphone Not Working

- Check your microphone permissions
- Ensure your microphone is set as the default input device
- Adjust `SILENCE_THRESHOLD` in `audio_engine.py` if needed

### API Key Errors

- Verify your API key is correct in `.env`
- Ensure you have API quota available
- Check your internet connection

### Slow Transcription

- The first transcription may be slow as Whisper loads
- Consider using a smaller model (change `model_size` in `main.py`)
- Options: `tiny`, `base`, `small`, `medium`

## 📊 Database

All interactions are logged to `calls.db` with:
- Timestamp
- Detected language
- User transcript
- Detected intent
- Agent response
- Summary

View the database:
```bash
sqlite3 calls.db "SELECT * FROM interactions;"
```

## 🔒 Safety Features

1. **Intent Classification**: Pre-filters medical queries
2. **System Prompt**: Strict instructions to Gemini
3. **Response Validation**: Post-processing safety check
4. **Fallback Messages**: Exact, unmodifiable responses for out-of-scope queries
5. **Safety-First Logic**: When uncertain, always use fallback

## 📝 Customization

### Change Clinic Information

Edit `clinic_config.json`:
```json
{
  "clinic_name": "Your Clinic Name",
  "doctor_name": "Dr. Your Name",
  "location": "Your Address",
  "consultation_fee": "₹XXX",
  "working_hours": {
    "monday_friday": "9:00 AM - 6:00 PM",
    "saturday": "9:00 AM - 2:00 PM",
    "sunday": "Closed"
  }
}
```

### Adjust Voice Detection

In `audio_engine.py`, modify:
- `SILENCE_THRESHOLD`: Lower = more sensitive (default: 500)
- `SILENCE_DURATION`: Seconds of silence to detect end of speech (default: 2.0)

### Change Whisper Model

In `main.py`, change model size:
```python
self.audio_engine = AudioEngine(model_size="small")  # tiny, base, small, medium
```

## 📄 License

This project is for educational and demonstration purposes.

## 🙏 Acknowledgments

- **Faster Whisper**: Speech recognition
- **gTTS**: Text-to-speech
- **CrewAI**: Multi-agent framework
- **Google Gemini**: Language model
- **PyAudio**: Audio I/O

---

**Made with ❤️ for safer AI medical assistance**
