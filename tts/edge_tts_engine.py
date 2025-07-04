"""
Microsoft Edge TTS Engine
Handles text-to-speech using Microsoft Edge TTS with word-level timing
"""

import edge_tts
import asyncio
import io
import re
from typing import List, Dict, Any, Tuple, Optional
from .base_tts import BaseTTSEngine


class EdgeTTSEngine(BaseTTSEngine):
    """Microsoft Edge TTS implementation"""
    
    def __init__(self):
        super().__init__("Edge TTS")
        self.default_voice = "zh-CN-XiaoxiaoNeural"
        self.supported_voices = [
            {"id": "zh-CN-XiaoxiaoNeural", "name": "Microsoft Xiaoxiao (Female)", "language": "zh-CN"},
            {"id": "zh-CN-XiaoyiNeural", "name": "Microsoft Xiaoyi (Female)", "language": "zh-CN"},
            {"id": "zh-CN-YunjianNeural", "name": "Microsoft Yunjian (Male)", "language": "zh-CN"},
            {"id": "zh-CN-YunxiNeural", "name": "Microsoft Yunxi (Male)", "language": "zh-CN"},
            {"id": "zh-CN-YunxiaNeural", "name": "Microsoft Yunxia (Female)", "language": "zh-CN"},
            {"id": "zh-CN-YunyangNeural", "name": "Microsoft Yunyang (Male)", "language": "zh-CN"},
            {"id": "zh-CN-liaoning-XiaobeiNeural", "name": "Microsoft Xiaobei (Female - Northeastern)", "language": "zh-CN"},
            {"id": "zh-CN-shaanxi-XiaoniNeural", "name": "Microsoft Xiaoni (Female - Shaanxi)", "language": "zh-CN"}
        ]
    
    async def generate_speech(
        self, 
        text: str, 
        voice: str = None, 
        speed: float = 1.0,
        volume: float = 0.8,
        **kwargs
    ) -> Tuple[bytes, List[Dict[str, Any]]]:
        """
        Generate speech using Edge TTS with word-level timing
        
        Args:
            text: Chinese text to convert to speech
            voice: Voice ID (defaults to class default)
            speed: Speech speed multiplier
            volume: Audio volume level (0.0-1.0)
            **kwargs: Additional parameters
            
        Returns:
            Tuple of (audio_bytes, word_timing_data)
        """
        if not voice:
            voice = self.default_voice
            
        if not self.validate_voice(voice):
            raise ValueError(f"Unsupported voice: {voice}")
        
        # Text is already preprocessed by centralized text_processor.py
        if not text:
            raise ValueError("No valid text to process")
        
        # Convert speed to Edge TTS rate format
        rate = self._convert_speed_to_rate(speed)
        
        # Convert volume to Edge TTS volume format
        volume_str = self._convert_volume_to_edge_format(volume)
        
        # Generate TTS with word boundaries
        communicate = edge_tts.Communicate(text, voice, rate=rate, volume=volume_str)
        
        audio_chunks = []
        word_timings = []
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                word_data = {
                    "word": chunk["text"],
                    "start_time": chunk["offset"] / 10000,  # Convert from 100ns to ms
                    "end_time": (chunk["offset"] + chunk["duration"]) / 10000,
                    "offset": chunk["offset"] / 10000,
                    "duration": chunk["duration"] / 10000
                }
                word_timings.append(word_data)
        
        if not audio_chunks:
            raise RuntimeError("No audio generated from Edge TTS")
        
        audio_bytes = b''.join(audio_chunks)
        return audio_bytes, word_timings
    
    def get_supported_voices(self) -> List[Dict[str, str]]:
        """Get list of supported Chinese voices"""
        return self.supported_voices.copy()
    
    def validate_voice(self, voice_id: str) -> bool:
        """Validate if voice ID is supported"""
        return any(voice["id"] == voice_id for voice in self.supported_voices)
    
    def _convert_speed_to_rate(self, speed: float) -> str:
        """
        Convert speed multiplier to Edge TTS rate format
        
        Args:
            speed: Speed multiplier (0.5 = 50% speed, 2.0 = 200% speed)
            
        Returns:
            Rate string for Edge TTS (e.g., "+50%", "-25%")
        """
        if speed == 1.0:
            return "+0%"
        
        # Convert to percentage change
        percentage = int((speed - 1.0) * 100)
        
        # Clamp to Edge TTS limits (-50% to +100%)
        percentage = max(-50, min(100, percentage))
        
        if percentage >= 0:
            return f"+{percentage}%"
        else:
            return f"{percentage}%"
    
    def _convert_volume_to_edge_format(self, volume: float) -> str:
        """
        Convert volume level to Edge TTS volume format
        
        Args:
            volume: Volume level (0.0 = 0%, 1.0 = 100%)
            
        Returns:
            Volume string for Edge TTS (e.g., "+20%", "-50%")
        """
        if volume == 1.0:
            return "+0%"
        
        # Convert to percentage change from normal volume
        # 0.0 = -100% (silent), 0.5 = -50%, 1.0 = +0% (normal), 1.5 = +50%
        percentage = int((volume - 1.0) * 100)
        
        # Clamp to Edge TTS limits (-100% to +100%)
        percentage = max(-100, min(100, percentage))
        
        if percentage >= 0:
            return f"+{percentage}%"
        else:
            return f"{percentage}%"