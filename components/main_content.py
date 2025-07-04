"""
Main content area component for karaoke display and input.
"""

from fasthtml.common import *
from .ui_elements import render_accessibility_controls, render_input_area
from config.defaults import DEFAULT_VOLUME, DEFAULT_SPEED, DEFAULT_VOICE, DEFAULT_ENGINE


def render_main_content(chinese_text=""):
    """
    Renders the main content area with karaoke display and input controls.
    
    Args:
        chinese_text: Text to display in the karaoke area
        
    Returns:
        Div: Main content container
    """
    return Div(
        # Karaoke Area (Top)
        Div(
            # Accessibility controls
            render_accessibility_controls(),
            
            # Text content area
            Div(
                Div(
                    Div(chinese_text, id="text-display", cls="font-size-medium leading-relaxed whitespace-pre-wrap"),
                    id="text-container",
                    cls="mb-4 p-4 bg-gray-50 rounded-lg min-h-[200px]"
                ),
                Div(id="audio-container", cls="mb-4", style="display: none;"),
                Div(id="loading-indicator", cls="mb-4", style="display: none;"),
                Div(id="json-display", cls="mb-4"),
                cls="bg-white p-4 rounded-lg shadow-lg",
                id="content-wrapper"
            ),
            cls="karaoke-area",
            style="min-height: 100%;"
        ),
        
        # Input Area (Bottom) - ChatGPT Style
        render_input_area(
            chinese_text=chinese_text,
            DEFAULT_VOICE=DEFAULT_VOICE,
            DEFAULT_SPEED=DEFAULT_SPEED,
            DEFAULT_VOLUME=DEFAULT_VOLUME,
            DEFAULT_ENGINE=DEFAULT_ENGINE
        ),
        
        cls="main-content"
    )