"""
Error Handling Module
Centralized error handling and logging for the application
"""

import logging
import traceback
from typing import Dict, Any, Optional
from fastapi import HTTPException
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class ErrorHandler:
    """Centralized error handling and logging"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def log_error(self, error: Exception, context: str = "", user_id: str = "") -> str:
        """Log an error with context and return error ID"""
        error_id = f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(error)) % 10000}"
        
        error_msg = f"Error ID: {error_id}"
        if user_id:
            error_msg += f" | User: {user_id}"
        if context:
            error_msg += f" | Context: {context}"
        error_msg += f" | Error: {str(error)}"
        
        self.logger.error(error_msg)
        self.logger.debug(f"Traceback for {error_id}: {traceback.format_exc()}")
        
        return error_id
    
    def create_fallback_response(self, operation: str, default_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a standardized fallback response"""
        response = {
            "status": "fallback",
            "operation": operation,
            "timestamp": datetime.now().isoformat(),
            "fallback": True
        }
        
        if default_data:
            response.update(default_data)
        
        return response
    
    def handle_api_error(self, error: Exception, context: str = "", user_id: str = "") -> HTTPException:
        """Handle API errors and return appropriate HTTP exceptions"""
        error_id = self.log_error(error, context, user_id)
        
        # Determine appropriate HTTP status code
        if isinstance(error, ValueError):
            status_code = 400
        elif isinstance(error, FileNotFoundError):
            status_code = 404
        elif isinstance(error, PermissionError):
            status_code = 403
        else:
            status_code = 500
        
        return HTTPException(
            status_code=status_code,
            detail={
                "error_id": error_id,
                "message": "An error occurred while processing your request",
                "details": str(error) if status_code == 400 else "Internal server error",
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def safe_execute(self, func, *args, fallback_result=None, context="", **kwargs):
        """Safely execute a function with error handling"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_id = self.log_error(e, context)
            if fallback_result is not None:
                if isinstance(fallback_result, dict):
                    fallback_result["error_id"] = error_id
                    fallback_result["fallback"] = True
                return fallback_result
            raise e

# Global error handler instance
error_handler = ErrorHandler()

# Decorator for error handling
def handle_errors(operation: str = "", fallback_result: Dict[str, Any] = None):
    """Decorator for automatic error handling"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_id = error_handler.log_error(e, operation)
                if fallback_result:
                    result = fallback_result.copy()
                    result["error_id"] = error_id
                    result["fallback"] = True
                    return result
                raise error_handler.handle_api_error(e, operation)
        return wrapper
    return decorator
