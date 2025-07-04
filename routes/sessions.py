"""
Session management routes for FastTTS application.
"""

from fasthtml.common import *
import logging
import json
import asyncio
from pathlib import Path
from datetime import datetime

# Import required utilities and functions from main scope
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.text_helpers import apply_session_filters
from utils.response_helpers import parse_request_data

logger = logging.getLogger(__name__)

# TODO: This file contains unused route functions that are duplicated in main_routes.py
# These functions are kept for reference but are not registered with the FastHTML app


@rt("/save-session", methods=["POST"])
async def save_session(request):
    """Save current session with audio and metadata"""
    try:
        # Parse request data
        data = await parse_request_data(request)
        text = data.get('text', '').strip()
        audio_data = data.get('audio_data')
        word_data = data.get('word_data', [])
        
        if not text:
            return JSONResponse({
                "success": False, 
                "error": "No text provided"
            }, status_code=400)
        
        if not audio_data:
            return JSONResponse({
                "success": False, 
                "error": "No audio data provided"
            }, status_code=400)
        
        # Generate session ID
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = Path("sessions") / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Save audio
        audio_path = session_dir / "audio.mp3"
        with open(audio_path, "wb") as f:
            f.write(audio_data)
        
        # Save timestamps
        timestamps_path = session_dir / "timestamps.json"
        with open(timestamps_path, "w", encoding="utf-8") as f:
            json.dump(word_data, f, ensure_ascii=False, indent=2)
        
        # Save metadata
        metadata = {
            "text": text,
            "date": datetime.now().isoformat(),
            "wordData": word_data,
            "audioData": None  # Don't store in metadata to keep it lighter
        }
        
        metadata_path = session_dir / "metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Session saved: {session_id}")
        
        return JSONResponse({
            "success": True,
            "session_id": session_id,
            "message": f"Session saved as {session_id}"
        })
        
    except Exception as e:
        logger.error(f"Error saving session: {e}")
        return JSONResponse({
            "success": False,
            "error": f"Failed to save session: {str(e)}"
        }, status_code=500)


@rt("/toggle-favorite/{session_id}", methods=["POST"])
def toggle_favorite(session_id: str):
    """Toggle favorite status for a session"""
    try:
        # Get current metadata
        metadata = get_session_metadata()
        
        # Toggle favorite status
        session_meta = metadata.get(session_id, {})
        current_favorite = session_meta.get('is_favorite', False)
        new_favorite = not current_favorite
        
        # Update metadata
        update_session_metadata(session_id, is_favorite=new_favorite)
        
        # Get updated sessions for rendering
        sessions = get_sessions()
        
        # Return updated session list with OOB swap
        return Div(
            render_session_list(sessions, {}, session_id),
            hx_swap_oob="true",
            id="sessions-list"
        )
        
    except Exception as e:
        logger.error(f"Error toggling favorite for session {session_id}: {e}")
        return Div(
            f"Error updating favorite status",
            cls="text-red-500"
        )


@rt("/load-session/{session_id}")
async def load_session(session_id: str):
    """Load a session and return its content for display"""
    try:
        import base64
        
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
    """Delete a session and return updated session list"""
    try:
        import shutil
        
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
        from starlette.responses import JSONResponse
        
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