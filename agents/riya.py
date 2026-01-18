"""
Agents module for Riya AI Medical Receptionist
Defines CrewAI agents and tasks with Gemini 1.5 Flash
"""

import os
import json
from typing import Dict, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from crewai import Agent, Task, Crew
    from langchain_huggingface import HuggingFaceEndpoint
except ImportError:
    print("⚠️ CrewAI or langchain-huggingface not installed")
    Agent = Task = Crew = HuggingFaceEndpoint = None


# Riya SYSTEM PROMPT (from instructions.md)
Riya_SYSTEM_PROMPT = """
You are **Riya**, an automated AI Medical Receptionist for a medical clinic in India.

========================
IDENTITY & PERSONA
========================
- Name: Riya
- Role: Medical Receptionist (NOT a doctor)
- Gendered Persona: Professional female receptionist
- Accent & Style: Indian, polite, calm, empathetic
- Tone: Courteous, concise, respectful
- Greeting Style:
  - English: "Hello" or "Namaste"
  - Hindi: "नमस्ते"
  - Marathi: "नमस्कार"

You MUST always respond in the SAME language as the user input.
Auto-detect the language and mirror it exactly.

========================
STRICT SCOPE (VERY IMPORTANT)
========================
You are ONLY allowed to handle:
1. Appointment booking
2. Appointment rescheduling
3. Appointment cancellation
4. General clinic information ONLY:
   - Clinic working hours
   - Clinic location
   - Consultation fees
   - Doctor availability (non-medical)

========================
ABSOLUTELY FORBIDDEN
========================
You must NEVER:
- Give medical advice
- Discuss symptoms
- Suggest medicines
- Explain diseases
- Interpret reports
- Give home remedies
- Answer health-related questions

You are NOT a doctor.
You are NOT a nurse.
You are NOT a medical advisor.

========================
MANDATORY FALLBACK RESPONSE
========================
If the user asks ANYTHING outside appointment scheduling or clinic information,
you MUST respond with the following message ONLY, translated into the detected language.

English:
"I apologize, but I am an automated assistant for appointments only. I cannot provide medical advice. Please consult the doctor directly for any health concerns."

Hindi:
"मुझे खेद है, लेकिन मैं केवल अपॉइंटमेंट से संबंधित सहायता के लिए बनाई गई एक स्वचालित सहायक हूँ। मैं चिकित्सा सलाह प्रदान नहीं कर सकती। कृपया किसी भी स्वास्थ्य संबंधी समस्या के लिए सीधे डॉक्टर से परामर्श करें।"

Marathi:
"माफ करा, पण मी केवळ अपॉइंटमेंटसाठी मदत करणारी स्वयंचलित सहाय्यक आहे. मी वैद्यकीय सल्ला देऊ शकत नाही. कोणत्याही आरोग्यविषयक समस्येसाठी कृपया थेट डॉक्टरांचा सल्ला घ्या."

🚨 DO NOT modify, shorten, paraphrase, or add anything to this fallback message.

========================
INTENT CLASSIFICATION (INTERNAL)
========================
Internally classify user intent as ONE of the following:
- APPOINTMENT
- CLINIC_INFO
- OUT_OF_SCOPE

Rules:
- Medical questions → OUT_OF_SCOPE
- Symptoms → OUT_OF_SCOPE
- Medicines → OUT_OF_SCOPE
- Health concerns → OUT_OF_SCOPE

========================
RESPONSE RULES
========================
- Keep responses short and clear
- Be polite and culturally respectful
- Do NOT ask unnecessary follow-up questions
- Do NOT assume medical conditions
- Do NOT add disclaimers beyond the fallback message
- Never break character

========================
CRITICAL SAFETY OVERRIDE
========================
If there is ANY uncertainty whether a question is medical or not:
→ Treat it as OUT_OF_SCOPE
→ Use the fallback message

Safety > Helpfulness > Fluency

========================
FINAL AUTHORITY RULE
========================
You are a receptionist.
You handle appointments.
Nothing else.
"""


# Fallback messages by language
FALLBACK_MESSAGES = {
    'English': "I apologize, but I am an automated assistant for appointments only. I cannot provide medical advice. Please consult the doctor directly for any health concerns.",
    'Hindi': "मुझे खेद है, लेकिन मैं केवल अपॉइंटमेंट से संबंधित सहायता के लिए बनाई गई एक स्वचालित सहायक हूँ। मैं चिकित्सा सलाह प्रदान नहीं कर सकती। कृपया किसी भी स्वास्थ्य संबंधी समस्या के लिए सीधे डॉक्टर से परामर्श करें。",
    'Marathi': "माफ करा, पण मी केवळ अपॉइंटमेंटसाठी मदत करणारी स्वयंचलित सहाय्यक आहे. मी वैद्यकीय सल्ला देऊ शकत नाही. कोणत्याही आरोग्यविषयक समस्येसाठी कृपया थेट डॉक्टरांचा सल्ला घ्या."
}


class RiyaAgent:
    """Riya AI Agent using CrewAI and HuggingFace"""
    
    def __init__(self, clinic_config_path: str = "clinic_config.json"):
        """
        Initialize Riya agent
        
        Args:
            clinic_config_path: Path to clinic configuration file
        """
        self.clinic_config = self._load_clinic_config(clinic_config_path)
        self.llm = self._initialize_llm()
        self.agent = self._create_agent()
    
    def _load_clinic_config(self, config_path: str) -> Dict:
        """Load clinic configuration"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading clinic config: {e}")
            return {}
    
    def _initialize_llm(self):
        """Initialize Google Gemini LLM"""
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except ImportError:
            print("⚠️ langchain-google-genai not found. Installing...")
            import subprocess
            subprocess.check_call(["pip", "install", "langchain-google-genai"])
            from langchain_google_genai import ChatGoogleGenerativeAI

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ GOOGLE_API_KEY not found in environment variables")
            return None
        
        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=api_key,
                temperature=0.3,
                convert_system_message_to_human=True
            )
            print("✅ Google Gemini initialized successfully")
            return llm
        except Exception as e:
            print(f"❌ Error initializing Google Gemini: {e}")
            return None
    
    def _create_agent(self):
        """Create Riya agent"""
        if Agent is None or self.llm is None:
            print("⚠️ Cannot create agent - dependencies not available")
            return None
        
        try:
            # Create clinic info context
            clinic_context = f"""
            
CLINIC INFORMATION:
- Clinic Name: {self.clinic_config.get('clinic_name', 'N/A')}
- Doctor: {self.clinic_config.get('doctor_name', 'N/A')}
- Location: {self.clinic_config.get('location', 'N/A')}
- Consultation Fee: {self.clinic_config.get('consultation_fee', 'N/A')}
- Working Hours:
  - Monday-Friday: {self.clinic_config.get('working_hours', {}).get('monday_friday', 'N/A')}
  - Saturday: {self.clinic_config.get('working_hours', {}).get('saturday', 'N/A')}
  - Sunday: {self.clinic_config.get('working_hours', {}).get('sunday', 'N/A')}
"""
            
            agent = Agent(
                role="Medical Receptionist",
                goal="Handle appointment scheduling and provide clinic information while strictly avoiding any medical advice",
                backstory=Riya_SYSTEM_PROMPT + clinic_context,
                llm=self.llm,
                verbose=False,
                allow_delegation=False
            )
            
            print("✅ Riya agent created successfully")
            return agent
            
        except Exception as e:
            print(f"❌ Error creating agent: {e}")
            return None
    
    def _classify_intent(self, transcript: str) -> str:
        """
        Classify user intent with safety-first approach
        
        Args:
            transcript: User's transcribed speech
            
        Returns:
            Intent: APPOINTMENT, CLINIC_INFO, or OUT_OF_SCOPE
        """
        transcript_lower = transcript.lower()
        
        # Medical keywords (if ANY are present, it's OUT_OF_SCOPE)
        medical_keywords = [
            'symptom', 'pain', 'hurt', 'ache', 'sick', 'ill', 'disease',
            'medicine', 'medication', 'drug', 'pill', 'tablet',
            'diagnosis', 'treatment', 'cure', 'remedy', 'heal',
            'fever', 'cough', 'cold', 'headache', 'stomach',
            'blood', 'pressure', 'sugar', 'diabetes', 'cancer',
            'infection', 'virus', 'bacteria',
            # Hindi/Marathi medical terms
            'दवा', 'बीमारी', 'लक्षण', 'दर्द', 'बुखार', 'इलाज',
            'औषध', 'आजार', 'वेदना', 'ताप', 'उपचार'
        ]
        
        # Check for medical keywords
        if any(keyword in transcript_lower for keyword in medical_keywords):
            return 'OUT_OF_SCOPE'
        
        # Appointment keywords
        appointment_keywords = [
            'appointment', 'book', 'schedule', 'reschedule', 'cancel',
            'visit', 'meet', 'see doctor', 'consultation',
            'अपॉइंटमेंट', 'बुक', 'मिलना', 'डॉक्टर',
            'भेट', 'वेळ'
        ]
        
        if any(keyword in transcript_lower for keyword in appointment_keywords):
            return 'APPOINTMENT'
        
        # Clinic info keywords
        clinic_keywords = [
            'hours', 'timing', 'time', 'location', 'address', 'where',
            'fee', 'cost', 'charge', 'price', 'open', 'closed',
            'समय', 'पता', 'फीस', 'खुला',
            'वेळ', 'पत्ता', 'शुल्क'
        ]
        
        if any(keyword in transcript_lower for keyword in clinic_keywords):
            return 'CLINIC_INFO'
        
        # If uncertain, treat as OUT_OF_SCOPE (safety first)
        return 'OUT_OF_SCOPE'
    
    def _validate_response(self, response: str, intent: str, language: str) -> str:
        """
        Validate response for safety before TTS
        
        Args:
            response: Agent's response
            intent: Detected intent
            language: Detected language
            
        Returns:
            Safe response (fallback if needed)
        """
        # If intent is OUT_OF_SCOPE, always use fallback
        if intent == 'OUT_OF_SCOPE':
            return FALLBACK_MESSAGES.get(language, FALLBACK_MESSAGES['English'])
        
        # Check if response contains medical terms (extra safety layer)
        medical_terms = [
            'diagnos', 'symptom', 'medicine', 'medication', 'treatment',
            'disease', 'illness', 'condition', 'prescription'
        ]
        
        response_lower = response.lower()
        if any(term in response_lower for term in medical_terms):
            print("⚠️ Medical content detected in response - using fallback")
            return FALLBACK_MESSAGES.get(language, FALLBACK_MESSAGES['English'])
        
        return response
    
    def process_query(self, transcript: str, language: str) -> Tuple[str, str]:
        """
        Process user query and generate response
        
        Args:
            transcript: User's transcribed speech
            language: Detected language
            
        Returns:
            Tuple of (response, intent)
        """
        if self.agent is None:
            return "System error. Please try again.", "ERROR"
        
        # Classify intent
        intent = self._classify_intent(transcript)
        print(f"🎯 Detected intent: {intent}")
        
        # If OUT_OF_SCOPE, return fallback immediately
        if intent == 'OUT_OF_SCOPE':
            response = FALLBACK_MESSAGES.get(language, FALLBACK_MESSAGES['English'])
            return response, intent
        
        try:
            # Create task for the agent
            task = Task(
                description=f"""
User said (in {language}): "{transcript}"

Respond appropriately in {language}. Keep your response short, polite, and helpful.
Remember: You can ONLY help with appointments and clinic information. Nothing else.
""",
                agent=self.agent,
                expected_output=f"A polite, concise response in {language}"
            )
            
            # Create crew and execute
            crew = Crew(
                agents=[self.agent],
                tasks=[task],
                verbose=False
            )
            
            result = crew.kickoff()
            
            # Extract response text
            if hasattr(result, 'raw'):
                response = result.raw
            else:
                response = str(result)
            
            # Validate response for safety
            response = self._validate_response(response, intent, language)
            
            return response, intent
            
        except Exception as e:
            print(f"❌ Error processing query: {e}")
            # Return fallback on error (safety first)
            return FALLBACK_MESSAGES.get(language, FALLBACK_MESSAGES['English']), 'ERROR'


if __name__ == "__main__":
    # Test the agent
    print("Testing RiyaAgent...")
    
    agent = RiyaAgent()
    
    # Test cases
    test_cases = [
        ("I want to book an appointment", "English"),
        ("What are your working hours?", "English"),
        ("I have a headache, what should I do?", "English"),  # Should trigger fallback
    ]
    
    for transcript, language in test_cases:
        print(f"\n--- Test: {transcript} ---")
        response, intent = agent.process_query(transcript, language)
        print(f"Intent: {intent}")
        print(f"Response: {response}")
    
    print("\n✅ Agent test completed!")
