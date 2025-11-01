"""
Enhanced STT Solutions for AI NinjaCoach
Multiple options to replace weak browser SpeechRecognition API
"""

import asyncio
import aiohttp
import aiofiles
import tempfile
import os
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional, Dict, Any
import json

logger = logging.getLogger(__name__)
router = APIRouter()

# =============================================================================
# SOLUTION 1: Upgraded Whisper Models (Better Accuracy)
# =============================================================================

class WhisperSTTService:
    """Enhanced Whisper STT with better models and preprocessing"""
    
    def __init__(self):
        self.model = None
        self.model_size = "medium"  # Upgrade from "base" to "medium" for better accuracy
        
    async def load_model(self, model_size: str = "medium"):
        """Load larger Whisper model for better accuracy"""
        try:
            import whisper
            logger.info(f"Loading Whisper model: {model_size}")
            
            # Use larger models for better accuracy:
            # - tiny: fastest, lowest accuracy
            # - base: balanced (current)
            # - small: better accuracy, slightly slower
            # - medium: much better accuracy (recommended)
            # - large: best accuracy, slower
            
            self.model = whisper.load_model(model_size)
            self.model_size = model_size
            logger.info(f"Whisper {model_size} model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            return False
    
    async def transcribe_with_preprocessing(self, audio_file_path: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enhanced transcription with preprocessing and options"""
        if not self.model:
            await self.load_model()
        
        try:
            # Enhanced Whisper options for better accuracy
            transcribe_options = {
                "language": "en",  # Force English for consistency
                "task": "transcribe",
                "temperature": 0.0,  # More deterministic output
                "beam_size": 5,  # Better beam search
                "best_of": 5,  # Consider multiple candidates
                "patience": 1.0,  # Wait for better results
                "length_penalty": 1.0,
                "suppress_tokens": "-1",  # Don't suppress any tokens
                "initial_prompt": "This is a professional interview conversation.",  # Context hint
                "condition_on_previous_text": True,  # Use context
                "fp16": True,  # Use mixed precision for speed
                "compression_ratio_threshold": 2.4,
                "logprob_threshold": -1.0,
                "no_speech_threshold": 0.6
            }
            
            # Override with custom options if provided
            if options:
                transcribe_options.update(options)
            
            result = self.model.transcribe(audio_file_path, **transcribe_options)
            
            # Post-process result
            text = result.get("text", "").strip()
            
            # Calculate confidence based on average log probability
            segments = result.get("segments", [])
            confidence = 0.0
            if segments:
                log_probs = [seg.get("avg_logprob", -2.0) for seg in segments]
                avg_log_prob = sum(log_probs) / len(log_probs)
                # Convert log prob to confidence (0-1)
                confidence = max(0.0, min(1.0, (avg_log_prob + 2.0) / 2.0))
            
            return {
                "text": text,
                "language": result.get("language", "en"),
                "confidence": confidence,
                "segments": segments,
                "model_used": self.model_size,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return {
                "text": "",
                "error": str(e),
                "success": False
            }

# =============================================================================
# SOLUTION 2: OpenAI Whisper API (Cloud-based, Most Accurate)
# =============================================================================

class OpenAIWhisperService:
    """OpenAI Whisper API for highest accuracy STT"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.openai.com/v1"
    
    async def transcribe(self, audio_file_path: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Transcribe using OpenAI Whisper API"""
        if not self.api_key:
            return {
                "text": "",
                "error": "OpenAI API key not configured",
                "success": False
            }
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # Prepare form data
            async with aiofiles.open(audio_file_path, 'rb') as audio_file:
                audio_data = await audio_file.read()
            
            form_data = aiohttp.FormData()
            form_data.add_field('file', audio_data, filename='audio.wav', content_type='audio/wav')
            form_data.add_field('model', 'whisper-1')
            form_data.add_field('language', 'en')
            form_data.add_field('response_format', 'verbose_json')
            form_data.add_field('temperature', '0')
            
            # Add custom prompt for interview context
            if options and options.get("prompt"):
                form_data.add_field('prompt', options["prompt"])
            else:
                form_data.add_field('prompt', 'This is a professional job interview conversation.')
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/audio/transcriptions",
                    headers=headers,
                    data=form_data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        # Calculate confidence from segments
                        segments = result.get("segments", [])
                        confidence = 0.0
                        if segments:
                            # OpenAI provides confidence in segments
                            confidences = [seg.get("avg_logprob", -2.0) for seg in segments]
                            avg_confidence = sum(confidences) / len(confidences)
                            confidence = max(0.0, min(1.0, (avg_confidence + 2.0) / 2.0))
                        
                        return {
                            "text": result.get("text", "").strip(),
                            "language": result.get("language", "en"),
                            "confidence": confidence,
                            "segments": segments,
                            "model_used": "whisper-1-api",
                            "success": True
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "text": "",
                            "error": f"OpenAI API error: {response.status} - {error_text}",
                            "success": False
                        }
        
        except Exception as e:
            logger.error(f"OpenAI Whisper API failed: {e}")
            return {
                "text": "",
                "error": str(e),
                "success": False
            }

# =============================================================================
# SOLUTION 3: Google Speech-to-Text (High Accuracy, Good for Conversations)
# =============================================================================

class GoogleSTTService:
    """Google Cloud Speech-to-Text for high accuracy"""
    
    def __init__(self, credentials_path: str = None):
        self.credentials_path = credentials_path
        self.client = None
    
    async def initialize(self):
        """Initialize Google STT client"""
        try:
            from google.cloud import speech
            import google.auth
            
            if self.credentials_path:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.credentials_path
            
            self.client = speech.SpeechClient()
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Google STT: {e}")
            return False
    
    async def transcribe(self, audio_file_path: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Transcribe using Google Speech-to-Text"""
        if not self.client and not await self.initialize():
            return {
                "text": "",
                "error": "Google STT client not initialized",
                "success": False
            }
        
        try:
            from google.cloud import speech
            
            # Read audio file
            async with aiofiles.open(audio_file_path, 'rb') as audio_file:
                audio_data = await audio_file.read()
            
            # Configure recognition
            audio = speech.RecognitionAudio(content=audio_data)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code="en-US",
                model="latest_long",  # Best model for conversations
                use_enhanced=True,  # Enhanced model for better accuracy
                enable_automatic_punctuation=True,
                enable_word_confidence=True,
                enable_word_time_offsets=True,
                speech_contexts=[
                    speech.SpeechContext(
                        phrases=[
                            "software engineer", "data scientist", "machine learning",
                            "Python", "JavaScript", "React", "FastAPI", "interview",
                            "experience", "project", "team", "development"
                        ],
                        boost=20.0  # Boost technical terms
                    )
                ]
            )
            
            # Perform transcription
            response = self.client.recognize(config=config, audio=audio)
            
            if response.results:
                # Get best result
                result = response.results[0]
                alternative = result.alternatives[0]
                
                # Calculate average confidence
                word_confidences = [word.confidence for word in alternative.words if hasattr(word, 'confidence')]
                avg_confidence = sum(word_confidences) / len(word_confidences) if word_confidences else 0.0
                
                return {
                    "text": alternative.transcript.strip(),
                    "language": "en",
                    "confidence": avg_confidence,
                    "words": [
                        {
                            "word": word.word,
                            "confidence": getattr(word, 'confidence', 0.0),
                            "start_time": word.start_time.total_seconds(),
                            "end_time": word.end_time.total_seconds()
                        }
                        for word in alternative.words
                    ],
                    "model_used": "google-latest-long",
                    "success": True
                }
            else:
                return {
                    "text": "",
                    "error": "No speech detected",
                    "success": False
                }
        
        except Exception as e:
            logger.error(f"Google STT failed: {e}")
            return {
                "text": "",
                "error": str(e),
                "success": False
            }

# =============================================================================
# SOLUTION 4: Azure Speech Services (Excellent for Real-time)
# =============================================================================

class AzureSTTService:
    """Azure Speech Services for real-time STT"""
    
    def __init__(self, subscription_key: str = None, region: str = "eastus"):
        self.subscription_key = subscription_key or os.getenv("AZURE_SPEECH_KEY")
        self.region = region
        self.endpoint = f"https://{region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"
    
    async def transcribe(self, audio_file_path: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Transcribe using Azure Speech Services"""
        if not self.subscription_key:
            return {
                "text": "",
                "error": "Azure Speech subscription key not configured",
                "success": False
            }
        
        try:
            headers = {
                "Ocp-Apim-Subscription-Key": self.subscription_key,
                "Content-Type": "audio/wav; codecs=audio/pcm; samplerate=16000",
                "Accept": "application/json"
            }
            
            params = {
                "language": "en-US",
                "format": "detailed",
                "profanity": "masked"
            }
            
            # Read audio file
            async with aiofiles.open(audio_file_path, 'rb') as audio_file:
                audio_data = await audio_file.read()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.endpoint,
                    headers=headers,
                    params=params,
                    data=audio_data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        if result.get("RecognitionStatus") == "Success":
                            display_text = result.get("DisplayText", "").strip()
                            confidence = result.get("Confidence", 0.0)
                            
                            return {
                                "text": display_text,
                                "language": "en",
                                "confidence": confidence,
                                "offset": result.get("Offset", 0),
                                "duration": result.get("Duration", 0),
                                "model_used": "azure-conversation",
                                "success": True
                            }
                        else:
                            return {
                                "text": "",
                                "error": f"Azure recognition failed: {result.get('RecognitionStatus')}",
                                "success": False
                            }
                    else:
                        error_text = await response.text()
                        return {
                            "text": "",
                            "error": f"Azure API error: {response.status} - {error_text}",
                            "success": False
                        }
        
        except Exception as e:
            logger.error(f"Azure STT failed: {e}")
            return {
                "text": "",
                "error": str(e),
                "success": False
            }

# =============================================================================
# UNIFIED STT SERVICE (Try multiple providers with fallback)
# =============================================================================

class UnifiedSTTService:
    """Unified STT service that tries multiple providers for best results"""
    
    def __init__(self):
        self.whisper_service = WhisperSTTService()
        self.openai_service = OpenAIWhisperService()
        self.google_service = GoogleSTTService()
        self.azure_service = AzureSTTService()
        
        # Priority order: OpenAI > Google > Azure > Local Whisper
        self.services = [
            ("openai", self.openai_service),
            ("google", self.google_service),
            ("azure", self.azure_service),
            ("whisper", self.whisper_service)
        ]
    
    async def transcribe(self, audio_file_path: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Try multiple STT services until one succeeds"""
        
        results = []
        
        for service_name, service in self.services:
            try:
                logger.info(f"Trying STT service: {service_name}")
                result = await service.transcribe(audio_file_path, options)
                
                results.append({
                    "service": service_name,
                    "result": result
                })
                
                # If successful and confidence is good, use this result
                if result.get("success") and result.get("confidence", 0) > 0.7:
                    logger.info(f"STT success with {service_name}: confidence {result.get('confidence')}")
                    result["service_used"] = service_name
                    result["all_attempts"] = results
                    return result
                
                # If text is non-empty (even if confidence is low), keep as backup
                if result.get("success") and result.get("text", "").strip():
                    logger.info(f"STT partial success with {service_name}")
                    # Continue trying other services but keep this as backup
                
            except Exception as e:
                logger.error(f"STT service {service_name} failed: {e}")
                results.append({
                    "service": service_name,
                    "error": str(e)
                })
        
        # If no high-confidence result, return the best available result
        best_result = None
        best_confidence = 0.0
        
        for attempt in results:
            result = attempt.get("result", {})
            if result.get("success") and result.get("text", "").strip():
                confidence = result.get("confidence", 0.0)
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_result = result
                    best_result["service_used"] = attempt["service"]
        
        if best_result:
            best_result["all_attempts"] = results
            logger.info(f"Using best available STT result: confidence {best_confidence}")
            return best_result
        
        # All services failed
        return {
            "text": "",
            "error": "All STT services failed",
            "success": False,
            "all_attempts": results
        }

# Initialize unified service
unified_stt = UnifiedSTTService()

# =============================================================================
# ENHANCED STT ENDPOINTS
# =============================================================================

@router.post("/stt/enhanced")
async def enhanced_speech_to_text(file: UploadFile = File(...), service: str = "auto"):
    """Enhanced STT with multiple provider options"""
    
    # Validate file
    if not file.content_type or not file.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload an audio file."
        )
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp.flush()
            
            # Choose service
            if service == "auto":
                result = await unified_stt.transcribe(tmp.name)
            elif service == "openai":
                result = await unified_stt.openai_service.transcribe(tmp.name)
            elif service == "google":
                result = await unified_stt.google_service.transcribe(tmp.name)
            elif service == "azure":
                result = await unified_stt.azure_service.transcribe(tmp.name)
            elif service == "whisper":
                result = await unified_stt.whisper_service.transcribe_with_preprocessing(tmp.name)
            else:
                raise HTTPException(status_code=400, detail=f"Unknown service: {service}")
            
            # Clean up
            os.unlink(tmp.name)
            
            return result
    
    except Exception as e:
        logger.error(f"Enhanced STT failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"STT processing failed: {str(e)}"
        )

@router.get("/stt/services")
def list_stt_services():
    """List available STT services and their status"""
    return {
        "services": {
            "whisper": {
                "available": True,
                "description": "Local Whisper model (medium size for better accuracy)",
                "accuracy": "Good",
                "speed": "Fast",
                "cost": "Free"
            },
            "openai": {
                "available": bool(os.getenv("OPENAI_API_KEY")),
                "description": "OpenAI Whisper API (highest accuracy)",
                "accuracy": "Excellent",
                "speed": "Medium",
                "cost": "Paid"
            },
            "google": {
                "available": bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS")),
                "description": "Google Cloud Speech-to-Text",
                "accuracy": "Excellent",
                "speed": "Fast",
                "cost": "Paid"
            },
            "azure": {
                "available": bool(os.getenv("AZURE_SPEECH_KEY")),
                "description": "Azure Speech Services",
                "accuracy": "Very Good",
                "speed": "Very Fast",
                "cost": "Paid"
            }
        },
        "recommended": "auto (tries multiple services for best result)"
    }
