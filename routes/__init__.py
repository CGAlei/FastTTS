"""
FastTTS Routes Package

This package contains modular route handlers extracted from the main application
to improve maintainability and separation of concerns.
"""

# Import existing route modules to register them with the FastHTML app
from . import main_routes

__all__ = [
    'main_routes'
]