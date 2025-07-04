"""
Response helper functions for FastTTS
"""

import json
import os
import logging
from fasthtml.common import *
from .text_helpers import check_word_in_vocabulary
from config.defaults import DEFAULT_VOLUME, DEFAULT_SPEED, DEFAULT_VOICE, DEFAULT_ENGINE

# Get logger
logger = logging.getLogger(__name__)


async def parse_request_data(request):
    """Parse request data from form or JSON with fallback to defaults"""
    
    try:
        # Try to get form data first (HTMX form submission)
        form = await request.form()
        custom_text = form.get('custom_text', '')
        voice = form.get('voice', DEFAULT_VOICE)
        speed = form.get('speed', str(DEFAULT_SPEED))
        volume = form.get('volume', str(DEFAULT_VOLUME))
        tts_engine = form.get('tts_engine', DEFAULT_ENGINE)
        logger.debug(f"Form data - Text: '{custom_text[:50]}{'...' if len(custom_text) > 50 else ''}', Engine: {tts_engine}, Voice: {voice}, Speed: {speed}, Volume: {volume}")
        return custom_text, voice, speed, volume, tts_engine
    except Exception as e:
        logger.warning(f"Form parsing failed: {e}")
        try:
            # Fallback to JSON data
            data = await request.json()
            custom_text = data.get('text', data.get('custom_text', ''))
            voice = data.get('voice', DEFAULT_VOICE)
            speed = data.get('speed', str(DEFAULT_SPEED))
            volume = data.get('volume', str(DEFAULT_VOLUME))
            tts_engine = data.get('tts_engine', DEFAULT_ENGINE)
            logger.debug(f"JSON data - Text: '{custom_text[:50]}{'...' if len(custom_text) > 50 else ''}', Engine: {tts_engine}, Voice: {voice}, Speed: {speed}, Volume: {volume}")
            return custom_text, voice, speed, volume, tts_engine
        except Exception as e2:
            logger.error(f"JSON parsing also failed: {e2}")
            # Return defaults
            logger.info(f"Using defaults: engine={DEFAULT_ENGINE}, voice={DEFAULT_VOICE}, speed={DEFAULT_SPEED}, volume={DEFAULT_VOLUME}")
            return '', DEFAULT_VOICE, str(DEFAULT_SPEED), str(DEFAULT_VOLUME), DEFAULT_ENGINE


def should_merge_words(word1, word2):
    """Merge ONLY consecutive single digits to form numbers (e.g., "1"+"8"="18")"""
    if not word1 or not word2:
        return False
    
    # Only merge single characters
    if len(word1) != 1 or len(word2) != 1:
        return False
    
    # Only merge consecutive single digits (0-9)
    if word1.isdigit() and word2.isdigit():
        return True
    
    # Do NOT merge anything else (preserves Chinese character timestamps)
    return False


def convert_timings_to_word_data(word_timings):
    """Convert TTS engine timing data with safety cleaning and character merging"""
    if not word_timings:
        return []
    
    # Safety filter: remove any problematic symbols that somehow made it through TTS
    filtered_timings = []
    for timing in word_timings:
        word_text = timing.get("word", "").strip()
        
        # Skip empty words
        if not word_text:
            continue
            
        # Safety check: filter out individual problematic symbols
        # This catches any symbols that somehow made it through TTS engines
        if word_text in ['"', '"', "'", '"', '—', '–', '―', '-', '[', ']', '(', ')', '{', '}', '\u201C', '\u201D']:
            logger.debug(f"Filtering out problematic symbol: '{word_text}'")
            continue
            
        filtered_timings.append(timing)
    
    # Merge consecutive single characters
    merged_timings = []
    current_group = None
    
    for timing in filtered_timings:
        word_text = timing.get("word", "").strip()
        start_time = timing.get("start_time", timing.get("offset", 0))
            
        if current_group is None:
            # Start new group
            current_group = {
                "word": word_text,
                "start_time": start_time
            }
        elif should_merge_words(current_group["word"], word_text):
            # Merge characters
            current_group["word"] += word_text
        else:
            # Finish current group, start new one
            merged_timings.append(current_group)
            current_group = {
                "word": word_text,
                "start_time": start_time
            }
    
    # Add final group
    if current_group:
        merged_timings.append(current_group)
    
    # Convert to final format
    word_data = []
    for timing in merged_timings:
        word_text = timing["word"]
        is_in_db = check_word_in_vocabulary(word_text)
        
        word_data.append({
            "word": word_text,
            "timestamp": timing["start_time"],
            "isInDB": is_in_db
        })
    
    return word_data


def save_timestamps_json(word_data):
    """Save word timing data to JSON file"""
    from config.paths import get_path_manager
    json_file_path = os.getenv("FASTTTS_TIMESTAMPS_PATH", str(get_path_manager().project_root / "timestamps.json"))
    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(word_data, f, ensure_ascii=False, indent=2)
    return json_file_path


def create_tts_response(audio_base64, word_data, pinyin_data, text, json_file_path):
    """Create the HTML response for TTS generation"""
    return Div(
        Audio(
            Source(src=f"data:audio/mp3;base64,{audio_base64}", type="audio/mpeg"),
            id="audio-player",
            controls=False,
            autoplay=False,
            style="display: none;"
        ),
        Div(id="word-data", style="display:none", **{"data-words": json.dumps(word_data, ensure_ascii=False)}),
        Div(id="pinyin-data", style="display:none", **{"data-pinyin": json.dumps(pinyin_data, ensure_ascii=False)}),
        # Out-of-band update to text display
        Div(
            text, 
            id="text-display", 
            cls="font-size-medium leading-relaxed whitespace-pre-wrap",
            **{"hx-swap-oob": "innerHTML"}
        ),
        Div(
            H3("📄 JSON Timestamps", cls="text-lg font-semibold mb-2"),
            Pre(
                Code(json.dumps(word_data, ensure_ascii=False, indent=2)),
                cls="bg-gray-100 p-3 rounded text-sm overflow-x-auto max-h-60"
            ),
            P(f"💾 Saved to: {json_file_path}", cls="text-sm text-gray-600 mt-2"),
            cls="mt-4"
        ),
        cls="mt-4"
    )