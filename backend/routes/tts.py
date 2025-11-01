# routes/tts.py - Text-to-Speech endpoint using gTTS
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from gtts import gTTS
import tempfile
import base64
import os
import logging
from typing import Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class TTSRequest(BaseModel):
    text: str
    language: str = "en"
    slow: bool = False

class TTSResponse(BaseModel):
    audio_base64: str
    text: str
    language: str
    success: bool

@router.post("/tts", response_model=TTSResponse)
async def text_to_speech(request: TTSRequest):
    """Convert text to speech using gTTS and return base64 encoded audio"""
    
    if not request.text or not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty"
        )
    
    try:
        logger.info(f"Converting text to speech: {request.text[:50]}...")
        
        # Create gTTS object
        tts = gTTS(
            text=request.text,
            lang=request.language,
            slow=request.slow
        )
        
        # Create temporary file for audio output
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        # Save TTS to temporary file
        tts.save(tmp_path)
        
        # Read the audio file and encode as base64
        with open(tmp_path, "rb") as audio_file:
            audio_content = audio_file.read()
            audio_base64 = base64.b64encode(audio_content).decode("utf-8")
        
        # Clean up temporary file
        os.unlink(tmp_path)
        
        logger.info("Text-to-speech conversion completed successfully")
        
        return TTSResponse(
            audio_base64=audio_base64,
            text=request.text,
            language=request.language,
            success=True
        )
        
    except Exception as e:
        logger.error(f"Error during text-to-speech conversion: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to convert text to speech: {str(e)}"
        )

@router.post("/tts/stream")
async def text_to_speech_stream(request: TTSRequest):
    """Convert text to speech and return audio data for streaming"""
    
    if not request.text or not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty"
        )
    
    try:
        logger.info(f"Converting text to speech (streaming): {request.text[:50]}...")
        
        # Create gTTS object
        tts = gTTS(
            text=request.text,
            lang=request.language,
            slow=request.slow
        )
        
        # Create temporary file for audio output
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        # Save TTS to temporary file
        tts.save(tmp_path)
        
        # Return file path for streaming (note: in production, you'd want to stream the file content)
        return {
            "audio_file_path": tmp_path,
            "text": request.text,
            "language": request.language,
            "success": True,
            "note": "In production, implement proper file streaming"
        }
        
    except Exception as e:
        logger.error(f"Error during text-to-speech conversion: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to convert text to speech: {str(e)}"
        )

@router.get("/tts/health")
def tts_health_check():
    """Health check for TTS service"""
    try:
        # Test gTTS with a simple phrase
        test_tts = gTTS("Health check", lang="en")
        return {
            "service": "Text-to-Speech",
            "gtts_available": True,
            "status": "healthy"
        }
    except Exception as e:
        return {
            "service": "Text-to-Speech",
            "gtts_available": False,
            "status": "unhealthy",
            "error": str(e)
        }

@router.get("/tts/languages")
def get_supported_languages():
    """Get list of supported languages for TTS"""
    # Common gTTS supported languages
    languages = {
        "en": "English",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "ru": "Russian",
        "ja": "Japanese",
        "ko": "Korean",
        "zh": "Chinese",
        "hi": "Hindi",
        "ar": "Arabic"
    }
    
    return {
        "supported_languages": languages,
        "default": "en"
    }
