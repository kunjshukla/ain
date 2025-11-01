"""
Database Service Module
Handles all database operations and data persistence
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseService:
    """Centralized service for database operations"""
    
    def __init__(self):
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database connections and functions"""
        try:
            from database import (
                save_session, 
                get_session, 
                track_user_session, 
                get_user_performance
            )
            self.save_session = save_session
            self.get_session = get_session
            self.track_user_session = track_user_session
            self.get_user_performance = get_user_performance
            self.available = True
            logger.info("Database service initialized successfully")
        except ImportError:
            try:
                from backend.database import (
                    save_session, 
                    get_session, 
                    track_user_session, 
                    get_user_performance
                )
                self.save_session = save_session
                self.get_session = get_session
                self.track_user_session = track_user_session
                self.get_user_performance = get_user_performance
                self.available = True
                logger.info("Database service initialized successfully")
            except ImportError as e:
                logger.warning(f"Database functions not available: {e}")
                self.available = False
                self._setup_fallback_functions()
    
    def _setup_fallback_functions(self):
        """Setup fallback functions when database is not available"""
        def fallback_save_session(session_id, session_type, data):
            logger.info(f"Mock saving session {session_id} of type {session_type}")
            return True
        
        def fallback_get_session(session_id):
            return {
                "session_id": session_id, 
                "data": {}, 
                "timestamp": datetime.now().isoformat()
            }
        
        def fallback_track_user_session(user_id, session_id, session_type, data):
            logger.info(f"Mock tracking session {session_id} for user {user_id}")
            return True
        
        def fallback_get_user_performance(user_id):
            return {
                "user_id": user_id, 
                "sessions": [], 
                "metrics": {},
                "fallback": True
            }
        
        self.save_session = fallback_save_session
        self.get_session = fallback_get_session
        self.track_user_session = fallback_track_user_session
        self.get_user_performance = fallback_get_user_performance
    
    def is_available(self) -> bool:
        """Check if database service is available"""
        return self.available
    
    def save_user_session(self, session_id: str, session_type: str, data: Dict[str, Any]) -> bool:
        """Save a user session to the database"""
        try:
            return self.save_session(session_id, session_type, data)
        except Exception as e:
            logger.error(f"Error saving session {session_id}: {e}")
            return False
    
    def get_user_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a user session from the database"""
        try:
            return self.get_session(session_id)
        except Exception as e:
            logger.error(f"Error getting session {session_id}: {e}")
            return None
    
    def track_session(self, user_id: str, session_id: str, session_type: str, data: Dict[str, Any]) -> bool:
        """Track a user session with performance data"""
        try:
            return self.track_user_session(user_id, session_id, session_type, data)
        except Exception as e:
            logger.error(f"Error tracking session {session_id} for user {user_id}: {e}")
            return False
    
    def get_performance_data(self, user_id: str) -> Dict[str, Any]:
        """Get user performance data from the database"""
        try:
            result = self.get_user_performance(user_id)
            if not self.available:
                result["fallback"] = True
            return result
        except Exception as e:
            logger.error(f"Error getting performance data for user {user_id}: {e}")
            return {
                "user_id": user_id,
                "sessions": [],
                "metrics": {},
                "error": str(e),
                "fallback": True
            }
    
    def determine_session_type(self, session_data: Dict[str, Any]) -> str:
        """Determine session type based on data content"""
        if "interview_score" in session_data:
            return "interview"
        elif "code_correctness" in session_data:
            return "dsa"
        elif "resume_skills" in session_data:
            return "resume"
        else:
            return "unknown"

# Global database service instance
database_service = DatabaseService()
