"""
Performance Routes Module
Handles user performance tracking and analytics endpoints
"""

from fastapi import APIRouter, HTTPException
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

router = APIRouter()

@router.get("/{user_id}")
@handle_errors("get_performance")
async def get_performance(user_id: str):
    """Get user performance metrics and analytics"""
    # Try to get data from AI service first
    ai_performance = ai_service.get_user_performance(user_id)
    
    # Try to get data from database
    db_performance = database_service.get_performance_data(user_id)
    
    # Prioritize database data if available and not a fallback
    if db_performance and not db_performance.get("fallback", False):
        return db_performance
    elif ai_performance and not ai_performance.get("fallback", False):
        return ai_performance
    else:
        # Return fallback with combined data
        return error_handler.create_fallback_response(
            "performance_retrieval",
            {
                "user_id": user_id,
                "activity": {"total_sessions": 0},
                "metrics": {},
                "insights": [],
                "recommendations": ["Start practicing to build performance data."]
            }
        )
