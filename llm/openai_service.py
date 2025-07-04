import os
import json
import traceback
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from .llm_provider import LLMProvider
from typing import Dict

# Load environment variables
load_dotenv()

class OpenAIService(LLMProvider):
    """
    Service for interacting with OpenAI API to get definitions and translations.
    """
    def __init__(self, api_key: str, config=None):
        """Initialize the OpenAI client with API key"""
        self._api_key = api_key
        self._model = "gpt-4o-mini"
        self._available = False
        self._config = config
        
        try:
            # Test the API key with a simple models list request
            client = OpenAI(api_key=api_key)
            client.models.list()  # This will fail if the API key is invalid
            
            self.client = client
            self._available = True
            
        except Exception as e:
            print(f"Error validating OpenAI API key: {e}")
            self._available = False
            raise

    def get_definition(self, word: str) -> Dict[str, str]:
        """
        Get definition, pronunciation, and Spanish translation for a Chinese word
        
        Args:
            word (str): Chinese word to define
            
        Returns:
            dict: Definition data with spanish_meaning, pinyin, chinese_meaning, word_type and other fields
        """
        if not self.is_available:
            raise Exception("OpenAI service is not available")
            
        try:
            # Create a structured response using OpenAI's function calling
            response = self.client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant specialized in Chinese language."},
                    {"role": "user", "content": f"Please provide information about the Chinese word: {word}"}
                ],
                tools=[
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
                tool_choice={"type": "function", "function": {"name": "get_word_information"}}
            )
            
            # Extract the function call result
            tool_calls = response.choices[0].message.tool_calls
            if not tool_calls:
                raise Exception("No tool calls in response")
                
            function_args = json.loads(tool_calls[0].function.arguments)
            
            # Note: TTS generation handled separately in main application
            
            return function_args
            
        except Exception as e:
            print(f"Error getting definition from OpenAI: {e}")
            raise
            
    @property
    def provider_name(self) -> str:
        """Return the name of the provider"""
        return "OpenAI"
    
    @property
    def model_name(self) -> str:
        """Return the current model name"""
        return self._model
    
    @property
    def is_available(self) -> bool:
        """Check if the provider is available and properly configured"""
        return self._available

    