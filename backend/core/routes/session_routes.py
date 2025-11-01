"""
Session Routes Module
Handles session tracking and management endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

# Import core services
try:
    from core.services.ai_service import ai_service
    from core.services.database_service import database_service
    from core.error_handling import error_handler, handle_errors
except ImportError:
    from backend.core.services.ai_service import ai_service
    from backend.core.services.database_service import database_service
    from backend.core.error_handling import error_handler, handle_errors

# Import models
try:
    from orchestrator_schema import SessionRequest
except ImportError:
    from backend.orchestrator_schema import SessionRequest

router = APIRouter()

@router.post("/session")
@handle_errors("track_session")
def track_session(request: SessionRequest):
    """Track user session data and performance metrics"""
    session_id = None
    
    # Track session with AI service
    session_id = ai_service.track_performance(request.user_id, request.session_data)
    
    # Determine session type
    session_type = database_service.determine_session_type(request.session_data)
    
    # Track in database
    success = database_service.track_session(
        request.user_id,
        request.session_data.get("session_id", session_id),
        session_type,
        request.session_data
    )
    
    return {
        "status": "success" if success else "partial",
        "session_id": session_id,
        "session_type": session_type,
        "database_tracked": success
    }
