"""
TTS Factory
Creates and manages TTS engine instances for FastTTS application
"""

from typing import Optional, Dict, Any
from .base_tts import BaseTTSEngine
from .edge_tts_engine import EdgeTTSEngine
from .minimax_tts_engine import MinimaxTTSEngine


class TTSFactory:
    """Factory class for creating TTS engine instances"""
    
    _engines = {
        "edge": EdgeTTSEngine,
        "hailuo": MinimaxTTSEngine,
        "minimax": MinimaxTTSEngine  # Alias for compatibility
    }
    
    _instances = {}
    
    @classmethod
    def create_engine(cls, engine_type: str) -> BaseTTSEngine:
        """
        Create a TTS engine instance
        
        Args:
            engine_type: Type of engine ("edge", "hailuo", "minimax")
            
        Returns:
            TTS engine instance
            
        Raises:
            ValueError: If engine type is not supported
        """
        engine_type = engine_type.lower()
        
        if engine_type not in cls._engines:
            supported = ", ".join(cls._engines.keys())
            raise ValueError(f"Unsupported TTS engine: {engine_type}. Supported engines: {supported}")
        
        # Use singleton pattern for engine instances
        if engine_type not in cls._instances:
            cls._instances[engine_type] = cls._engines[engine_type]()
        
        return cls._instances[engine_type]
    
    @classmethod
    def get_supported_engines(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all supported TTS engines
        
        Returns:
            Dictionary with engine info
        """
        engines_info = {}
        
        for engine_type, engine_class in cls._engines.items():
            # Skip aliases
            if engine_type == "minimax":
                continue
                
            try:
                engine = cls.create_engine(engine_type)
                engines_info[engine_type] = {
                    "name": engine.name,
                    "voices": engine.get_supported_voices(),
                    "default_voice": engine.get_default_voice(),
                    "available": True
                }
                
                # Check if engine is properly configured
                if hasattr(engine, 'is_configured'):
                    engines_info[engine_type]["configured"] = engine.is_configured()
                else:
                    engines_info[engine_type]["configured"] = True
                    
            except Exception as e:
                engines_info[engine_type] = {
                    "name": engine_class.__name__,
                    "voices": [],
                    "default_voice": None,
                    "available": False,
                    "configured": False,
                    "error": str(e)
                }
        
        return engines_info
    
    @classmethod
    def get_default_engine(cls) -> str:
        """Get the default TTS engine type"""
        return "edge"
    
    @classmethod
    def validate_engine_config(cls, engine_type: str) -> Dict[str, Any]:
        """
        Validate engine configuration
        
        Args:
            engine_type: Engine type to validate
            
        Returns:
            Validation result dictionary
        """
        try:
            engine = cls.create_engine(engine_type)
            
            result = {
                "valid": True,
                "engine": engine.name,
                "voices_count": len(engine.get_supported_voices()),
                "default_voice": engine.get_default_voice()
            }
            
            # Check configuration for engines that need it
            if hasattr(engine, 'is_configured'):
                result["configured"] = engine.is_configured()
                if not result["configured"]:
                    result["valid"] = False
                    result["error"] = "Engine not properly configured"
            
            return result
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }