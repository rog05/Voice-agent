# Quick Start Guide for Riya AI

## ✅ What's Already Done

All components have been implemented and tested:
- ✅ Database module (SQLite logging)
- ✅ Audio engine (STT, TTS, VAD)
- ✅ Agent system (CrewAI + Gemini)
- ✅ Main application (event loop)
- ✅ Virtual environment created
- ✅ Dependencies installed

## 🚀 Next Steps (Required Before Running)

### 1. Get Your Google Gemini API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key

### 2. Configure the API Key

1. Open the `.env` file in the `Riya-ai` folder
2. Replace `your_gemini_api_key_here` with your actual API key
3. Save the file

Example:
```
GOOGLE_API_KEY=AIzaSyABC123XYZ789...
```

### 3. (Optional) Customize Clinic Information

Edit `clinic_config.json` with your clinic's details:
- Clinic name
- Doctor name
- Location
- Working hours
- Consultation fee

## 🎯 Running Riya

### Option 1: Using Command Line

```bash
cd "c:\Users\Rohan\Desktop\Voice AI\Riya-ai"
.\venv\Scripts\activate
python main.py
```

### Option 2: Using PowerShell (Direct)

```powershell
cd "c:\Users\Rohan\Desktop\Voice AI\Riya-ai"
.\venv\Scripts\python.exe main.py
```

## 🗣️ How to Use

1. **Start the application** - Run `python main.py`
2. **Wait for greeting** - Riya will say "Namaste!"
3. **Speak into your microphone** - Say your request
4. **Wait for silence detection** - Stop speaking and wait 2 seconds
5. **Listen to response** - Riya will respond in your language
6. **Repeat** - Continue the conversation
7. **Exit** - Say "goodbye", "exit", or press Ctrl+C

## 📝 Test Scenarios

### ✅ Allowed Queries (Should Work)

**English:**
- "I want to book an appointment"
- "What are your working hours?"
- "Where is your clinic?"
- "What is the consultation fee?"
- "Can I reschedule my appointment?"

**Hindi:**
- "मुझे अपॉइंटमेंट बुक करना है"
- "आपके क्लिनिक का समय क्या है?"
- "आपका क्लिनिक कहाँ है?"

**Marathi:**
- "मला अपॉइंटमेंट बुक करायचे आहे"
- "तुमचे क्लिनिक कुठे आहे?"
- "तुमचे शुल्क किती आहे?"

### ❌ Rejected Queries (Should Trigger Fallback)

These will get the polite "I cannot provide medical advice" response:

- "I have a headache"
- "What medicine should I take?"
- "I have fever, what should I do?"
- "मुझे बुखार है" (I have fever)
- "मला डोकेदुखी आहे" (I have headache)

## 🧪 Testing Without Microphone

Run the test script to verify the agent works:

```bash
.\venv\Scripts\python test_Riya.py
```

This will test:
- Language detection
- Intent classification
- Safety fallback system

## 🔧 Troubleshooting

### "GOOGLE_API_KEY not configured"
- Make sure you edited the `.env` file
- Check that there are no extra spaces
- Verify the API key is valid

### Microphone Not Working
- Check Windows microphone permissions
- Ensure microphone is set as default input device
- Test microphone in Windows settings first

### Slow First Response
- First transcription is slow as Whisper model loads
- Subsequent responses will be faster
- This is normal behavior

### PyAudio Errors
If you get PyAudio errors, run:
```bash
pip install pipwin
pipwin install pyaudio
```

## 📊 View Interaction Logs

After using Riya, view the database logs:

```bash
sqlite3 calls.db "SELECT * FROM interactions;"
```

Or use a SQLite browser tool to view `calls.db`

## 📁 Project Files

```
Riya-ai/
├── main.py              - Start here to run Riya
├── agents.py            - AI agent logic
├── audio_engine.py      - Voice processing
├── database.py          - Logging system
├── clinic_config.json   - Customize your clinic info
├── .env                 - ADD YOUR API KEY HERE
├── README.md           - Full documentation
├── test_Riya.py    - Test script
└── calls.db            - Interaction logs (auto-created)
```

## 🎉 You're Ready!

Once you add your API key, you can run:

```bash
python main.py
```

And start talking to Riya! 🙏
