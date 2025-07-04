"""
Application Context for FastTTS
Provides shared dependencies to avoid circular imports between main.py and route modules.
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class AppContext:
    """Central registry for shared application dependencies."""
    
    def __init__(self):
        self._dependencies: Dict[str, Any] = {}
        self._initialized = False
    
    def register(self, name: str, dependency: Any) -> None:
        """Register a dependency by name."""
        self._dependencies[name] = dependency
        logger.debug(f"Registered dependency: {name}")
    
    def get(self, name: str) -> Any:
        """Get a dependency by name."""
        if name not in self._dependencies:
            raise KeyError(f"Dependency '{name}' not registered. Available: {list(self._dependencies.keys())}")
        return self._dependencies[name]
    
    def get_all(self) -> Dict[str, Any]:
        """Get all registered dependencies."""
        return self._dependencies.copy()
    
    def is_initialized(self) -> bool:
        """Check if context has been initialized with core dependencies."""
        return self._initialized
    
    def mark_initialized(self) -> None:
        """Mark context as initialized."""
        self._initialized = True
        logger.info(f"App context initialized with {len(self._dependencies)} dependencies")

# Global app context instance
app_context = AppContext()

def get_app_context() -> AppContext:
    """Get the global app context instance."""
    return app_context

def register_core_dependencies(
    rt,
    get_sessions,
    render_session_list,
    get_session_metadata,
    save_session_metadata,
    update_session_metadata,
    path_manager,
    preprocess_text_for_tts,
    extract_pinyin_for_characters
):
    """Register core dependencies from main.py."""
    context = get_app_context()
    
    # Register FastHTML router
    context.register('rt', rt)
    
    # Register session functions
    context.register('get_sessions', get_sessions)
    context.register('render_session_list', render_session_list)
    context.register('get_session_metadata', get_session_metadata)
    context.register('save_session_metadata', save_session_metadata)
    context.register('update_session_metadata', update_session_metadata)
    
    # Register utilities
    context.register('path_manager', path_manager)
    context.register('preprocess_text_for_tts', preprocess_text_for_tts)
    context.register('extract_pinyin_for_characters', extract_pinyin_for_characters)
    
    # Mark as initialized
    context.mark_initialized()
    
    logger.info("Core dependencies registered successfully")

def get_dependency(name: str) -> Any:
    """Convenience function to get a dependency."""
    return get_app_context().get(name)