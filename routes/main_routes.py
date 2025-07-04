"""
Main routes for FastTTS application.
Contains the main page and session filtering routes.
"""

from fasthtml.common import *
import logging

# Import from parent modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.text_helpers import apply_session_filters, parse_filter_params
from components.layout import render_main_layout

logger = logging.getLogger(__name__)

# Get the rt object from main app
from main import rt, get_sessions, render_session_list, chinese_text, credentials_manager


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