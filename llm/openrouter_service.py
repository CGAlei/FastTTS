import os
import json
import requests
from typing import Dict, Any
from pathlib import Path
import traceback
from .llm_provider import LLMProvider


class OpenRouterService(LLMProvider):
    """
    Service for interacting with OpenRouter API to get definitions and translations.
    """
    
    def __init__(self, api_key: str, config=None):
        """Initialize the OpenRouter client with API key"""
        self._api_key = api_key
        self._model = "gpt-4o-mini"  # Default model
        self._base_url = "https://openrouter.ai/api/v1"
        self._available = False
        self._config = config
        
        # Note: TTS service handled separately in main application
        
        # Verify API key and connection
        try:
            self._verify_connection()
            self._available = True
        except Exception as e:
            print(f"Error validating OpenRouter API key: {e}")
            raise
    
    def _verify_connection(self):
        """Verify the API key and connection to OpenRouter"""
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "HTTP-Referer": "https://github.com/yourusername/your-repo",  # Replace with your repo
            "X-Title": "Chinese Vocabulary Meaning"
        }
        
        response = requests.get(
            f"{self._base_url}/models",
            headers=headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to connect to OpenRouter: {response.text}")
    
    def get_definition(self, word: str) -> Dict[str, str]:
        """
        Get definition, pronunciation, and Spanish translation for a Chinese word
        
        Args:
            word (str): Chinese word to define
            
        Returns:
            dict: Definition data with spanish_meaning, pinyin, chinese_meaning, word_type and other fields
        """
        if not self.is_available:
            raise Exception("OpenRouter service is not available")
            
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "HTTP-Referer": "https://github.com/yourusername/your-repo",  # Replace with your repo
            "X-Title": "Chinese Vocabulary Indexer"
        }
        
        # Create the same function calling format as OpenAI
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant specialized in Chinese language."},
                {"role": "user", "content": f"Please provide information about the Chinese word: {word}"}
            ],
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "get_word_information",
                        "description": "Get information about a Chinese word",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "spanish_meaning": {
                                    "type": "string",
                                    "description": "The Spanish translation/meaning of the word"
                                },
                                "pinyin": {
                                    "type": "string",
                                    "description": "The Pinyin pronunciation of the word"
                                },
                                "chinese_meaning": {
                                    "type": "string",
                                    "description": "The definition of the word in Chinese simplified"
                                },
                                "word_type": {
                                    "type": "string",
                                    "description": "The grammatical type of the word (e.g., noun, verb, adjective, etc.)"
                                },
                                "synonyms": {
                                    "type": "string", 
                                    "description": "Synonyms of the word in Chinese (comma separated)"
                                },
                                "antonyms": {
                                    "type": "string",
                                    "description": "Antonyms of the word in Chinese (comma separated)"
                                },
                                "usage_example": {
                                    "type": "string",
                                    "description": "An example sentence using the word in Chinese"
                                }
                            },
                            "required": ["spanish_meaning", "pinyin", "chinese_meaning"]
                        }
                    }
                }
            ],
            "tool_choice": {"type": "function", "function": {"name": "get_word_information"}}
        }
        
        try:
            response = requests.post(
                f"{self._base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenRouter API error: {response.text}")
                
            result = response.json()
            
            # Extract the function call result
            tool_calls = result["choices"][0]["message"].get("tool_calls", [])
            if not tool_calls:
                raise Exception("No tool calls in response")
                
            function_args = json.loads(tool_calls[0]["function"]["arguments"])
            
            # Note: TTS generation handled separately in main application
            
            return function_args
            
        except Exception as e:
            print(f"Error getting definition from OpenRouter: {e}")
            raise
    
    
    @property
    def provider_name(self) -> str:
        """Return the name of the provider"""
        return "OpenRouter"
    
    @property
    def model_name(self) -> str:
        """Return the current model name"""
        return self._model
    
    @property
    def is_available(self) -> bool:
        """Check if the provider is available and properly configured"""
        return self._available 