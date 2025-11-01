"""
Application Configuration and Setup Module
Handles app initialization, middleware setup, and configuration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="AI NinjaCoach API", 
        description="API for AI NinjaCoach platform",
        version="1.0.0"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure as needed for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app

def setup_socketio() -> socketio.AsyncServer:
    """Create and configure Socket.io server"""
    sio = socketio.AsyncServer(
        cors_allowed_origins="*",
        async_mode='asgi',
        logger=True,
        engineio_logger=True
    )
    
    return sio

def register_routes(app: FastAPI):
    """Register all application routes"""
    try:
        # Direct imports to avoid module resolution issues
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from routes.analysis_routes import router as analysis_router
        from routes.performance_routes import router as performance_router
        from routes.session_routes import router as session_router
        from routes.orchestrator_routes import router as orchestrator_router
        
        # Register route modules
        app.include_router(analysis_router, prefix="/analyze", tags=["analysis"])
        app.include_router(performance_router, prefix="/performance", tags=["performance"])
        app.include_router(session_router, prefix="/track", tags=["session"])
        app.include_router(orchestrator_router, prefix="/orchestrate", tags=["orchestrator"])
        
        print("Core routes registered successfully")
    except Exception as e:
        print(f"Warning: Could not register core routes: {e}")
        print(f"Error details: {type(e).__name__}")
    
    # Add health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "service": "AI NinjaCoach API",
            "timestamp": "2024-12-08T12:00:00Z",
            "modular": True
        }
