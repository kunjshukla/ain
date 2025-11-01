# File: backend/services/ollama_service.py
# Minimal Ollama client that sends a prompt to llama3.3 model at localhost:11434 and returns JSON response with error handling

import requests
import json
from typing import Dict, Optional, List
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OllamaService:
    """
    Minimal Ollama client for local LLM inference
    Supports llama3.3 and other models running on localhost:11434
    """
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.default_model = "llama3:latest"  # Use available model
        
        # Try to find the best available model
        self._set_best_model()
    
    def generate(self, prompt: str, model: str = None) -> Optional[Dict]:
        """
        Generate response from Ollama model
        
        Args:
            prompt: Text prompt to send to the model
            model: Model name (defaults to llama3.3)
            
        Returns:
            Dict with response or None if error
        """
        if model is None:
            model = self.default_model
            
        try:
            logger.info(f"Sending prompt to {model}: {prompt[:50]}...")
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False  # Get complete response
                },
                timeout=60  # Increased timeout for local models
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Generated response: {result.get('response', '')[:50]}...")
            
            return result
            
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to Ollama at {self.base_url}")
            return None
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama request error: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from Ollama: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected Ollama error: {e}")
            return None
    
    def is_available(self) -> bool:
        """
        Check if Ollama service is available
        
        Returns:
            True if Ollama is running and accessible
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def list_models(self) -> List[str]:
        """
        Get list of available models
        
        Returns:
            List of model names
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            models = [model["name"] for model in data.get("models", [])]
            
            logger.info(f"Available models: {models}")
            return models
            
        except Exception as e:
            logger.error(f"Error fetching models: {e}")
            return []
    
    def model_exists(self, model: str) -> bool:
        """
        Check if a specific model exists
        
        Args:
            model: Model name to check
            
        Returns:
            True if model exists
        """
        available_models = self.list_models()
        return any(model in available_model for available_model in available_models)
    
    def _set_best_model(self):
        """
        Automatically detect and set the best available model
        Priority: llama3.3 > llama3:latest > mistral:latest > first available
        """
        try:
            models = self.list_models()
            if not models:
                return
                
            # Preferred models in order (mistral first for speed)
            preferred = ["mistral:latest", "llama3:latest", "llama3.3"]
            
            for preferred_model in preferred:
                if any(preferred_model in model for model in models):
                    self.default_model = preferred_model
                    logger.info(f"Using model: {self.default_model}")
                    return
            
            # Use first available model as fallback
            if models:
                self.default_model = models[0]
                logger.info(f"Using fallback model: {self.default_model}")
                
        except Exception as e:
            logger.warning(f"Could not detect best model: {e}")

# Global instance for easy import
ollama_service = OllamaService()

# Convenience functions
def generate_response(prompt: str, model: str = None) -> Optional[str]:
    """
    Simple function to generate a text response
    
    Args:
        prompt: Text prompt
        model: Model name (defaults to auto-detected best model)
        
    Returns:
        Generated text or None if error
    """
    if model is None:
        model = ollama_service.default_model
        
    result = ollama_service.generate(prompt, model)
    if result:
        return result.get("response")
    return None

def is_ollama_ready() -> bool:
    """
    Check if Ollama is ready for use
    
    Returns:
        True if Ollama is available and has models
    """
    if not ollama_service.is_available():
        return False
    
    models = ollama_service.list_models()
    return len(models) > 0

# Test function
def test_ollama():
    """Test the Ollama service"""
    print("🧪 Testing Ollama Service...")
    
    # Check availability
    if not ollama_service.is_available():
        print("❌ Ollama is not available at localhost:11434")
        return False
    
    print("✅ Ollama is available")
    
    # List models
    models = ollama_service.list_models()
    if not models:
        print("❌ No models available")
        return False
    
    print(f"✅ Available models: {models}")
    
    # Test generation
    test_prompt = "Say hello in a friendly way."
    response = generate_response(test_prompt)
    
    if response:
        print(f"✅ Test generation successful: {response[:100]}...")
        return True
    else:
        print("❌ Test generation failed")
        return False

if __name__ == "__main__":
    test_ollama()
