"""
Base TTS Engine Abstract Class
Defines the interface for all TTS engines in FastTTS
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
import asyncio


class BaseTTSEngine(ABC):
    """Abstract base class for TTS engines"""
    
    def __init__(self, name: str):
        self.name = name
        self.supported_voices = []
        self.default_voice = None
    
    @abstractmethod
    async def generate_speech(
        self, 
        text: str, 
        voice: str = None, 
        speed: float = 1.0,
        **kwargs
    ) -> Tuple[bytes, List[Dict[str, Any]]]:
        """
        Generate speech from text and return audio bytes with timing data
        
        Args:
            text: Text to convert to speech
            voice: Voice ID to use (engine-specific)
            speed: Speech speed multiplier (1.0 = normal)
            **kwargs: Additional engine-specific parameters
            
        Returns:
            Tuple of (audio_bytes, timing_data)
            timing_data: List of dicts with 'word', 'start_time', 'end_time'
        """
        pass
    
    @abstractmethod
    def get_supported_voices(self) -> List[Dict[str, str]]:
        """
        Get list of supported voices for this engine
        
        Returns:
            List of dicts with 'id', 'name', 'language' keys
        """
        pass
    
    @abstractmethod
    def validate_voice(self, voice_id: str) -> bool:
        """
        Validate if a voice ID is supported by this engine
        
        Args:
            voice_id: Voice ID to validate
            
        Returns:
            True if voice is supported, False otherwise
        """
        pass
    
    def get_default_voice(self) -> str:
        """Get the default voice for this engine"""
        return self.default_voice
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text for TTS processing
        Override in subclasses for engine-specific cleaning
        
        Args:
            text: Raw input text
            
        Returns:
            Cleaned text ready for TTS processing
        """
        if not text:
            return ""
        return text.strip()