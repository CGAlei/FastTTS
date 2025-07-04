"""
Main layout wrapper component for FastTTS application.
"""

from fasthtml.common import *
from .ui_elements import render_mobile_toggle, render_sidebar_toggles
from .sidebar import render_left_sidebar
from .main_content import render_main_content
from .vocabulary import render_right_sidebar
from .modals import render_settings_modal


def render_main_layout(sessions, filter_params, current_session_id, chinese_text="", 
                      render_session_list_func=None, credentials_manager=None):
    """
    Renders the complete main layout with all components.
    
    Args:
        sessions: List of session objects
        filter_params: Dictionary containing filter parameters
        current_session_id: Currently selected session ID
        chinese_text: Text to display in the content area
        render_session_list_func: Function to render the session list (from main.py)
        credentials_manager: CredentialsManager instance for settings modal
        
    Returns:
        Div: Complete application layout
    """
    # Generate sessions content if function provided
    sessions_content = None
    if render_session_list_func:
        sessions_content = render_session_list_func(sessions, filter_params, current_session_id)
    
    return Div(
        # Mobile menu toggle button
        render_mobile_toggle(),
        
        # App container wrapper
        Div(
            # Left Sidebar
            render_left_sidebar(sessions, filter_params, current_session_id, sessions_content),
            
            # Main Content
            render_main_content(chinese_text),
            
            # Right Sidebar
            render_right_sidebar(),
            
            cls="app-container"
        ),
        
        # Sidebar toggle buttons
        render_sidebar_toggles(),
        
        # Settings Modal
        render_settings_modal(credentials_manager)
    )