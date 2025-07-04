"""
Centralized LLM Service Manager for Word Definition Generation
Provides fallback logic: OpenRouter (primary) → OpenAI (fallback)
"""

import os
import logging
from typing import Dict, Optional
from dotenv import load_dotenv

from llm.openrouter_service import OpenRouterService
from llm.openai_service import OpenAIService

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class LLMManager:
    """
    Centralized manager for LLM services with automatic fallback.
    Handles API key validation, service initialization, and error recovery.
    """
    
    def __init__(self):
        """Initialize both OpenRouter and OpenAI services with error handling"""
        self.primary_service = None
        self.fallback_service = None
        self._init_services()
    
    def _init_services(self):
        """Initialize LLM services with proper error handling"""
        # Initialize OpenRouter as primary service
        openrouter_key = os.getenv('OPENROUTER_API_KEY')
        if openrouter_key and openrouter_key != 'your_openrouter_api_key_here':
            try:
                self.primary_service = OpenRouterService(openrouter_key)
                logger.info("OpenRouter service initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenRouter service: {e}")
                self.primary_service = None
        else:
            logger.info("OpenRouter API key not configured, skipping OpenRouter service")
        
        # Initialize OpenAI as fallback service
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key and openai_key != 'your_openai_api_key_here':
            try:
                self.fallback_service = OpenAIService(openai_key)
                logger.info("OpenAI service initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI service: {e}")
                self.fallback_service = None
        else:
            logger.info("OpenAI API key not configured, skipping OpenAI service")
    
    def is_available(self) -> bool:
        """Check if at least one LLM service is available"""
        return (self.primary_service and self.primary_service.is_available) or \
               (self.fallback_service and self.fallback_service.is_available)
    
    def get_word_definition(self, word: str) -> Dict[str, str]:
        """
        Get comprehensive word definition using available LLM services
        
        Args:
            word (str): Chinese word to define
            
        Returns:
            dict: Structured word definition data
            
        Raises:
            Exception: If both services fail or no services available
        """
        if not word or not word.strip():
            raise ValueError("Word cannot be empty")
        
        word = word.strip()
        
        # Try primary service (OpenRouter) first
        if self.primary_service and self.primary_service.is_available:
            try:
                logger.info(f"Attempting definition generation with OpenRouter for word: {word}")
                result = self.primary_service.get_definition(word)
                logger.info(f"OpenRouter successfully generated definition for: {word}")
                return result
            except Exception as e:
                logger.warning(f"OpenRouter failed for word '{word}': {e}")
        
        # Fallback to OpenAI service
        if self.fallback_service and self.fallback_service.is_available:
            try:
                logger.info(f"Attempting definition generation with OpenAI for word: {word}")
                result = self.fallback_service.get_definition(word)
                logger.info(f"OpenAI successfully generated definition for: {word}")
                return result
            except Exception as e:
                logger.error(f"OpenAI also failed for word '{word}': {e}")
        
        # Both services failed or unavailable
        raise Exception("All LLM services are unavailable or failed to generate definition")
    
    def get_service_status(self) -> Dict[str, any]:
        """Get status information about available services"""
        return {
            'primary_service': {
                'name': self.primary_service.provider_name if self.primary_service else None,
                'available': self.primary_service.is_available if self.primary_service else False,
                'model': self.primary_service.model_name if self.primary_service else None
            },
            'fallback_service': {
                'name': self.fallback_service.provider_name if self.fallback_service else None,
                'available': self.fallback_service.is_available if self.fallback_service else False,
                'model': self.fallback_service.model_name if self.fallback_service else None
            },
            'overall_available': self.is_available()
        }

def test_llm_manager():
    """Test function for development purposes"""
    try:
        manager = LLMManager()
        print("LLM Manager Status:")
        print(manager.get_service_status())
        
        if manager.is_available():
            # Test with a simple Chinese word
            test_word = "你好"
            print(f"\nTesting definition generation for: {test_word}")
            result = manager.get_word_definition(test_word)
            print("Success! Definition generated:")
            print(result)
        else:
            print("No LLM services available for testing")
            
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_llm_manager()