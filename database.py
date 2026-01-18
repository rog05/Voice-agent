"""
Database module for Riya AI Medical Receptionist
Handles SQLite logging and call summaries
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import os


class CallDatabase:
    """Manages SQLite database for call interactions"""
    
    def __init__(self, db_path: str = "calls.db"):
        """Initialize database connection and create tables if needed"""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
    
    def _create_tables(self):
        """Create interactions table if it doesn't exist"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                detected_language TEXT NOT NULL,
                user_transcript TEXT NOT NULL,
                detected_intent TEXT NOT NULL,
                agent_response TEXT NOT NULL,
                summary TEXT
            )
        """)
        self.conn.commit()
    
    def log_interaction(
        self,
        detected_language: str,
        user_transcript: str,
        detected_intent: str,
        agent_response: str,
        summary: Optional[str] = None
    ) -> int:
        """
        Log a single interaction to the database
        
        Args:
            detected_language: Language detected (English/Hindi/Marathi)
            user_transcript: What the user said
            detected_intent: APPOINTMENT/CLINIC_INFO/OUT_OF_SCOPE
            agent_response: Riya's response
            summary: Optional single-sentence summary
            
        Returns:
            ID of the inserted record
        """
        timestamp = datetime.now().isoformat()
        
        self.cursor.execute("""
            INSERT INTO interactions 
            (timestamp, detected_language, user_transcript, detected_intent, agent_response, summary)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (timestamp, detected_language, user_transcript, detected_intent, agent_response, summary))
        
        self.conn.commit()
        return self.cursor.lastrowid
    
    def generate_summary(self, user_transcript: str, intent: str) -> str:
        """
        Generate a single-sentence summary of the interaction
        
        Args:
            user_transcript: What the user said
            intent: Detected intent
            
        Returns:
            Single sentence summary
        """
        if intent == "APPOINTMENT":
            return f"User called to book or manage an appointment."
        elif intent == "CLINIC_INFO":
            return f"User inquired about clinic information."
        elif intent == "OUT_OF_SCOPE":
            return f"User asked a question outside the scope of appointment scheduling."
        else:
            return f"User interaction recorded."
    
    def get_recent_interactions(self, limit: int = 10) -> List[Dict]:
        """
        Retrieve recent interactions
        
        Args:
            limit: Number of recent interactions to retrieve
            
        Returns:
            List of interaction dictionaries
        """
        self.cursor.execute("""
            SELECT id, timestamp, detected_language, user_transcript, 
                   detected_intent, agent_response, summary
            FROM interactions
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        rows = self.cursor.fetchall()
        
        interactions = []
        for row in rows:
            interactions.append({
                'id': row[0],
                'timestamp': row[1],
                'detected_language': row[2],
                'user_transcript': row[3],
                'detected_intent': row[4],
                'agent_response': row[5],
                'summary': row[6]
            })
        
        return interactions
    
    def get_interaction_stats(self) -> Dict:
        """
        Get statistics about interactions
        
        Returns:
            Dictionary with stats
        """
        # Total interactions
        self.cursor.execute("SELECT COUNT(*) FROM interactions")
        total = self.cursor.fetchone()[0]
        
        # By intent
        self.cursor.execute("""
            SELECT detected_intent, COUNT(*) 
            FROM interactions 
            GROUP BY detected_intent
        """)
        by_intent = dict(self.cursor.fetchall())
        
        # By language
        self.cursor.execute("""
            SELECT detected_language, COUNT(*) 
            FROM interactions 
            GROUP BY detected_language
        """)
        by_language = dict(self.cursor.fetchall())
        
        return {
            'total_interactions': total,
            'by_intent': by_intent,
            'by_language': by_language
        }
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


if __name__ == "__main__":
    # Test the database
    print("Testing CallDatabase...")
    
    db = CallDatabase("test_calls.db")
    
    # Log a test interaction
    interaction_id = db.log_interaction(
        detected_language="English",
        user_transcript="I want to book an appointment",
        detected_intent="APPOINTMENT",
        agent_response="Sure, I can help you book an appointment. What day works best for you?",
        summary="User called to book an appointment."
    )
    
    print(f"Logged interaction with ID: {interaction_id}")
    
    # Get recent interactions
    recent = db.get_recent_interactions(5)
    print(f"\nRecent interactions: {len(recent)}")
    for interaction in recent:
        print(f"  - {interaction['timestamp']}: {interaction['user_transcript'][:50]}...")
    
    # Get stats
    stats = db.get_interaction_stats()
    print(f"\nStats: {stats}")
    
    db.close()
    
    # Clean up test database
    if os.path.exists("test_calls.db"):
        os.remove("test_calls.db")
    
    print("\n✅ Database module test completed successfully!")
