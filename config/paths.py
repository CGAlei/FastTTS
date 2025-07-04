"""
Central path configuration system for FastTTS
Automatically detects project root and provides relative paths
"""

import os
import sys
from pathlib import Path
from typing import Optional, Union
import logging

logger = logging.getLogger(__name__)


class PathManager:
    """
    Manages all file paths for FastTTS application
    Auto-detects project root and provides relative paths
    """
    
    def __init__(self, project_root: Optional[Union[str, Path]] = None):
        """
        Initialize path manager
        
        Args:
            project_root: Optional project root path. If None, auto-detected.
        """
        self._project_root = self._detect_project_root(project_root)
        self._validate_project_structure()
        
        logger.info(f"PathManager initialized with project root: {self._project_root}")
    
    def _detect_project_root(self, provided_root: Optional[Union[str, Path]] = None) -> Path:
        """
        Detect the project root directory
        
        Args:
            provided_root: Optional provided root path
            
        Returns:
            Path to project root
        """
        if provided_root:
            root = Path(provided_root).resolve()
            if self._is_valid_project_root(root):
                return root
            else:
                logger.warning(f"Provided root {root} is not valid, auto-detecting...")
        
        # Method 1: Use __file__ location (most reliable)
        current_file = Path(__file__).resolve()
        potential_root = current_file.parent.parent  # Go up from config/ to project root
        
        if self._is_valid_project_root(potential_root):
            return potential_root
        
        # Method 2: Use main module location
        try:
            import __main__
            if hasattr(__main__, '__file__'):
                main_file = Path(__main__.__file__).resolve()
                potential_root = main_file.parent
                if self._is_valid_project_root(potential_root):
                    return potential_root
        except:
            pass
        
        # Method 3: Search up from current working directory
        cwd = Path.cwd()
        current = cwd
        while current != current.parent:  # Stop at filesystem root
            if self._is_valid_project_root(current):
                return current
            current = current.parent
        
        # Method 4: Use environment variable fallback
        env_root = os.getenv('FASTTTS_PROJECT_ROOT')
        if env_root:
            env_path = Path(env_root).resolve()
            if self._is_valid_project_root(env_path):
                return env_path
        
        # Fallback: Use current working directory
        logger.warning("Could not detect project root, using current working directory")
        return cwd
    
    def _is_valid_project_root(self, path: Path) -> bool:
        """
        Check if a path is a valid FastTTS project root
        
        Args:
            path: Path to check
            
        Returns:
            True if valid project root
        """
        if not path.exists() or not path.is_dir():
            return False
        
        # Check for key project files/directories
        required_indicators = [
            'main.py',  # Main application file
            'requirements.txt',  # Dependencies
            'config',  # Config directory
        ]
        
        for indicator in required_indicators:
            if not (path / indicator).exists():
                return False
        
        return True
    
    def _validate_project_structure(self):
        """Validate and create necessary directories"""
        directories_to_ensure = [
            self.sessions_dir,
            self.logs_dir,
            self.db_dir,
            self.static_dir,
        ]
        
        for directory in directories_to_ensure:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Ensured directory exists: {directory}")
            except Exception as e:
                logger.error(f"Failed to create directory {directory}: {e}")
    
    @property
    def project_root(self) -> Path:
        """Get project root directory"""
        return self._project_root
    
    @property
    def db_dir(self) -> Path:
        """Get database directory"""
        return self._project_root / "db"
    
    @property
    def sessions_dir(self) -> Path:
        """Get sessions directory"""
        custom_sessions = os.getenv('FASTTTS_SESSIONS_DIR')
        if custom_sessions:
            sessions_path = Path(custom_sessions)
            if sessions_path.is_absolute():
                return sessions_path
            else:
                return self._project_root / sessions_path
        return self._project_root / "sessions"
    
    @property
    def static_dir(self) -> Path:
        """Get static assets directory"""
        return self._project_root / "static"
    
    @property
    def logs_dir(self) -> Path:
        """Get logs directory"""
        custom_logs = os.getenv('FASTTTS_LOG_DIR', 'logs')
        logs_path = Path(custom_logs)
        if logs_path.is_absolute():
            return logs_path
        else:
            return self._project_root / logs_path
    
    @property
    def vocab_db_path(self) -> Path:
        """Get vocabulary database path"""
        custom_db = os.getenv('FASTTTS_VOCAB_DB_PATH')
        if custom_db:
            db_path = Path(custom_db)
            if db_path.is_absolute():
                return db_path
            else:
                return self._project_root / db_path
        return self.db_dir / "vocab.db"
    
    @property
    def session_metadata_file(self) -> Path:
        """Get session metadata file path"""
        return self.sessions_dir / "session_metadata.json"
    
    @property
    def env_file(self) -> Path:
        """Get .env file path"""
        return self._project_root / ".env"
    
    def get_session_dir(self, session_id: str) -> Path:
        """
        Get directory for specific session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Path to session directory
        """
        return self.sessions_dir / session_id
    
    def get_session_file(self, session_id: str, filename: str) -> Path:
        """
        Get file path within session directory
        
        Args:
            session_id: Session identifier
            filename: File name within session
            
        Returns:
            Path to session file
        """
        return self.get_session_dir(session_id) / filename
    
    def find_vocab_databases(self) -> list[Path]:
        """
        Find all vocabulary databases in the system
        Searches in db/ directory and any custom locations
        
        Returns:
            List of found database paths
        """
        databases = []
        
        # Check default location
        default_db = self.vocab_db_path
        if default_db.exists():
            databases.append(default_db)
        
        # Check for additional databases in db directory
        if self.db_dir.exists():
            for db_file in self.db_dir.glob("*.db"):
                if db_file != default_db and db_file not in databases:
                    databases.append(db_file)
        
        # Check environment variables for additional databases
        additional_dbs = os.getenv('FASTTTS_ADDITIONAL_VOCAB_DBS', '')
        if additional_dbs:
            for db_path in additional_dbs.split(';'):
                db_path = db_path.strip()
                if db_path:
                    db_file = Path(db_path)
                    if not db_file.is_absolute():
                        db_file = self._project_root / db_file
                    if db_file.exists() and db_file not in databases:
                        databases.append(db_file)
        
        return databases
    
    def to_dict(self) -> dict:
        """
        Get path configuration as dictionary
        
        Returns:
            Dictionary with all configured paths
        """
        return {
            'project_root': str(self.project_root),
            'db_dir': str(self.db_dir),
            'sessions_dir': str(self.sessions_dir),
            'static_dir': str(self.static_dir),
            'logs_dir': str(self.logs_dir),
            'vocab_db_path': str(self.vocab_db_path),
            'session_metadata_file': str(self.session_metadata_file),
            'env_file': str(self.env_file),
        }
    
    def __str__(self) -> str:
        """String representation of path manager"""
        return f"PathManager(project_root={self.project_root})"
    
    def __repr__(self) -> str:
        """Detailed representation of path manager"""
        return f"PathManager(project_root={self.project_root}, paths={self.to_dict()})"


# Global path manager instance
_path_manager: Optional[PathManager] = None


def get_path_manager() -> PathManager:
    """
    Get the global path manager instance
    
    Returns:
        PathManager instance
    """
    global _path_manager
    if _path_manager is None:
        _path_manager = PathManager()
    return _path_manager


def reset_path_manager(project_root: Optional[Union[str, Path]] = None):
    """
    Reset the global path manager with new project root
    
    Args:
        project_root: New project root path
    """
    global _path_manager
    _path_manager = PathManager(project_root)


# Convenience functions for common paths
def get_project_root() -> Path:
    """Get project root directory"""
    return get_path_manager().project_root


def get_sessions_dir() -> Path:
    """Get sessions directory"""
    return get_path_manager().sessions_dir


def get_vocab_db_path() -> Path:
    """Get vocabulary database path"""
    return get_path_manager().vocab_db_path


def get_static_dir() -> Path:
    """Get static assets directory"""
    return get_path_manager().static_dir


def get_logs_dir() -> Path:
    """Get logs directory"""
    return get_path_manager().logs_dir