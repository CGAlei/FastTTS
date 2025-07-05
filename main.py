from fasthtml.common import *
from starlette.responses import JSONResponse, Response
import edge_tts
import asyncio
import io
import base64
import json
import re
import sqlite3
import urllib.parse
import urllib.request
from pathlib import Path
from pypinyin import lazy_pinyin, Style as PinyinStyle
from datetime import datetime
import os
import logging
import time
from dotenv import load_dotenv
from config.defaults import DEFAULT_VOLUME, DEFAULT_SPEED, DEFAULT_VOICE, DEFAULT_ENGINE, DEFAULT_VOLUME_DISPLAY

# Load environment variables from .env file
load_dotenv()

# Configure enhanced logging with file rotation
import logging.handlers

def setup_logging():
    """Configure logging with file rotation and multiple handlers"""
    # Get log configuration from environment
    log_level = os.getenv("FASTTTS_LOG_LEVEL", "INFO").upper()
    log_dir = os.getenv("FASTTTS_LOG_DIR", "logs")
    
    # Ensure log directory exists
    log_path = Path(log_dir)
    if not log_path.is_absolute():
        log_path = Path(__file__).parent / log_path
    log_path.mkdir(exist_ok=True)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Console handler (for development)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Main application log file (rotating daily, keep 10 files)
    app_log_file = log_path / "fasttts.log"
    file_handler = logging.handlers.TimedRotatingFileHandler(
        app_log_file,
        when='midnight',
        interval=1,
        backupCount=10,
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, log_level, logging.INFO))
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Error-only log file (for quick debugging)
    error_log_file = log_path / "error.log"
    error_handler = logging.handlers.TimedRotatingFileHandler(
        error_log_file,
        when='midnight',
        interval=1,
        backupCount=10,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    return logging.getLogger(__name__)

# Setup logging and get logger
logger = setup_logging()
logger.info("FastTTS logging system initialized")

# Logging is now configured with:
# - fasttts.log: All application logs (INFO and above)
# - error.log: Error-only logs for quick debugging
# - Console: Formatted output for development
# - Daily rotation: Keeps 10 days of logs automatically

# Import TTS factory and config manager
from tts import TTSFactory
from config import CredentialsManager

# Import progress manager
from progress_manager import progress_manager
from text_processor import preprocess_text_for_tts

# Import path manager
from config.paths import get_path_manager

# Import vocabulary manager
from utils.vocabulary_manager import get_vocabulary_manager

# Import UI components
from components.layout import render_main_layout

# Routes are defined inline to avoid circular imports

# Import utility modules
from utils.text_helpers import (
    check_word_in_vocabulary,
    get_vocabulary_info,
    insert_vocabulary_word,
    get_google_translate,
    update_all_sessions_with_word,
    extract_pinyin_for_characters,
    parse_filter_params,
    apply_session_filters
)
from utils.db_helpers import get_database_connection, close_database_connection
from utils.response_helpers import (
    parse_request_data,
    convert_timings_to_word_data,
    save_timestamps_json,
    create_tts_response
)

# Initialize path manager
path_manager = get_path_manager()

# Initialize vocabulary manager
vocab_manager = get_vocabulary_manager()

# Configuration Constants - Use dynamic paths
DEFAULT_VOICE = os.getenv("FASTTTS_DEFAULT_VOICE", "zh-CN-XiaoxiaoNeural")
DEFAULT_TEXT = os.getenv("FASTTTS_DEFAULT_TEXT", "就像心里起的小波浪，是你突然想到的念头")

# Initialize credentials manager
credentials_manager = CredentialsManager()

app, rt = fast_app(
    hdrs=[
        Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css"),
        Script(src="https://unpkg.com/htmx.org@1.9.6"),
        Meta(name="language", content="zh-CN"),
        Link(rel="stylesheet", href="/static/css/main.css?v=4"),
        Link(rel="stylesheet", href="/static/css/themes.css?v=4"),
        Link(rel="stylesheet", href="/static/css/components.css?v=4"),
        Link(rel="stylesheet", href="/static/css/responsive.css?v=4"),
        Script(src="/static/js/theme-manager.js?v=4"),
        Script(src="/static/js/ui-manager.js?v=4"),
        Script(src="/static/js/session-manager.js?v=4"),
        Script(src="/static/js/audio-player.js?v=4"),
        Script(src="/static/js/karaoke-interactions.js?v=4"),
        Script(src="/static/js/settings-manager.js?v=4"),
        Script(src="/static/js/vocabulary-refresh.js?v=4"),
        Script(src="/static/js/vocab-status-manager.js?v=4"),
        Script(src="/static/js/word-rating.js?v=4"),
        # Smart polling safety mechanism
        Script("""
            // Initialize TTS polling state management
            window.ttsPending = false;
            window.ttsTimeoutId = null;
            
            // Safety timeout to prevent stuck polling (30 seconds max)
            function resetTTSTimeout() {
                if (window.ttsTimeoutId) {
                    clearTimeout(window.ttsTimeoutId);
                }
                window.ttsTimeoutId = setTimeout(function() {
                    if (window.ttsPending) {
                        console.log('TTS polling timeout reached, clearing ttsPending flag');
                        window.ttsPending = false;
                    }
                }, 30000); // 30 second safety timeout
            }
            
            // Override TTS trigger to reset timeout
            const originalTTSClick = document.querySelector ? function() {
                const ttsBtn = document.querySelector('[title="Generate TTS"]');
                if (ttsBtn && ttsBtn.onclick) {
                    const originalOnClick = ttsBtn.onclick;
                    ttsBtn.onclick = function(e) {
                        resetTTSTimeout(); // Reset safety timeout when TTS starts
                        return originalOnClick.call(this, e);
                    };
                }
            } : function() {};
            
            // Initialize on DOM ready
            document.addEventListener('DOMContentLoaded', function() {
                window.ttsPending = false; // Ensure clean state on page load
                setTimeout(originalTTSClick, 100); // Setup after elements load
            });
        """),
    ]
)

chinese_text = DEFAULT_TEXT

# Text processing functions moved to text_processor.py module

# Function moved to utils.text_helpers

# Function moved to utils.text_helpers

# All vocabulary and text processing functions moved to utils modules

# Session metadata management
SESSION_METADATA_FILE = str(path_manager.session_metadata_file)

# Filter utilities moved to utils.text_helpers

def get_session_metadata():
    """Load session metadata from JSON file"""
    if not os.path.exists(SESSION_METADATA_FILE):
        return {}
    
    try:
        with open(SESSION_METADATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def save_session_metadata(metadata_dict):
    """Save session metadata to JSON file with atomic operations"""
    import tempfile
    import shutil
    
    try:
        # Write to temporary file first for atomic operation
        temp_file = SESSION_METADATA_FILE + '.tmp'
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(metadata_dict, f, indent=2, ensure_ascii=False)
        
        # Atomic move to final location
        shutil.move(temp_file, SESSION_METADATA_FILE)
    except IOError as e:
        # Clean up temp file if it exists
        if os.path.exists(temp_file):
            os.unlink(temp_file)
        raise e

def update_session_metadata(session_id, **updates):
    """Update metadata for a specific session"""
    metadata = get_session_metadata()
    
    if session_id not in metadata:
        metadata[session_id] = {
            'is_favorite': False,
            'custom_name': None,
            'created_at': datetime.now().isoformat(),
            'modified_at': datetime.now().isoformat()
        }
    
    # Update provided fields
    for key, value in updates.items():
        metadata[session_id][key] = value
    
    metadata[session_id]['modified_at'] = datetime.now().isoformat()
    save_session_metadata(metadata)
    return metadata[session_id]

def get_sessions():
    """Get list of saved sessions with metadata"""
    import os
    sessions_dir = str(path_manager.sessions_dir)
    sessions = []
    metadata_dict = get_session_metadata()
    metadata_updated = False
    
    if os.path.exists(sessions_dir):
        for session_dir in sorted(os.listdir(sessions_dir), reverse=True):
            session_path = os.path.join(sessions_dir, session_dir)
            if os.path.isdir(session_path):
                metadata_file = os.path.join(session_path, "metadata.json")
                if os.path.exists(metadata_file):
                    try:
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            session_data = json.load(f)
                        
                        # Get UI metadata or create default
                        if session_dir not in metadata_dict:
                            # New session discovered - create metadata entry
                            ui_metadata = {
                                'is_favorite': False,
                                'custom_name': None,
                                'created_at': session_data.get('date', datetime.now().isoformat()),
                                'modified_at': session_data.get('date', datetime.now().isoformat())
                            }
                            metadata_dict[session_dir] = ui_metadata
                            metadata_updated = True
                            logger.info(f"Auto-discovered new session: {session_dir}")
                        else:
                            ui_metadata = metadata_dict[session_dir]
                        
                        sessions.append({
                            'id': session_dir,
                            'text': session_data.get('text', 'No text'),
                            'date': session_data.get('date', 'Unknown date'),
                            'is_favorite': ui_metadata.get('is_favorite', False),
                            'custom_name': ui_metadata.get('custom_name')
                        })
                    except:
                        continue
    
    # Save updated metadata if new sessions were discovered
    if metadata_updated:
        save_session_metadata(metadata_dict)
        logger.info("Session metadata updated with newly discovered sessions")
    
    return sessions

def render_session_list(sessions, filter_params=None, current_session_id=None):
    """Render session list HTML fragment"""
    if not sessions:
        return Div(
            Div(
                "No sessions found",
                cls="text-center text-gray-500 py-8"
            ),
            id="sessions-list",
            cls="left-sidebar-content"
        )
    
    return Div(
        *[Div(
            # Favorite button
            Button(
                "⭐" if session.get('is_favorite', False) else "☆",
                cls=f"favorite-btn {'favorite-active' if session.get('is_favorite', False) else 'favorite-inactive'}",
                hx_post=f"/toggle-favorite/{session['id']}",
                hx_target="closest .favorite-btn",
                hx_swap="outerHTML",
                title="Toggle favorite"
            ),
            # Session content with improved structure
            Div(
                Div(
                    session.get('custom_name') or (session['text'][:60] + '...' if len(session['text']) > 60 else session['text']), 
                    cls="session-title"
                ),
                Div(session['date'], cls="session-date"),
                cls="session-content",
                hx_get=f"/load-session/{session['id']}",
                hx_target="#audio-container",
                hx_indicator="#loading-indicator",
                onclick=f"setCurrentSession('{session['id']}')"
            ),
            # Edit and Delete buttons
            Div(
                Button(
                    "✏️",
                    cls="edit-btn",
                    title="Rename session",
                    **{"data-session-id": session['id']}
                ),
                Button(
                    "🗑️",
                    cls="delete-btn",
                    hx_delete=f"/delete-session/{session['id']}",
                    hx_target="#sessions-list",
                    hx_confirm="Delete this session?",
                    title="Delete session"
                ),
                cls="session-buttons"
            ),
            cls=f"session-item {'active' if session['id'] == current_session_id else ''}"
        ) for session in sessions],
        id="sessions-list",
        cls="left-sidebar-content"
    )

# Session routes moved to routes/sessions.py

@rt("/")
def get(request):
    """
    Main route handler - now using modular components for clean separation of concerns.
    Reduced from 648 lines to ~15 lines while maintaining all functionality.
    """
    # Parse any initial filter parameters
    filter_params = parse_filter_params(request)
    
    # Get current session from URL if any
    current_session_id = getattr(request, 'query_params', {}).get('session')
    
    # Get and filter sessions
    all_sessions = get_sessions()
    sessions = apply_session_filters(all_sessions, filter_params)
    
    # Render using modular components
    return render_main_layout(
        sessions=sessions,
        filter_params=filter_params,
        current_session_id=current_session_id,
        chinese_text=chinese_text,
        render_session_list_func=render_session_list,
        credentials_manager=credentials_manager
    )


@rt("/filter-sessions", methods=["GET", "POST"])
async def filter_sessions(request):
    """Filter sessions based on query parameters or form data"""
    try:
        filter_params = {
            'show_favorites': False,
            'search_text': '',
            'sort_by': 'date'
        }
        
        # Handle GET request (query parameters)
        if request.method == "GET":
            query_params = getattr(request, 'query_params', {})
            
            # Handle favorites filter
            favorites_param = query_params.get('favorites', '')
            if favorites_param and str(favorites_param).lower() in ['true', '1', 'yes', 'on']:
                filter_params['show_favorites'] = True
            
            # Handle search text
            search_param = query_params.get('search', '').strip()
            if search_param and len(search_param) <= 100:
                filter_params['search_text'] = search_param
        
        # Handle POST request (form data from HTMX)
        elif request.method == "POST":
            try:
                form_data = await request.form()
                
                # Handle search text from form
                search_param = form_data.get('search', '').strip()
                if search_param and len(search_param) <= 100:
                    filter_params['search_text'] = search_param
                
                # Handle favorites from form or query params
                favorites_param = form_data.get('favorites') or request.query_params.get('favorites', '')
                if favorites_param and str(favorites_param).lower() in ['true', '1', 'yes', 'on']:
                    filter_params['show_favorites'] = True
                    
            except Exception as form_error:
                logger.debug(f"Form parsing error (trying query params): {form_error}")
                # Fallback to query params if form parsing fails
                query_params = getattr(request, 'query_params', {})
                favorites_param = query_params.get('favorites', '')
                if favorites_param and str(favorites_param).lower() in ['true', '1', 'yes', 'on']:
                    filter_params['show_favorites'] = True
        
        # Debug logging
        logger.debug(f"Filter params: {filter_params}")
        
        # Get all sessions
        all_sessions = get_sessions()
        logger.debug(f"Total sessions: {len(all_sessions)}")
        
        # Apply filters
        filtered_sessions = apply_session_filters(all_sessions, filter_params)
        logger.debug(f"Filtered sessions: {len(filtered_sessions)}")
        
        # Get current session ID if available - check both form and query params
        current_session_id = None
        if request.method == "POST":
            try:
                form_data = await request.form()
                current_session_id = form_data.get('current_session') or request.query_params.get('current_session')
            except:
                current_session_id = request.query_params.get('current_session')
        else:
            current_session_id = request.query_params.get('current_session')
        
        # Return filtered session list HTML
        return render_session_list(filtered_sessions, filter_params, current_session_id)
        
    except Exception as e:
        logger.error(f"Error filtering sessions: {e}")
        return Div(
            "Error loading sessions",
            cls="text-center text-red-500 py-8"
        )


# Response helper functions moved to utils.response_helpers

@rt("/tts-progress/{session_id}")
async def tts_progress_stream(request):
    """Server-Sent Events endpoint for real-time TTS progress updates"""
    session_id = request.path_params.get('session_id')
    
    if not session_id:
        return Response("Session ID required", status_code=400)
    
    # Check if session exists
    session_progress = progress_manager.get_session_progress(session_id)
    if not session_progress:
        return Response("Session not found", status_code=404)
    
    logger.info(f"SSE client connected for session: {session_id}")
    
    async def generate_sse_response():
        """Generator for SSE response"""
        # Send initial connection message
        yield f"data: {json.dumps({'type': 'connected', 'session_id': session_id})}\n\n"
        
        # Send current progress if available
        current_progress = progress_manager.get_session_progress(session_id)
        if current_progress:
            event_data = {
                'type': 'progress_update',
                'session_id': session_id,
                'current_chunk': current_progress['current_chunk'],
                'total_chunks': current_progress['total_chunks'],
                'percentage': current_progress['percentage'],
                'status': current_progress['status'],
                'message': current_progress['message'],
                'timestamp': current_progress['last_update']
            }
            yield f"data: {json.dumps(event_data)}\n\n"
        
        # Keep connection alive and monitor for updates
        try:
            while True:
                # Check if session still exists
                session_data = progress_manager.get_session_progress(session_id)
                if not session_data:
                    # Session completed or expired
                    yield f"data: {json.dumps({'type': 'session_ended', 'session_id': session_id})}\n\n"
                    break
                
                # Check if session is completed
                if session_data.get('status') in ['completed', 'error']:
                    # Send final update and close
                    await asyncio.sleep(2)  # Give time for final message
                    yield f"data: {json.dumps({'type': 'session_ended', 'session_id': session_id})}\n\n"
                    break
                
                # Keep alive ping
                yield f"data: {json.dumps({'type': 'ping', 'timestamp': time.time()})}\n\n"
                await asyncio.sleep(5)  # Ping every 5 seconds
                
        except Exception as e:
            logger.error(f"SSE stream error for session {session_id}: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    from starlette.responses import StreamingResponse
    
    return StreamingResponse(
        generate_sse_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )

@rt("/api/progress-sessions")
def get_progress_sessions():
    """Get active progress sessions for frontend SSE connection"""
    try:
        # Find the most recent active session
        active_sessions = progress_manager.active_sessions
        if not active_sessions:
            return {"active_session": None}
        
        # Return the most recently created session
        latest_session = max(active_sessions.items(), 
                           key=lambda x: x[1]['start_time'])
        
        return {
            "active_session": latest_session[0],
            "status": latest_session[1]['status'],
            "total_chunks": latest_session[1]['total_chunks']
        }
        
    except Exception as e:
        logger.error(f"Error getting progress sessions: {e}")
        return {"active_session": None, "error": str(e)}

@rt("/minimax-progress")
def minimax_progress():
    """Get current MiniMax progress for HTMX progress bar with message"""
    try:
        # Get current progress from progress_manager
        minimax_progress = progress_manager.get_minimax_progress()
        if minimax_progress:
            current_chunk = minimax_progress.get('current_chunk', 0)
            total_chunks = minimax_progress.get('total_chunks', 1)
            percentage = int((current_chunk / total_chunks) * 100) if total_chunks > 0 else 0
            message = minimax_progress.get('message', '')
        else:
            percentage = 0
            message = "Ready to process!"
        
        # Return HTMX progress bar HTML with message
        progress_div = Div(
            # Progress message area
            Div(message, id="progress-message", cls="progress-message"),
            # Progress bar
            Div(
                Div(
                    id="minimax-progress-bar", 
                    cls="progress-bar", 
                    style=f"width:{percentage}%"
                ),
                cls="progress",
                role="progressbar",
                **{"aria-valuemin": "0", "aria-valuemax": "100", "aria-valuenow": str(percentage)}
            )
        )
        
        # Clear ttsPending flag only when TTS is actually complete (100% or finished)
        if minimax_progress and percentage >= 100:
            progress_div.children.append(
                Script("window.ttsPending = false; console.log('TTS completed, clearing ttsPending flag');")
            )
        
        return progress_div
        
    except Exception as e:
        logger.debug(f"Progress check error: {e}")
        # Return empty progress bar and message on error
        return Div(
            # Empty message
            Div("", id="progress-message", cls="progress-message"),
            # Empty progress bar
            Div(
                Div(id="minimax-progress-bar", cls="progress-bar", style="width:0%"),
                cls="progress",
                role="progressbar",
                **{"aria-valuemin": "0", "aria-valuemax": "100", "aria-valuenow": "0"}
            )
        )

@rt("/generate-custom-tts", methods=["POST"])
async def generate_custom_tts(request):
    """Main TTS generation endpoint"""
    logger.info("TTS Generation Request Started")
    
    # Parse request data
    custom_text, voice, speed, volume, tts_engine = await parse_request_data(request)
    
    # Preprocess the input text - converts numbers to Chinese and sanitizes
    cleaned_text = preprocess_text_for_tts(custom_text)
    
    # Log text cleaning if changes were made
    if cleaned_text != custom_text:
        logger.info(f"Text sanitized: removed {len(custom_text) - len(cleaned_text)} characters")
    
    # Show notification if text was cleaned
    if cleaned_text != custom_text:
        logger.debug(f"Text cleaned: '{custom_text}' -> '{cleaned_text}'")
    
    logger.info(f"Final parameters: engine={tts_engine}, voice={voice}, speed={speed}x, volume={volume}")
    return await _generate_tts_response(cleaned_text, voice, float(speed), float(volume), tts_engine)

async def _generate_tts_response(text: str, voice: str = DEFAULT_VOICE, speed: float = DEFAULT_SPEED, volume: float = DEFAULT_VOLUME, engine: str = DEFAULT_ENGINE):
    """Generate TTS audio and create response"""
    try:
        logger.debug(f"TTS Response called - Text: '{text}', Engine: {engine}, Voice: {voice}, Speed: {speed}, Volume: {volume}")
        
        # Get TTS engine instance
        logger.debug(f"Creating TTS engine instance for: {engine}")
        tts_engine = TTSFactory.create_engine(engine)
        logger.debug(f"Engine created: {tts_engine.name}")
        
        # Check if engine is configured (for MiniMax)
        if hasattr(tts_engine, 'is_configured'):
            is_configured = tts_engine.is_configured()
            logger.debug(f"Engine configuration status: {is_configured}")
            if not is_configured:
                logger.error("Engine not properly configured!")
        
        # Generate TTS using the selected engine
        logger.info(f"Starting TTS generation with {tts_engine.name}")
        audio_data, word_timings = await tts_engine.generate_speech(text, voice, speed, volume)
        logger.info(f"TTS generation completed - Audio size: {len(audio_data)} bytes, Word timings: {len(word_timings)} entries")
        
        # Convert timing data to frontend format
        word_data = convert_timings_to_word_data(word_timings)
        
        # Encode audio as base64
        audio_base64 = base64.b64encode(audio_data).decode()
        
        # Extract pinyin data for characters
        pinyin_data = extract_pinyin_for_characters(text)
        
        # Save timing data to JSON file
        json_file_path = save_timestamps_json(word_data)
        
        # Create and return response
        return create_tts_response(audio_base64, word_data, pinyin_data, text, json_file_path)
    
    except Exception as e:
        import traceback
        logger.error(f"TTS Generation Failed - Error: {type(e).__name__}: {str(e)}, Engine: {engine}, Voice: {voice}, Speed: {speed}, Text: '{text}'")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        
        return Div(
            f"❌ Error generating TTS: {str(e)}", 
            cls="text-red-500 p-4 bg-red-50 border border-red-200 rounded-md"
        )

@rt("/word-interaction", methods=["POST"])
async def word_interaction(request):
    """Handle word container interaction callbacks from frontend"""
    try:
        data = await request.json()
        action = data.get('action')
        word_data = data.get('data', {})
        timestamp = data.get('timestamp')
        
        word_id = word_data.get('wordId')
        word_index = word_data.get('wordIndex')
        word_text = word_data.get('wordText')
        start_time = word_data.get('startTime')
        end_time = word_data.get('endTime')
        
        logger.debug(f"Word interaction: {action} on '{word_text}' ({word_id})")
        
        # Handle different interaction types
        if action == 'left-click':
            # Check if word exists in vocabulary database
            vocab_info = get_vocabulary_info(word_text)
            
            if vocab_info:
                # Word exists in database - display full info in right sidebar
                response_action = {
                    'action': 'show-vocabulary-info',
                    'wordId': word_id,
                    'vocabularyData': vocab_info
                }
            else:
                # Word not in database - play audio segment
                response_action = {
                    'action': 'play-word-audio',
                    'wordId': word_id,
                    'startTime': start_time,
                    'endTime': end_time
                }
            
        elif action == 'right-click':
            # Check if word exists in vocabulary database
            vocab_info = get_vocabulary_info(word_text)
            
            if vocab_info:
                # Word exists in database - show full vocabulary info
                response_action = {
                    'action': 'show-vocabulary-info',
                    'wordId': word_id,
                    'vocabularyData': vocab_info
                }
            else:
                # Word not in database - show Google Translate popup
                translation = get_google_translate(word_text)
                response_action = {
                    'action': 'show-translation-popup',
                    'wordId': word_id,
                    'wordText': word_text,
                    'translation': translation,
                    'coordinates': {
                        'x': 0,  # Will be updated by frontend
                        'y': 0   # Will be updated by frontend
                    }
                }
            
        elif action == 'hover-enter':
            # Example: Subtle highlight
            response_action = {
                'action': 'highlight-word',
                'wordId': word_id,
                'duration': 500
            }
            
        else:
            response_action = {
                'action': 'unknown',
                'message': f"Unknown action: {action}"
            }
        
        # Log interaction for analytics/learning
        logger.debug(f"Processing {action} for word '{word_text}' at position {word_index}")
        
        return {
            'success': True,
            'received': {
                'action': action,
                'wordText': word_text,
                'wordId': word_id
            },
            **response_action
        }
        
    except Exception as e:
        logger.error(f"Error processing word interaction: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

@rt("/define-word", methods=["POST"])
async def define_word(request):
    """Generate AI-powered definition for unknown word and save to database"""
    try:
        data = await request.json()
        word = data.get('word', '').strip()
        word_id = data.get('wordId', '')
        current_session_id = data.get('currentSessionId', '')
        
        if not word:
            logger.error("No word provided for definition")
            return JSONResponse({
                'success': False,
                'error': 'No word provided'
            }, status_code=400)
        
        logger.info(f"Starting AI definition generation for word: {word}")
        
        # Import and initialize LLM manager
        from llm_manager import LLMManager
        llm_manager = LLMManager()
        
        # Check if any LLM service is available
        if not llm_manager.is_available():
            logger.error("No LLM services available")
            return JSONResponse({
                'success': False,
                'error': 'AI definition service unavailable'
            }, status_code=503)
        
        try:
            # Generate definition using AI
            logger.info(f"Calling LLM service for word: {word}")
            definition_data = llm_manager.get_word_definition(word)
            logger.info(f"LLM successfully generated definition for: {word}")
            
            # Add the original word to the definition data
            definition_data['word'] = word
            
            # Save to database
            success = insert_vocabulary_word(definition_data)
            
            if success:
                logger.info(f"Successfully saved AI-generated definition for: {word}")
                
                # Get the complete vocabulary info for response
                vocab_info = get_vocabulary_info(word)
                
                # Prepare immediate response
                response_data = {
                    'success': True,
                    'message': 'Word definition generated and saved successfully',
                    'word': word,
                    'wordId': word_id,
                    'vocabularyData': vocab_info
                }
                
                # Trigger background session updates (non-blocking)
                logger.info(f"Starting background session updates for word: {word}")
                asyncio.create_task(update_all_sessions_with_word(word))
                
                return JSONResponse(response_data)
            else:
                logger.error(f"Failed to save definition to database for: {word}")
                return JSONResponse({
                    'success': False,
                    'error': 'Failed to save definition to database'
                }, status_code=500)
                
        except Exception as llm_error:
            logger.error(f"LLM definition generation failed for word '{word}': {llm_error}")
            return JSONResponse({
                'success': False,
                'error': f'Definition generation failed: {str(llm_error)}'
            }, status_code=500)
            
    except Exception as e:
        logger.error(f"Error in define_word endpoint: {e}")
        return JSONResponse({
            'success': False,
            'error': 'Internal server error'
        }, status_code=500)

@rt("/save-session", methods=["POST"])
async def save_session(request):
    try:
        import os
        import datetime
        from pathlib import Path
        
        data = await request.json()
        raw_text = data.get('text', '')
        text = preprocess_text_for_tts(raw_text)  # Preprocess text (number conversion + sanitization) before saving
        word_data = data.get('wordData', [])
        audio_data = data.get('audioData')
        
        # Create session ID with timestamp
        session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = path_manager.get_session_dir(session_id)
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Save metadata
        metadata = {
            'id': session_id,
            'text': text,
            'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'word_count': len(word_data)
        }
        
        with open(session_dir / "metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        # Save word data
        with open(session_dir / "timestamps.json", 'w', encoding='utf-8') as f:
            json.dump(word_data, f, ensure_ascii=False, indent=2)
        
        # Save audio data if available
        if audio_data:
            audio_bytes = base64.b64decode(audio_data)
            with open(session_dir / "audio.mp3", 'wb') as f:
                f.write(audio_bytes)
        
        # Initialize session metadata for UI features
        update_session_metadata(session_id, 
                               is_favorite=False,
                               created_at=datetime.datetime.now().isoformat())
        
        return {"success": True, "session_id": session_id}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

@rt("/toggle-favorite/{session_id}", methods=["POST"])
def toggle_favorite(session_id: str):
    """Toggle favorite status for a session"""
    try:
        # Get current metadata
        metadata = get_session_metadata()
        current_favorite = metadata.get(session_id, {}).get('is_favorite', False)
        
        # Toggle favorite status
        new_favorite = not current_favorite
        update_session_metadata(session_id, is_favorite=new_favorite)
        
        # Create response with updated favorite state
        favorite_icon = "⭐" if new_favorite else "☆"
        favorite_class = "favorite-active" if new_favorite else "favorite-inactive"
        
        return Div(
            Button(
                favorite_icon,
                cls=f"favorite-btn {favorite_class}",
                hx_post=f"/toggle-favorite/{session_id}",
                hx_target="closest .favorite-btn",
                hx_swap="outerHTML",
                title="Toggle favorite" if not new_favorite else "Remove from favorites"
            ),
            # Out-of-band update to refresh entire sidebar list to show updated favorite status
            Div(
                *render_session_list(get_sessions(), {}, None).children,
                id="sessions-list",
                cls="left-sidebar-content",
                **{"hx-swap-oob": "outerHTML"}
            )
        )
        
    except Exception as e:
        logger.error(f"Error toggling favorite for session {session_id}: {e}")
        return Div("Error", cls="text-red-500")

@rt("/tts-engines-info")
def get_tts_engines_info():
    """Get information about available TTS engines"""
    try:
        engines_info = TTSFactory.get_supported_engines()
        return {
            "success": True,
            "engines": engines_info,
            "default_engine": TTSFactory.get_default_engine()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@rt("/mfa-status")
def get_mfa_status():
    """Get MFA installation and model status"""
    try:
        from alignment import MFAAligner
        aligner = MFAAligner()
        status = aligner.get_installation_status()
        return {
            "success": True,
            "status": status
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@rt("/mfa-setup", methods=["POST"])
async def setup_mfa():
    """Download and setup MFA models"""
    try:
        from alignment import MFAAligner
        aligner = MFAAligner()
        
        if not aligner.is_available:
            return {
                "success": False,
                "error": "MFA not installed. Please install Montreal Forced Aligner first."
            }
        
        result = await aligner.download_models()
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@rt("/credentials-status")
def get_credentials_status():
    """Get credentials configuration status for all engines"""
    try:
        status = credentials_manager.get_all_engine_status()
        return {
            "success": True,
            "engines": status
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@rt("/save-credentials", methods=["POST"])
async def save_credentials(request):
    """Save TTS engine credentials"""
    logger.info("Save Credentials Request")
    
    try:
        data = await request.json()
        engine = data.get('engine', '')
        credentials = data.get('credentials', {})
        
        logger.debug(f"Request data - Engine: {engine}, Credentials keys: {list(credentials.keys())}")
        
        # Log credential values (safely)
        for key, value in credentials.items():
            if 'key' in key.lower() or 'secret' in key.lower():
                logger.debug(f"   {key}: {'***' + value[-4:] if value and len(value) > 4 else 'Empty'}")
            else:
                logger.debug(f"   {key}: {value}")
        
        if not engine:
            logger.error("No engine specified")
            return {
                "success": False,
                "error": "Engine type is required"
            }
        
        logger.debug(f"Calling credentials_manager.set_credentials for: {engine}")
        result = credentials_manager.set_credentials(engine, credentials)
        
        logger.debug(f"Credentials manager result - Success: {result.get('success', False)}")
        if not result.get('success', False):
            logger.error(f"Credentials error: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        import traceback
        logger.error(f"Save credentials failed with exception: {str(e)}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        return {
            "success": False,
            "error": str(e)
        }

@rt("/validate-credentials", methods=["POST"])
async def validate_credentials(request):
    """Validate TTS engine credentials"""
    try:
        data = await request.json()
        engine = data.get('engine', '')
        
        if not engine:
            return {
                "success": False,
                "error": "Engine type is required"
            }
        
        result = credentials_manager.validate_credentials(engine)
        return {
            "success": True,
            "validation": result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@rt("/load-session/{session_id}")
async def load_session(session_id: str):
    try:
        import os
        from pathlib import Path
        
        session_dir = path_manager.get_session_dir(session_id)
        
        if not session_dir.exists():
            return Div("Session not found", cls="text-red-500")
        
        # Load metadata
        with open(session_dir / "metadata.json", 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # Preprocess the loaded text for consistency with TTS generation
        cleaned_text = preprocess_text_for_tts(metadata['text'])
        
        # Load word data
        word_data = []
        if (session_dir / "timestamps.json").exists():
            with open(session_dir / "timestamps.json", 'r', encoding='utf-8') as f:
                word_data = json.load(f)
        
        # Load audio data
        audio_data = None
        if (session_dir / "audio.mp3").exists():
            with open(session_dir / "audio.mp3", 'rb') as f:
                audio_bytes = f.read()
                audio_data = base64.b64encode(audio_bytes).decode()
        
        # Generate pinyin data for the cleaned text
        pinyin_data = extract_pinyin_for_characters(cleaned_text)
        
        # Return the same format as TTS generation for karaoke functionality
        return Div(
            Audio(
                Source(src=f"data:audio/mp3;base64,{audio_data}", type="audio/mpeg"),
                id="audio-player",
                controls=False,
                autoplay=False,
                style="display: none;"
            ),
            Div(id="word-data", style="display:none", **{"data-words": json.dumps(word_data, ensure_ascii=False)}),
            Div(id="pinyin-data", style="display:none", **{"data-pinyin": json.dumps(pinyin_data, ensure_ascii=False)}),
            # Out-of-band update to text display
            Div(
                cleaned_text, 
                id="text-display", 
                cls="font-size-medium leading-relaxed whitespace-pre-wrap",
                **{"hx-swap-oob": "innerHTML"}
            ),
            # Out-of-band update to input textarea 
            Textarea(
                cleaned_text,
                name="custom_text",
                id="custom-text",
                rows="4",
                placeholder="Enter Chinese text for TTS...",
                cls="w-full p-4 pr-16 border-0 resize-none focus:outline-none text-base bg-transparent",
                **{"hx-swap-oob": "outerHTML"}
            ),
            # Out-of-band update to refresh sidebar with active session
            Div(
                *render_session_list(get_sessions(), {}, session_id).children,
                id="sessions-list",
                **{"hx-swap-oob": "innerHTML"}
            ),
            Div(
                H3(f"📄 Session: {session_id}", cls="text-lg font-semibold mb-2"),
                P(f"📅 Date: {metadata.get('date', 'Unknown')}", cls="text-sm text-gray-600"),
                P(f"🔤 Words: {len(word_data)}", cls="text-sm text-gray-600"),
                cls="mt-4"
            ),
            cls="mt-4"
        )
    
    except Exception as e:
        return Div(f"Error loading session: {str(e)}", cls="text-red-500")

@rt("/delete-session/{session_id}", methods=["DELETE"])
async def delete_session(session_id: str):
    try:
        import os
        import shutil
        from pathlib import Path
        
        # Get list of sessions before deletion to determine next selection
        all_sessions_before = get_sessions()
        deleted_session_index = None
        
        # Find the index of the session being deleted
        for i, session in enumerate(all_sessions_before):
            if session['id'] == session_id:
                deleted_session_index = i
                break
        
        session_dir = path_manager.get_session_dir(session_id)
        
        if session_dir.exists():
            shutil.rmtree(session_dir)
            logger.info(f"Deleted session: {session_id}")
        
        # Remove from session metadata JSON
        metadata = get_session_metadata()
        if session_id in metadata:
            del metadata[session_id]
            save_session_metadata(metadata)
            logger.info(f"Removed session {session_id} from metadata JSON")
        
        # Get updated session list after deletion
        remaining_sessions = get_sessions()
        
        # Determine which session to auto-select
        auto_select_session_id = None
        if remaining_sessions and deleted_session_index is not None:
            if deleted_session_index < len(remaining_sessions):
                # Select the session that took the deleted session's position
                auto_select_session_id = remaining_sessions[deleted_session_index]['id']
            elif len(remaining_sessions) > 0:
                # If we deleted the last session, select the new last session
                auto_select_session_id = remaining_sessions[-1]['id']
        
        # Return updated session list with auto-selection
        session_list_html = render_session_list(remaining_sessions, {}, auto_select_session_id)
        
        # If we have a session to auto-select, add JavaScript to trigger it
        if auto_select_session_id:
            session_list_html = Div(
                session_list_html,
                Script(f"""
                    // Auto-select the next session after deletion
                    setTimeout(function() {{
                        setCurrentSession('{auto_select_session_id}');
                        // Trigger the session loading
                        const sessionElement = document.querySelector('[onclick*="{auto_select_session_id}"]');
                        if (sessionElement) {{
                            sessionElement.click();
                        }}
                    }}, 100);
                """)
            )
        
        return session_list_html
    
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {str(e)}")
        return Div(f"Error deleting session: {str(e)}", cls="vocab-word-antonym p-4")

@rt("/rename-session/{session_id}", methods=["POST"])
async def rename_session(session_id: str, request):
    """Rename a session with custom name"""
    logger.info(f"Rename session endpoint called for session: {session_id}")
    try:
        form_data = await request.form()
        new_name = form_data.get('new_name', '').strip()
        
        # Validate session exists
        session_dir = path_manager.get_session_dir(session_id)
        if not session_dir.exists():
            return JSONResponse({"success": False, "error": "Session not found"}, status_code=404)
        
        # Validate name
        if not new_name:
            return JSONResponse({"success": False, "error": "Session name cannot be empty"}, status_code=400)
        
        if len(new_name) > 100:  # Reasonable length limit
            return JSONResponse({"success": False, "error": "Session name too long (max 100 characters)"}, status_code=400)
        
        # Update session metadata with custom name
        update_session_metadata(session_id, custom_name=new_name)
        logger.info(f"Renamed session {session_id} to: {new_name}")
        
        # Get current session from request form data or default to None
        current_session_id = form_data.get('current_session_id', None)
        
        # Return updated session item HTML for HTMX replacement
        sessions = get_sessions()
        updated_session = next((s for s in sessions if s['id'] == session_id), None)
        
        if updated_session:
            # Just return success - the frontend will update the display
            return JSONResponse({"success": True, "session": updated_session})
        else:
            return JSONResponse({"success": False, "error": "Failed to retrieve updated session"}, status_code=500)
            
    except Exception as e:
        logger.error(f"Error renaming session {session_id}: {str(e)}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@rt("/vocabulary-display", methods=["POST"])
async def vocabulary_display(request):
    """Return HTML content for displaying vocabulary information in right sidebar"""
    try:
        data = await request.json()
        vocab_data = data.get('vocabularyData', {})
        
        if not vocab_data:
            return Div("No vocabulary data available", cls="vocab-status-text-primary p-4")
        
        return Div(
            # Card-based content layout
            Div(
                # Enhanced Word Header with prominent styling - MOVED INSIDE GRID
                Div(
                    Div(
                        H1(vocab_data.get('word', ''), cls="vocab-card-title text-3xl font-bold mb-2"),
                        H2(vocab_data.get('pinyin', ''), cls="vocab-card-subtitle text-lg font-medium"),
                        # Star rating component
                        Div(
                            Input(
                                type="range",
                                min="0",
                                max="5",
                                step="1",
                                value=str(vocab_data.get('rating', 0)),
                                cls="star-rating",
                                style=f"--val: {vocab_data.get('rating', 0)}",
                                oninput="this.style.setProperty('--val', this.value); updateWordRating(this.value)",
                                **{"data-word": vocab_data.get('word', '')},
                                id="word-rating-input"
                            ),
                            cls="flex justify-center mt-3"
                        ),
                        cls="vocab-card-header text-center"
                    ),
                    cls="vocab-card vocab-card-sm"
                ),
                
                # Other cards follow...
                # Translation Card
                Div(
                    Div("Translation", cls="vocab-card-label"),
                    Div(
                        Span("🇪🇸 ", cls="text-lg mr-1"),
                        Span(vocab_data.get('spanish_meaning', ''), cls="vocab-word-translation text-base font-medium"),
                        cls="vocab-card-content"
                    ),
                    cls="vocab-card vocab-card-sm"
                ),
                
                # Definition Card
                Div(
                    Div("Definition", cls="vocab-card-label"),
                    Div(
                        Span("🇨🇳 ", cls="text-lg mr-1"),
                        Span(vocab_data.get('chinese_meaning', ''), cls="vocab-word-definition text-base"),
                        cls="vocab-card-content"
                    ),
                    cls="vocab-card vocab-card-sm"
                ) if vocab_data.get('chinese_meaning') else None,
                
                # Grammar Card
                Div(
                    Div("Grammar", cls="vocab-card-label"),
                    Div(
                        Span(vocab_data.get('word_type', ''), cls="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium vocab-word-grammar-bg vocab-word-grammar-text"),
                        cls="vocab-card-content"
                    ),
                    cls="vocab-card vocab-card-sm"
                ) if vocab_data.get('word_type') else None,
                
                # Examples Card
                Div(
                    Div("Example", cls="vocab-card-label"),
                    Div(
                        P(vocab_data.get('usage_example', ''), cls="text-sm italic leading-relaxed vocab-word-example-text vocab-word-example-bg p-3 rounded-lg"),
                        cls="vocab-card-content"
                    ),
                    cls="vocab-card vocab-card-sm"
                ) if vocab_data.get('usage_example') else None,
                
                # Related Words Card (if synonyms or antonyms exist)
                Div(
                    Div("Related Words", cls="vocab-card-label"),
                    Div(
                        # Synonyms
                        Div(
                            Span("Synonyms: ", cls="text-xs font-semibold vocab-word-synonym mr-2"),
                            Span(vocab_data.get('synonyms', ''), cls="text-sm vocab-word-synonym"),
                            cls="mb-2"
                        ) if vocab_data.get('synonyms') and vocab_data.get('synonyms') != '无' else None,
                        
                        # Antonyms
                        Div(
                            Span("Antonyms: ", cls="text-xs font-semibold vocab-word-antonym mr-2"),
                            Span(vocab_data.get('antonyms', ''), cls="text-sm vocab-word-antonym"),
                        ) if vocab_data.get('antonyms') and vocab_data.get('antonyms') != '无' else None,
                        
                        cls="vocab-card-content"
                    ),
                    cls="vocab-card vocab-card-sm"
                ) if (vocab_data.get('synonyms') and vocab_data.get('synonyms') != '无') or (vocab_data.get('antonyms') and vocab_data.get('antonyms') != '无') else None,
                
                cls="vocab-cards-container"
            ),
            
            # Database Attribution Footer
            Div(
                Div(
                    cls="border-t my-4",
                    style="border-color: var(--db-footer-border);"
                ),
                Div(
                    # Database source information
                    Div(
                        Span("📚 From: ", cls="text-xs font-semibold db-footer-text-primary"),
                        Span(vocab_manager.get_database_stats()['filename'], cls="text-xs font-medium db-footer-text-accent"),
                        cls="mb-1"
                    ),
                    Div(
                        Span("📅 Updated: ", cls="text-xs font-semibold db-footer-text-primary"),
                        Span(vocab_manager.get_database_stats()['last_modified_formatted'] or 'Unknown', cls="text-xs db-footer-text-secondary"),
                        cls="mb-1"
                    ),
                    Div(
                        Span("🔄 State: ", cls="text-xs font-semibold db-footer-text-primary"),
                        Span("Current" if not vocab_manager.needs_refresh() else "Refresh recommended", 
                             cls=f"text-xs {'vocab-word-synonym' if not vocab_manager.needs_refresh() else 'vocab-word-antonym'}"),
                        cls="mb-1"
                    ),
                    cls="database-attribution-info"
                ),
                cls="database-attribution-footer p-3 rounded-lg mt-4 border"
            ),
            
            cls="vocab-display-container"
        )
        
    except Exception as e:
        return Div(f"Error displaying vocabulary: {str(e)}", cls="vocab-word-antonym p-4")


@rt("/refresh-vocabulary", methods=["POST"])
async def refresh_vocabulary():
    """Refresh vocabulary state across all sessions"""
    try:
        logger.info("Starting vocabulary refresh")
        
        # Get refresh statistics
        refresh_result = await vocab_manager.refresh_vocabulary_state()
        
        return JSONResponse({
            'success': refresh_result['success'],
            'message': refresh_result.get('message', 'Refresh completed'),
            'stats': {
                'vocabulary_count': refresh_result.get('vocabulary_count', 0),
                'sessions_processed': refresh_result.get('sessions_processed', 0),
                'words_updated': refresh_result.get('words_updated', 0),
                'duration_seconds': refresh_result.get('duration_seconds', 0)
            }
        })
        
    except Exception as e:
        logger.error(f"Error during vocabulary refresh: {e}")
        return JSONResponse({
            'success': False,
            'error': str(e)
        }, status_code=500)


@rt("/vocab-stats")
async def get_vocab_stats():
    """Get vocabulary database statistics"""
    try:
        db_stats = vocab_manager.get_database_stats()
        refresh_stats = vocab_manager.get_refresh_stats()
        needs_refresh = vocab_manager.needs_refresh()
        
        return JSONResponse({
            'database': db_stats,
            'last_refresh': refresh_stats,
            'needs_refresh': needs_refresh
        })
        
    except Exception as e:
        logger.error(f"Error getting vocabulary stats: {e}")
        return JSONResponse({
            'error': str(e)
        }, status_code=500)


@rt("/refresh-vocabulary-progress/{session_id}")
async def refresh_vocabulary_progress(session_id: str):
    """Server-Sent Events stream for vocabulary refresh progress"""
    
    logger.info(f"SSE client connected for vocabulary refresh: {session_id}")
    
    progress_data = {'progress': 0, 'message': 'Starting refresh...', 'completed': False}
    
    async def progress_callback(message: str, current: int, total: int):
        progress_data['progress'] = current
        progress_data['message'] = message
        progress_data['completed'] = (current >= total)
    
    async def generate_sse_response():
        """Generator for SSE response"""
        try:
            # Send initial connection message
            yield f"data: {json.dumps({'type': 'connected', 'session_id': session_id})}\n\n"
            
            # Start refresh process
            refresh_task = asyncio.create_task(
                vocab_manager.refresh_vocabulary_state(progress_callback)
            )
            
            # Monitor progress
            while not refresh_task.done():
                # Send progress update
                event_data = {
                    'type': 'progress_update',
                    'session_id': session_id,
                    'progress': progress_data['progress'],
                    'message': progress_data['message'],
                    'completed': progress_data['completed'],
                    'timestamp': time.time()
                }
                yield f"data: {json.dumps(event_data)}\n\n"
                
                await asyncio.sleep(0.5)  # Update every 500ms
            
            # Get final result
            result = await refresh_task
            
            # Send completion message
            final_event = {
                'type': 'completed',
                'session_id': session_id,
                'success': result['success'],
                'stats': {
                    'vocabulary_count': result.get('vocabulary_count', 0),
                    'sessions_processed': result.get('sessions_processed', 0),
                    'words_updated': result.get('words_updated', 0),
                    'duration_seconds': result.get('duration_seconds', 0)
                },
                'timestamp': time.time()
            }
            
            if not result['success']:
                final_event['error'] = result.get('error', 'Unknown error')
            
            yield f"data: {json.dumps(final_event)}\n\n"
            
        except Exception as e:
            logger.error(f"SSE stream error for vocabulary refresh {session_id}: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    from starlette.responses import StreamingResponse
    
    return StreamingResponse(
        generate_sse_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )

@rt("/tab-word-info")
def tab_word_info():
    """Tab content for word information display"""
    return Div(
        id="vocabulary-content",
        cls="vocabulary-display-area",
        style="height: 100%; overflow-y: auto; padding: 8px; box-sizing: border-box;"
    )

@rt("/tab-word-list")
def tab_word_list():
    """Tab content for word list display with search and pagination"""
    return Div(
        # Search Section
        Div(
            Input(
                type="text",
                placeholder="搜索词汇...",
                cls="word-search-input w-full p-3 border border-gray-300 rounded-md text-sm",
                hx_get="/search-words",
                hx_trigger="keyup changed delay:300ms",
                hx_target="#word-list-container",
                hx_include="[name='page']",
                name="search"
            ),
            cls="word-search-container"
        ),
        
        # Word List Container
        Div(
            # Initial load with first page
            **{
                "hx-get": "/search-words?page=1",
                "hx-trigger": "load",
                "hx-target": "this",
                "hx-swap": "innerHTML"
            },
            id="word-list-container",
            cls="word-list-container flex-1 overflow-y-auto"
        ),
        
        # Hidden page input for pagination
        Input(type="hidden", name="page", value="1", id="current-page"),
        
        cls="vocabulary-display-area flex flex-col h-full"
    )

@rt("/search-words")
def search_words(request):
    """Search vocabulary database with pagination"""
    try:
        # Get search parameters
        search_query = getattr(request, 'query_params', {}).get('search', '').strip()
        page_str = getattr(request, 'query_params', {}).get('page', '1')
        
        # Parse page number
        try:
            page = int(page_str)
            if page < 1:
                page = 1
        except ValueError:
            page = 1
        
        # Pagination settings
        words_per_page = 6
        offset = (page - 1) * words_per_page
        
        # Connect to database
        conn = sqlite3.connect(str(path_manager.vocab_db_path))
        cursor = conn.cursor()
        
        # Build query based on search
        if search_query:
            # Search in Chinese word
            count_query = "SELECT COUNT(*) FROM vocabulary WHERE ChineseWord LIKE ?"
            words_query = """
                SELECT ChineseWord, SpanishMeaning, rating 
                FROM vocabulary 
                WHERE ChineseWord LIKE ? 
                ORDER BY ChineseWord 
                LIMIT ? OFFSET ?
            """
            search_param = f"%{search_query}%"
            cursor.execute(count_query, (search_param,))
            total_words = cursor.fetchone()[0]
            cursor.execute(words_query, (search_param, words_per_page, offset))
        else:
            # Get all words
            cursor.execute("SELECT COUNT(*) FROM vocabulary")
            total_words = cursor.fetchone()[0]
            cursor.execute("""
                SELECT ChineseWord, SpanishMeaning, rating 
                FROM vocabulary 
                ORDER BY ChineseWord 
                LIMIT ? OFFSET ?
            """, (words_per_page, offset))
        
        words = cursor.fetchall()
        conn.close()
        
        # Calculate pagination
        total_pages = (total_words + words_per_page - 1) // words_per_page
        
        # Build word list HTML with multi-line structured layout
        word_items = []
        for chinese_word, spanish_meaning, rating in words:
            word_items.append(
                Div(
                    # Chinese word header with rating space
                    Div(
                        Span(chinese_word, cls="word-chinese-main"),
                        Div(
                            # Star rating display (read-only)
                            Div("", cls="star-display", **{"data-rating": str(rating or 0)}),
                            cls="word-rating-container"
                        ),
                        cls="word-header-row"
                    ),
                    # Spanish translation row
                    Div(
                        spanish_meaning or "No translation available",
                        cls="word-spanish-translation"
                    ),
                    cls="word-list-item-structured",
                    onclick=f"wordListClick('{chinese_word}')"
                )
            )
        
        # Build pagination controls
        pagination_controls = []
        
        if page > 1:
            pagination_controls.append(
                Button(
                    "←",
                    cls="pagination-btn",
                    hx_get=f"/search-words?page={page-1}&search={search_query}",
                    hx_target="#word-list-container",
                    hx_swap="innerHTML"
                )
            )
        
        pagination_controls.append(
            Span(f"{page} of {total_pages}", cls="pagination-info")
        )
        
        if page < total_pages:
            pagination_controls.append(
                Button(
                    "→",
                    cls="pagination-btn",
                    hx_get=f"/search-words?page={page+1}&search={search_query}",
                    hx_target="#word-list-container",
                    hx_swap="innerHTML"
                )
            )
        
        # Return complete content
        return Div(
            # Word list
            Div(
                *word_items if word_items else [Div("No words found", cls="text-center text-gray-500 py-8")],
                cls="word-list-content p-4"
            ),
            
            # Pagination
            Div(
                *pagination_controls,
                cls="word-pagination flex items-center justify-between p-4 border-t"
            ) if total_pages > 1 else None,
            
            cls="word-list-container h-full flex flex-col"
        )
        
    except Exception as e:
        logger.error(f"Error searching words: {e}")
        return Div(
            "Error loading vocabulary list",
            cls="text-center text-red-500 py-8"
        )

@rt("/update-word-rating", methods=["POST"])
async def update_word_rating(request):
    """Update the rating for a vocabulary word"""
    try:
        data = await request.json()
        word = data.get('word', '').strip()
        rating = data.get('rating', 0)
        
        # Validate inputs
        if not word:
            return JSONResponse({"success": False, "error": "Word is required"}, status_code=400)
        
        try:
            rating = int(rating)
            if rating < 0 or rating > 5:
                return JSONResponse({"success": False, "error": "Rating must be between 0 and 5"}, status_code=400)
        except ValueError:
            return JSONResponse({"success": False, "error": "Invalid rating value"}, status_code=400)
        
        # Clean the word - remove punctuation and spaces
        cleaned_word = re.sub(r'[^\u4e00-\u9fff]', '', word)
        
        if not cleaned_word:
            return JSONResponse({"success": False, "error": "Invalid Chinese word"}, status_code=400)
        
        # Update the database
        conn = sqlite3.connect(str(path_manager.vocab_db_path))
        cursor = conn.cursor()
        
        # Check if word exists
        cursor.execute("SELECT ChineseWord FROM vocabulary WHERE ChineseWord = ?", (cleaned_word,))
        if not cursor.fetchone():
            conn.close()
            return JSONResponse({"success": False, "error": "Word not found in vocabulary"}, status_code=404)
        
        # Update the rating
        cursor.execute("UPDATE vocabulary SET rating = ? WHERE ChineseWord = ?", (rating, cleaned_word))
        conn.commit()
        conn.close()
        
        logger.info(f"Updated rating for word '{cleaned_word}' to {rating}")
        
        return JSONResponse({"success": True, "word": cleaned_word, "rating": rating})
        
    except Exception as e:
        logger.error(f"Error updating word rating: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


if __name__ == "__main__":
    serve(host='127.0.0.1', port=5001)