# routes/test_ollama.py - Test routes for Ollama service
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.ollama_service import generate_response, is_ollama_ready, ollama_service
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/test", tags=["Testing"])

class TestPromptRequest(BaseModel):
    prompt: str
    model: Optional[str] = None

class TestPromptResponse(BaseModel):
    prompt: str
    response: str
    model: str
    success: bool

@router.get("/ollama/health")
async def test_ollama_health():
    """Test if Ollama service is healthy"""
    is_ready = is_ollama_ready()
    models = ollama_service.list_models()
    
    return {
        "ollama_available": is_ready,
        "available_models": models,
        "default_model": ollama_service.default_model,
        "status": "healthy" if is_ready else "unhealthy"
    }

@router.post("/ollama/generate", response_model=TestPromptResponse)
async def test_ollama_generate(request: TestPromptRequest):
    """Test text generation with Ollama"""
    
    if not is_ollama_ready():
        raise HTTPException(
            status_code=503,
            detail="Ollama service is not available"
        )
    
    try:
        response = generate_response(request.prompt, request.model)
        
        if not response:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate response"
            )
        
        return TestPromptResponse(
            prompt=request.prompt,
            response=response,
            model=request.model or ollama_service.default_model,
            success=True
        )
        
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Generation failed: {str(e)}"
        )

@router.post("/quick-chat")
async def quick_chat(message: dict):
    """Quick chat test endpoint"""
    user_message = message.get("message", "Hello!")
    
    if not is_ollama_ready():
        return {
            "response": "AI service is currently unavailable. Please try again later.",
            "success": False
        }
    
    try:
        prompt = f"You are a helpful AI assistant. Respond briefly and friendly to: {user_message}"
        response = generate_response(prompt)
        
        return {
            "user_message": user_message,
            "response": response or "Sorry, I couldn't generate a response.",
            "success": response is not None
        }
        
    except Exception as e:
        return {
            "response": f"Error: {str(e)}",
            "success": False
        }
