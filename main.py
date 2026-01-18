"""
Main module for Riya AI Medical Receptionist
Orchestrates the voice interaction loop
"""

import os
import sys
import signal
from datetime import datetime

from audio_engine import AudioEngine
from agents import RiyaAgent
from database import CallDatabase


class RiyaReceptionist:
    """Main orchestrator for Riya AI"""
    
    def __init__(self):
        """Initialize all components"""
        print("=" * 60)
        print("🙏 Riya - AI Medical Receptionist")
        print("=" * 60)
        print()
        
        # Initialize components
        print("Initializing components...")
        self.audio_engine = AudioEngine(model_size="base")
        self.agent = RiyaAgent()
        self.database = CallDatabase()
        
        # Session tracking
        self.session_active = True
        self.interaction_count = 0
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        
        print()
        print("✅ All components initialized successfully!")
        print()
    
    def _signal_handler(self, sig, frame):
        """Handle Ctrl+C gracefully"""
        print("\n\n🛑 Shutting down gracefully...")
        self.session_active = False
    
    def greet(self):
        """Initial greeting"""
        greeting = "Namaste! I am Riya, your medical receptionist. How may I help you today?"
        print(f"\n💬 Riya: {greeting}")
        self.audio_engine.speak(greeting, "English")
    
    def run(self):
        """Main interaction loop"""
        try:
            # Greet the user
            self.greet()
            
            # Main loop
            while self.session_active:
                print("\n" + "-" * 60)
                
                # Listen to user
                transcript, detected_language = self.audio_engine.listen_and_transcribe()
                
                if transcript is None or not transcript.strip():
                    print("⚠️ No input detected. Please try again.")
                    continue
                
                # Check for exit commands
                exit_commands = ['exit', 'quit', 'goodbye', 'bye', 'stop', 
                                'बाहर निकलें', 'बंद करें', 'बाय',
                                'बाहेर पडा', 'बंद करा']
                if any(cmd in transcript.lower() for cmd in exit_commands):
                    print("\n👋 User requested to exit")
                    farewell = self._get_farewell(detected_language)
                    print(f"💬 Riya: {farewell}")
                    self.audio_engine.speak(farewell, detected_language)
                    break
                
                # Process with agent
                print(f"\n🤖 Processing query...")
                response, intent = self.agent.process_query(transcript, detected_language)
                
                # Speak response
                print(f"💬 Riya ({detected_language}): {response}")
                self.audio_engine.speak(response, detected_language)
                
                # Log to database
                summary = self.database.generate_summary(transcript, intent)
                self.database.log_interaction(
                    detected_language=detected_language,
                    user_transcript=transcript,
                    detected_intent=intent,
                    agent_response=response,
                    summary=summary
                )
                
                self.interaction_count += 1
                print(f"✅ Interaction logged (Total: {self.interaction_count})")
        
        except Exception as e:
            print(f"\n❌ Error in main loop: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.cleanup()
    
    def _get_farewell(self, language: str) -> str:
        """Get farewell message in appropriate language"""
        farewells = {
            'English': "Thank you for calling. Have a great day! Namaste.",
            'Hindi': "कॉल करने के लिए धन्यवाद। आपका दिन शुभ हो! नमस्ते।",
            'Marathi': "कॉल केल्याबद्दल धन्यवाद. तुमचा दिवस चांगला जावो! नमस्कार."
        }
        return farewells.get(language, farewells['English'])
    
    def cleanup(self):
        """Clean up resources"""
        print("\n🧹 Cleaning up resources...")
        
        # Show session summary
        if self.interaction_count > 0:
            print(f"\n📊 Session Summary:")
            print(f"   Total interactions: {self.interaction_count}")
            
            stats = self.database.get_interaction_stats()
            print(f"   By intent: {stats.get('by_intent', {})}")
            print(f"   By language: {stats.get('by_language', {})}")
        
        # Cleanup components
        self.audio_engine.cleanup()
        self.database.close()
        
        print("\n✅ Cleanup complete. Goodbye!")
        print("=" * 60)


def check_environment():
    """Check if environment is properly configured"""
    print("🔍 Checking environment...")
    
    # Check for .env file
    if not os.path.exists('.env'):
        print("\n⚠️ WARNING: .env file not found!")
        print("   Please create a .env file with your GOOGLE_API_KEY")
        print("   You can copy .env.example and add your API key")
        print()
        
        response = input("Do you want to continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            sys.exit(1)
    
    # Check for API key
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        print("\n❌ ERROR: GOOGLE_API_KEY not configured!")
        print("   Please set your Gemini API key in the .env file")
        sys.exit(1)
    
    print("✅ Environment check passed")
    print()


def main():
    """Main entry point"""
    # Check environment
    check_environment()
    
    # Create and run receptionist
    receptionist = RiyaReceptionist()
    receptionist.run()


if __name__ == "__main__":
    main()
