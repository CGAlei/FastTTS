"""
Text processing and vocabulary helper functions for FastTTS
"""

import sqlite3
import re
import json
import urllib.parse
import urllib.request
import asyncio
import os
import logging
from pathlib import Path
from datetime import datetime
from pypinyin import lazy_pinyin, Style as PinyinStyle

# Get logger
logger = logging.getLogger(__name__)

# Import path manager
from config.paths import get_path_manager

# Initialize path manager
path_manager = get_path_manager()


def check_word_in_vocabulary(word):
    """Check if a word exists in the vocabulary database"""
    try:
        # Clean the word - remove punctuation and spaces
        cleaned_word = re.sub(r'[^\u4e00-\u9fff]', '', word)
        
        if not cleaned_word:
            return False
            
        conn = sqlite3.connect(str(path_manager.vocab_db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT ChineseWord FROM vocabulary WHERE ChineseWord = ?", (cleaned_word,))
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
    except Exception as e:
        logger.error(f"Error checking vocabulary: {e}")
        return False


def get_vocabulary_info(word):
    """Get complete vocabulary information for a word"""
    try:
        # Clean the word - remove punctuation and spaces
        cleaned_word = re.sub(r'[^\u4e00-\u9fff]', '', word)
        
        if not cleaned_word:
            return None
            
        conn = sqlite3.connect(str(path_manager.vocab_db_path))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ChineseWord, PinyinPronunciation, SpanishMeaning, ChineseMeaning, 
                   Sinonims, Antonims, UsageExample, WordType, rating
            FROM vocabulary WHERE ChineseWord = ?
        """, (cleaned_word,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'word': result[0],
                'pinyin': result[1],
                'spanish_meaning': result[2],
                'chinese_meaning': result[3],
                'synonyms': result[4],
                'antonyms': result[5],
                'usage_example': result[6],
                'word_type': result[7],
                'rating': result[8] or 0
            }
        return None
    except Exception as e:
        logger.error(f"Error getting vocabulary info: {e}")
        return None


def insert_vocabulary_word(word_data):
    """
    Insert new vocabulary word into database from AI-generated definition
    
    Args:
        word_data (dict): Dictionary containing word information from LLM
            - word: Chinese word
            - pinyin: Pinyin pronunciation
            - spanish_meaning: Spanish translation
            - chinese_meaning: Chinese definition
            - word_type: Grammatical type (noun, verb, etc.)
            - synonyms: Synonyms (optional)
            - antonyms: Antonyms (optional)
            - usage_example: Example sentence (optional)
    
    Returns:
        bool: True if insertion successful, False otherwise
    """
    try:
        # Validate required fields
        required_fields = ['word', 'pinyin', 'spanish_meaning', 'chinese_meaning']
        for field in required_fields:
            if not word_data.get(field):
                logger.error(f"Missing required field: {field}")
                return False
        
        # Clean the word - remove punctuation and spaces
        cleaned_word = re.sub(r'[^\u4e00-\u9fff]', '', word_data['word'])
        if not cleaned_word:
            logger.error("No valid Chinese characters in word")
            return False
        
        conn = sqlite3.connect(str(path_manager.vocab_db_path))
        cursor = conn.cursor()
        
        # Use INSERT OR REPLACE to handle duplicates
        cursor.execute("""
            INSERT OR REPLACE INTO vocabulary 
            (ChineseWord, PinyinPronunciation, SpanishMeaning, ChineseMeaning, 
             WordType, Sinonims, Antonims, UsageExample, UpdatedAt, filename, length)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            cleaned_word,
            word_data.get('pinyin', ''),
            word_data.get('spanish_meaning', ''),
            word_data.get('chinese_meaning', ''),
            word_data.get('word_type', ''),
            word_data.get('synonyms', ''),
            word_data.get('antonyms', ''),
            word_data.get('usage_example', ''),
            datetime.now().isoformat(),
            'AI_Generated',  # Mark as AI-generated
            len(cleaned_word)  # Word length
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Successfully inserted word into database: {cleaned_word}")
        return True
        
    except Exception as e:
        logger.error(f"Error inserting vocabulary word: {e}")
        return False


def update_session_timestamp_for_word(session_id, word):
    """
    Update a specific session's timestamps.json to mark a word as in database
    
    Args:
        session_id (str): Session ID (directory name)
        word (str): Chinese word that was added to database
    
    Returns:
        bool: True if update successful, False otherwise
    """
    try:
        session_dir = path_manager.get_session_dir(session_id)
        timestamps_file = session_dir / "timestamps.json"
        
        if not timestamps_file.exists():
            logger.warning(f"Timestamps file not found for session {session_id}")
            return False
        
        # Read current timestamps
        with open(timestamps_file, 'r', encoding='utf-8') as f:
            timestamps_data = json.load(f)
        
        # Clean the word for comparison
        cleaned_word = re.sub(r'[^\u4e00-\u9fff]', '', word)
        if not cleaned_word:
            return False
        
        # Update matching word entries
        updated = False
        for word_entry in timestamps_data:
            if isinstance(word_entry, dict):
                word_text = word_entry.get('word', '')
                cleaned_entry_word = re.sub(r'[^\u4e00-\u9fff]', '', word_text)
                
                if cleaned_entry_word == cleaned_word:
                    word_entry['isInDB'] = True
                    updated = True
        
        if updated:
            # Save updated timestamps
            with open(timestamps_file, 'w', encoding='utf-8') as f:
                json.dump(timestamps_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Updated timestamps for word '{cleaned_word}' in session {session_id}")
            return True
        else:
            logger.debug(f"Word '{cleaned_word}' not found in session {session_id} timestamps")
            return False
            
    except Exception as e:
        logger.error(f"Error updating session timestamp for word '{word}' in session {session_id}: {e}")
        return False


async def update_all_sessions_with_word(word):
    """
    Background task to update all sessions containing a specific word
    
    Args:
        word (str): Chinese word that was added to database
    """
    try:
        sessions_dir = path_manager.sessions_dir
        if not sessions_dir.exists():
            return
        
        updated_count = 0
        total_sessions = 0
        
        # Process all session directories
        for session_path in sessions_dir.iterdir():
            if session_path.is_dir():
                total_sessions += 1
                session_id = session_path.name
                
                # Update this session's timestamps
                if update_session_timestamp_for_word(session_id, word):
                    updated_count += 1
        
        logger.info(f"Background update completed: Updated {updated_count} of {total_sessions} sessions for word '{word}'")
        
    except Exception as e:
        logger.error(f"Error in background session update for word '{word}': {e}")


def extract_pinyin_for_characters(text):
    """Extract pinyin for each character, mapping non-Chinese chars to empty strings"""
    pinyin_data = []
    
    for char in text:
        if '\u4e00' <= char <= '\u9fff':  # Chinese character range
            # Get pinyin with tone marks (e.g., "wǒ")
            pinyin = lazy_pinyin(char, style=PinyinStyle.TONE)[0]
            pinyin_data.append({"char": char, "pinyin": pinyin})
        else:
            # Non-Chinese character (punctuation, space, etc.)
            pinyin_data.append({"char": char, "pinyin": ""})
    
    return pinyin_data


def get_google_translate(text, target_lang='es'):
    """Get translation from Google Translate (free method using web interface)"""
    try:
        # Clean the word - remove punctuation and spaces
        cleaned_text = re.sub(r'[^\u4e00-\u9fff]', '', text)
        
        if not cleaned_text:
            return "Translation not available"
        
        # Use Google Translate web interface
        base_url = "https://translate.googleapis.com/translate_a/single"
        params = {
            'client': 'gtx',
            'sl': 'zh-cn',  # source language: Chinese
            'tl': target_lang,  # target language: Spanish
            'dt': 't',  # return translation
            'q': cleaned_text
        }
        
        url = f"{base_url}?{urllib.parse.urlencode(params)}"
        
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        with urllib.request.urlopen(req, timeout=5) as response:
            result = response.read().decode('utf-8')
            
        # Parse the JSON response
        data = json.loads(result)
        
        if data and len(data) > 0 and data[0] and len(data[0]) > 0:
            translation = data[0][0][0]
            return translation
        else:
            return "Translation not available"
            
    except Exception as e:
        logger.error(f"Google Translate error: {e}")
        return "Translation error"


# Filter utilities
def parse_filter_params(request):
    """Parse and validate filter parameters from request"""
    filter_params = {
        'show_favorites': False,
        'search_text': '',
        'sort_by': 'date'  # date, name, favorites
    }
    
    # Parse query parameters
    query_params = getattr(request, 'query_params', {})
    
    # Handle favorites filter
    favorites_param = query_params.get('favorites', '')
    if favorites_param and str(favorites_param).lower() in ['true', '1', 'yes', 'on']:
        filter_params['show_favorites'] = True
    
    # Handle search text
    search_param = query_params.get('search', '').strip()
    if search_param and len(search_param) <= 100:  # Validate length
        filter_params['search_text'] = search_param
    
    # Handle sort parameter
    sort_param = query_params.get('sort', 'date')
    if sort_param and str(sort_param).lower() in ['date', 'name', 'favorites']:
        filter_params['sort_by'] = str(sort_param).lower()
    
    return filter_params


def apply_session_filters(sessions, filter_params):
    """Apply filtering logic to sessions list"""
    filtered_sessions = sessions.copy()
    
    # Apply favorites filter
    if filter_params['show_favorites']:
        filtered_sessions = [s for s in filtered_sessions if s.get('is_favorite', False)]
    
    # Apply search filter
    if filter_params['search_text']:
        search_text = filter_params['search_text'].lower()
        filtered_sessions = [
            s for s in filtered_sessions 
            if (search_text in (s.get('text') or '').lower() or 
                search_text in (s.get('custom_name') or '').lower())
        ]
    
    # Apply sorting
    if filter_params['sort_by'] == 'name':
        filtered_sessions.sort(key=lambda x: (x.get('custom_name') or x.get('text') or '').lower())
    elif filter_params['sort_by'] == 'favorites':
        filtered_sessions.sort(key=lambda x: (not x.get('is_favorite', False), x.get('date', '')), reverse=True)
    else:  # Default: sort by date (newest first)
        filtered_sessions.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    return filtered_sessions