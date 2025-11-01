# routes/stt.py - Speech-to-Text endpoint using Whisper
from fastapi import APIRouter, UploadFile, File, HTTPException
import whisper
import tempfile
import os
import logging
from typing import Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Global Whisper model - load once on startup
model: Optional[whisper.Whisper] = None

def load_whisper_model(model_size: str = "base"):
    """Load Whisper model with error handling"""
    global model
    try:
        logger.info(f"Loading Whisper model: {model_size}")
        model = whisper.load_model(model_size)
        logger.info("Whisper model loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to load Whisper model: {e}")
        return False

# Try to load model on import
try:
    load_whisper_model("base")
except Exception as e:
    logger.warning(f"Whisper model not loaded on startup: {e}")

@router.post("/stt")
async def speech_to_text(file: UploadFile = File(...)):
    """Convert speech audio file to text using Whisper"""
    
    if model is None:
        # Try to load model if not already loaded
        if not load_whisper_model():
            raise HTTPException(
                status_code=500, 
                detail="Whisper model not available. Please ensure Whisper is installed."
            )
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload an audio file."
        )
    
    try:
        # Create temporary file for audio processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            # Write uploaded file content to temporary file
            content = await file.read()
            tmp.write(content)
            tmp.flush()
            
            # Transcribe audio using Whisper
            logger.info(f"Transcribing audio file: {file.filename}")
            result = model.transcribe(tmp.name)
            
            # Clean up temporary file
            os.unlink(tmp.name)
            
            # Extract text and confidence if available
            text = result.get("text", "").strip()
            language = result.get("language", "unknown")
            
            logger.info(f"Transcription completed. Language: {language}, Text length: {len(text)}")
            
            return {
                "text": text,
                "language": language,
                "confidence": result.get("avg_logprob", 0.0),
                "success": True
            }
            
    except Exception as e:
        logger.error(f"Error during transcription: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to transcribe audio: {str(e)}"
        )

@router.get("/stt/health")
def stt_health_check():
    """Health check for STT service"""
    return {
        "service": "Speech-to-Text",
        "whisper_loaded": model is not None,
        "status": "healthy" if model is not None else "model_not_loaded"
    }

@router.post("/stt/reload-model")
def reload_whisper_model(model_size: str = "base"):
    """Reload Whisper model with specified size"""
    try:
        success = load_whisper_model(model_size)
        return {
            "success": success,
            "model_size": model_size,
            "message": "Model reloaded successfully" if success else "Failed to reload model"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reload model: {str(e)}"
        )
