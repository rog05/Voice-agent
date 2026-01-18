"""
FastAPI Backend for Riya AI Web UI
Handles audio processing, agent interaction, and session management
"""

import os
import shutil
import base64
import json
from datetime import datetime
from typing import Optional, Dict

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from pydantic import BaseModel

from audio_engine import AudioEngine
from agents import RiyaAgent
from database import CallDatabase

# Initialize FastAPI
app = FastAPI(title="Riya AI API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for UI
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize components
print("Initializing Riya components...")
audio_engine = AudioEngine(model_size="base")
agent = RiyaAgent()
database = CallDatabase()
print("✅ Components initialized")

# Ensure temp directory exists
TEMP_DIR = "static/temp"
os.makedirs(TEMP_DIR, exist_ok=True)

class SessionStats(BaseModel):
    total_interactions: int
    by_intent: Dict[str, int]
    by_language: Dict[str, int]

@app.get("/")
async def root():
    """Serve the main UI"""
    from fastapi.responses import FileResponse
    return FileResponse("static/index.html")

@app.post("/api/process-audio")
async def process_audio(file: UploadFile = File(...)):
    """
    Process uploaded audio file
    Returns transcript, intent, response text, and audio URL
    """
    try:
        # Save uploaded file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"input_{timestamp}_{file.filename}"
        file_path = os.path.join(TEMP_DIR, filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Transcribe
        transcript, language = audio_engine.transcribe_file(file_path)
        
        if not transcript:
            return {"success": False, "error": "Could not transcribe audio"}
        
        # Process with agent
        response_text, intent = agent.process_query(transcript, language)
        
        # Generate response audio
        response_filename = f"response_{timestamp}.mp3"
        response_path = os.path.join(TEMP_DIR, response_filename)
        
        audio_engine.generate_audio_file(
            text=response_text,
            language=language,
            output_path=response_path
        )
        
        # Log interaction
        summary = database.generate_summary(transcript, intent)
        database.log_interaction(
            detected_language=language,
            user_transcript=transcript,
            detected_intent=intent,
            agent_response=response_text,
            summary=summary
        )
        
        # Return result
        return {
            "success": True,
            "transcript": transcript,
            "language": language,
            "intent": intent,
            "response_text": response_text,
            "audio_url": f"/static/temp/{response_filename}",
            "interaction_id": timestamp
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

@app.get("/api/session-stats")
async def get_stats():
    """Get session statistics"""
    stats = database.get_interaction_stats()
    return stats

@app.get("/api/clinic-info")
async def get_clinic_info():
    """Get clinic configuration"""
    return agent.clinic_config

# Cleanup task (run periodically or on startup)
def cleanup_temp_files():
    """Remove old temp files"""
    import time
    now = time.time()
    for f in os.listdir(TEMP_DIR):
        f_path = os.path.join(TEMP_DIR, f)
        if os.stat(f_path).st_mtime < now - 3600:  # Older than 1 hour
            os.remove(f_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
