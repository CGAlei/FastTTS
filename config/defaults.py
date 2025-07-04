"""
FastTTS Default Configuration Values
Centralized location for all default settings
"""

# Audio Settings
DEFAULT_VOLUME = 1.3  # Volume level (0.0 to 2.0, where 1.0 = 100%)
DEFAULT_SPEED = 1.0   # Speech speed multiplier
DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"  # Default TTS voice
DEFAULT_ENGINE = "edge"  # Default TTS engine

# UI Display Formatting
def format_volume_percentage(volume: float) -> str:
    """Convert volume float to percentage string for UI display"""
    return f"{int(volume * 100)}%"

# Derived values for UI
DEFAULT_VOLUME_DISPLAY = format_volume_percentage(DEFAULT_VOLUME)  # "130%"