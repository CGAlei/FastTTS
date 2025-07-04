from abc import ABC, abstractmethod
from typing import Dict, Any

class LLMProvider(ABC):
    """
    Abstract base class for LLM providers (OpenAI, OpenRouter, etc.)
    Defines the common interface that all providers must implement.
    """
    
    @abstractmethod
    def __init__(self, api_key: str):
        """Initialize the provider with API key"""
        pass
    
    @abstractmethod
    def get_definition(self, word: str) -> Dict[str, str]:
        """
        Get definition, pronunciation, and Spanish translation for a Chinese word
        
        Args:
            word (str): Chinese word to define
            
        Returns:
            dict: Definition data with spanish_meaning, pinyin, and definition
        """
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of the provider"""
        pass
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the current model name"""
        pass
    
    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and properly configured"""
        pass 