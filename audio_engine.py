"""
Audio Engine module for Riya AI Medical Receptionist
Handles Speech-to-Text, Text-to-Speech, and Voice Activity Detection
"""

import os
import tempfile
import time
from typing import Optional, Tuple
import numpy as np

# Audio I/O
try:
    import pyaudio
except ImportError:
    print("⚠️ PyAudio not installed. Install with: pip install pyaudio")
    pyaudio = None

# Text-to-Speech
try:
    from gtts import gTTS
except ImportError:
    print("⚠️ gTTS not installed. Install with: pip install gTTS")
    gTTS = None

# Audio playback
try:
    import pygame
    pygame.mixer.init()
except ImportError:
    print("⚠️ pygame not installed. Install with: pip install pygame")
    pygame = None

# Speech-to-Text
try:
    from faster_whisper import WhisperModel
except ImportError:
    print("⚠️ faster-whisper not installed. Install with: pip install faster-whisper")
    WhisperModel = None


class AudioEngine:
    """Handles all audio input/output operations"""
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize the audio engine
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self.whisper_model = None
        self.audio = None
        
        # Audio parameters
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16 if pyaudio else None
        self.CHANNELS = 1
        self.RATE = 16000
        self.SILENCE_THRESHOLD = 500  # Adjust based on environment
        self.SILENCE_DURATION = 2.0  # Seconds of silence to detect end of speech
        
        self._initialize_whisper()
        self._initialize_pyaudio()
    
    def _initialize_whisper(self):
        """Initialize Faster Whisper model"""
        if WhisperModel is None:
            print("⚠️ Whisper model not available")
            return
        
        try:
            print(f"Loading Whisper model: {self.model_size}...")
            self.whisper_model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
            print("✅ Whisper model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading Whisper model: {e}")
            self.whisper_model = None
    
    def _initialize_pyaudio(self):
        """Initialize PyAudio"""
        if pyaudio is None:
            print("⚠️ PyAudio not available")
            return
        
        try:
            self.audio = pyaudio.PyAudio()
            print("✅ PyAudio initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing PyAudio: {e}")
            self.audio = None
    
    def detect_language(self, text: str) -> str:
        """
        Detect language from text
        
        Args:
            text: Input text
            
        Returns:
            Language code: 'English', 'Hindi', or 'Marathi'
        """
        # Simple heuristic: check for Devanagari script
        if any('\u0900' <= char <= '\u097F' for char in text):
            # Devanagari script - could be Hindi or Marathi
            # For now, we'll use keyword detection
            marathi_keywords = ['नमस्कार', 'काय', 'आहे', 'मला', 'तुम्ही']
            hindi_keywords = ['नमस्ते', 'क्या', 'है', 'मुझे', 'आप']
            
            text_lower = text.lower()
            marathi_count = sum(1 for kw in marathi_keywords if kw in text_lower)
            hindi_count = sum(1 for kw in hindi_keywords if kw in text_lower)
            
            if marathi_count > hindi_count:
                return 'Marathi'
            else:
                return 'Hindi'
        else:
            return 'English'
    
    def get_language_code(self, language: str) -> str:
        """
        Get gTTS language code
        
        Args:
            language: Language name (English/Hindi/Marathi)
            
        Returns:
            gTTS language code
        """
        mapping = {
            'English': 'en',
            'Hindi': 'hi',
            'Marathi': 'mr'
        }
        return mapping.get(language, 'en')
    
    def get_tts_language_code(self, language: str) -> str:
        """
        Get TTS language code with Indian accent
        
        Args:
            language: Language name
            
        Returns:
            Language code for TTS
        """
        if language == 'English':
            return 'en-in'  # Indian English
        elif language == 'Hindi':
            return 'hi'
        elif language == 'Marathi':
            return 'mr'
        else:
            return 'en-in'
    
    def listen_and_transcribe(self, timeout: int = 30) -> Tuple[Optional[str], Optional[str]]:
        """
        Listen to microphone and transcribe speech
        
        Args:
            timeout: Maximum time to listen in seconds
            
        Returns:
            Tuple of (transcript, detected_language) or (None, None) if failed
        """
        if self.audio is None or self.whisper_model is None:
            print("❌ Audio engine not properly initialized")
            return None, None
        
        print("\n🎤 Listening... (speak now)")
        
        frames = []
        stream = None
        
        try:
            # Open audio stream
            stream = self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )
            
            silence_chunks = 0
            max_silence_chunks = int(self.SILENCE_DURATION * self.RATE / self.CHUNK)
            recording_started = False
            
            start_time = time.time()
            
            while True:
                # Check timeout
                if time.time() - start_time > timeout:
                    print("⏱️ Timeout reached")
                    break
                
                # Read audio chunk
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                frames.append(data)
                
                # Convert to numpy array for analysis
                audio_data = np.frombuffer(data, dtype=np.int16)
                volume = np.abs(audio_data).mean()
                
                # Detect speech
                if volume > self.SILENCE_THRESHOLD:
                    recording_started = True
                    silence_chunks = 0
                    print("🔊", end="", flush=True)
                else:
                    if recording_started:
                        silence_chunks += 1
                        print(".", end="", flush=True)
                
                # Check if we've detected end of speech
                if recording_started and silence_chunks >= max_silence_chunks:
                    print("\n✅ End of speech detected")
                    break
            
            # Close stream
            stream.stop_stream()
            stream.close()
            
            if not recording_started:
                print("⚠️ No speech detected")
                return None, None
            
            # Save audio to temporary file
            temp_audio = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            temp_audio_path = temp_audio.name
            temp_audio.close()
            
            # Write WAV file
            import wave
            wf = wave.open(temp_audio_path, 'wb')
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            # Transcribe with Whisper
            print("🔄 Transcribing...")
            segments, info = self.whisper_model.transcribe(temp_audio_path, beam_size=5)
            
            transcript = " ".join([segment.text for segment in segments]).strip()
            
            # Clean up temp file
            os.unlink(temp_audio_path)
            
            if not transcript:
                print("⚠️ No transcript generated")
                return None, None
            
            # Detect language
            detected_language = self.detect_language(transcript)
            
            print(f"📝 Transcript ({detected_language}): {transcript}")
            
            return transcript, detected_language
            
        except Exception as e:
            print(f"❌ Error during transcription: {e}")
            if stream:
                stream.stop_stream()
                stream.close()
            return None, None

    def transcribe_file(self, file_path: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Transcribe an audio file
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Tuple of (transcript, detected_language) or (None, None) if failed
        """
        if self.whisper_model is None:
            print("❌ Whisper model not initialized")
            return None, None
            
        try:
            print(f"🔄 Transcribing file: {file_path}...")
            segments, info = self.whisper_model.transcribe(file_path, beam_size=5)
            
            transcript = " ".join([segment.text for segment in segments]).strip()
            
            if not transcript:
                print("⚠️ No transcript generated")
                return None, None
            
            # Detect language
            detected_language = self.detect_language(transcript)
            
            print(f"📝 Transcript ({detected_language}): {transcript}")
            
            return transcript, detected_language
            
        except Exception as e:
            print(f"❌ Error during file transcription: {e}")
            return None, None
    
    def generate_audio_file(self, text: str, language: str = "English", output_path: str = None) -> Optional[str]:
        """
        Convert text to speech and save to file without playing
        
        Args:
            text: Text to speak
            language: Language (English/Hindi/Marathi)
            output_path: Optional path to save file
            
        Returns:
            Path to saved audio file or None if failed
        """
        if gTTS is None:
            print(f"⚠️ TTS not available")
            return None
        
        try:
            # Get language code
            lang_code = self.get_language_code(language)
            
            # Generate speech
            print(f"🔊 Generating audio ({language}): {text}")
            tts = gTTS(text=text, lang=lang_code, slow=False)
            
            # Save to temporary file if path not provided
            if not output_path:
                temp_audio = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
                output_path = temp_audio.name
                temp_audio.close()
            
            tts.save(output_path)
            
            return output_path
            
        except Exception as e:
            print(f"❌ Error during TTS generation: {e}")
            return None

    def speak(self, text: str, language: str = "English"):
        """
        Convert text to speech and play it
        
        Args:
            text: Text to speak
            language: Language (English/Hindi/Marathi)
        """
        if gTTS is None or pygame is None:
            print(f"⚠️ TTS not available. Would say: {text}")
            return
        
        try:
            # Generate audio file
            temp_audio_path = self.generate_audio_file(text, language)
            
            if not temp_audio_path:
                return

            # Play audio
            pygame.mixer.music.load(temp_audio_path)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            # Clean up
            pygame.mixer.music.unload()
            time.sleep(0.2)  # Small delay to ensure file is released
            
            try:
                os.unlink(temp_audio_path)
            except:
                pass  # File might still be locked on Windows
            
        except Exception as e:
            print(f"❌ Error during TTS: {e}")
            print(f"   Would say: {text}")
    
    def cleanup(self):
        """Clean up resources"""
        if self.audio:
            self.audio.terminate()
        
        if pygame and pygame.mixer.get_init():
            pygame.mixer.quit()


if __name__ == "__main__":
    # Test the audio engine
    print("Testing AudioEngine...")
    
    engine = AudioEngine(model_size="base")
    
    # Test language detection
    print("\n--- Testing Language Detection ---")
    print(f"English: {engine.detect_language('Hello, how are you?')}")
    print(f"Hindi: {engine.detect_language('नमस्ते, आप कैसे हैं?')}")
    print(f"Marathi: {engine.detect_language('नमस्कार, तुम्ही कसे आहात?')}")
    
    # Test TTS
    print("\n--- Testing Text-to-Speech ---")
    engine.speak("Hello, I am Riya, your medical receptionist.", "English")
    time.sleep(1)
    
    print("\n✅ Audio engine test completed!")
    
    engine.cleanup()
