"""
FastTTS UI Components Package

This package contains modular UI components extracted from the main application
to improve maintainability and separation of concerns.
"""

from .layout import render_main_layout
from .sidebar import render_left_sidebar
from .main_content import render_main_content
from .vocabulary import render_right_sidebar
from .modals import render_settings_modal
from .ui_elements import render_accessibility_controls, render_input_area

__all__ = [
    'render_main_layout',
    'render_left_sidebar', 
    'render_main_content',
    'render_right_sidebar',
    'render_settings_modal',
    'render_accessibility_controls',
    'render_input_area'
]