# utils/ollama_client.py - Ollama integration for local LLM
import requests
import logging
import json
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OllamaConfig:
    """Configuration for Ollama client"""
    def __init__(self, 
                 base_url: str = "http://localhost:11434",
                 model: str = "mistral",
                 timeout: int = 60):
        self.base_url = base_url
        self.model = model
        self.timeout = timeout

class OllamaResponse(BaseModel):
    """Response model for Ollama API"""
    text: str
    success: bool
    model: str
    error: Optional[str] = None

class OllamaClient:
    """Client for interacting with local Ollama instance"""
    
    def __init__(self, config: OllamaConfig = None):
        self.config = config or OllamaConfig()
        self.base_url = self.config.base_url
        self.model = self.config.model
        self.timeout = self.config.timeout
    
    def health_check(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False
    
    def list_models(self) -> List[str]:
        """List available models in Ollama"""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
            return []
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []
    
    def generate(self, 
                prompt: str, 
                model: str = None,
                system_prompt: str = None,
                temperature: float = 0.7,
                max_tokens: int = 1000) -> OllamaResponse:
        """Generate text using Ollama"""
        
        model_name = model or self.model
        
        try:
            # Prepare the request payload
            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            # Add system prompt if provided
            if system_prompt:
                payload["system"] = system_prompt
            
            logger.info(f"Querying Ollama with model: {model_name}")
            
            # Make request to Ollama
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                generated_text = data.get("response", "").strip()
                
                logger.info(f"Ollama response received, length: {len(generated_text)}")
                
                return OllamaResponse(
                    text=generated_text,
                    success=True,
                    model=model_name
                )
            else:
                error_msg = f"Ollama API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return OllamaResponse(
                    text="",
                    success=False,
                    model=model_name,
                    error=error_msg
                )
                
        except requests.exceptions.Timeout:
            error_msg = f"Ollama request timeout after {self.timeout} seconds"
            logger.error(error_msg)
            return OllamaResponse(
                text="",
                success=False,
                model=model_name,
                error=error_msg
            )
        except Exception as e:
            error_msg = f"Ollama client error: {str(e)}"
            logger.error(error_msg)
            return OllamaResponse(
                text="",
                success=False,
                model=model_name,
                error=error_msg
            )
    
    def chat(self, 
             messages: List[Dict[str, str]], 
             model: str = None,
             temperature: float = 0.7) -> OllamaResponse:
        """Chat with Ollama using conversation format"""
        
        model_name = model or self.model
        
        try:
            payload = {
                "model": model_name,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature
                }
            }
            
            logger.info(f"Chat request to Ollama with {len(messages)} messages")
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", {})
                generated_text = message.get("content", "").strip()
                
                logger.info(f"Ollama chat response received, length: {len(generated_text)}")
                
                return OllamaResponse(
                    text=generated_text,
                    success=True,
                    model=model_name
                )
            else:
                error_msg = f"Ollama chat API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return OllamaResponse(
                    text="",
                    success=False,
                    model=model_name,
                    error=error_msg
                )
                
        except Exception as e:
            error_msg = f"Ollama chat error: {str(e)}"
            logger.error(error_msg)
            return OllamaResponse(
                text="",
                success=False,
                model=model_name,
                error=error_msg
            )

# Global Ollama client instance
ollama_client = OllamaClient()

# Convenience functions for backward compatibility
def query_ollama(prompt: str, 
                model: str = None, 
                system_prompt: str = None,
                temperature: float = 0.7) -> str:
    """Simple function to query Ollama and return text"""
    response = ollama_client.generate(
        prompt=prompt,
        model=model,
        system_prompt=system_prompt,
        temperature=temperature
    )
    
    if response.success:
        return response.text
    else:
        logger.error(f"Ollama query failed: {response.error}")
        return f"Error: {response.error or 'Failed to generate response'}"

def check_ollama_health() -> bool:
    """Check if Ollama is available"""
    return ollama_client.health_check()

def get_available_models() -> List[str]:
    """Get list of available Ollama models"""
    return ollama_client.list_models()
