"""
Vocabulary Manager for FastTTS
Handles database changes, vocabulary inventory, and session synchronization
"""

import sqlite3
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
import json
import re
from datetime import datetime

from config.paths import get_path_manager
from utils.text_helpers import update_session_timestamp_for_word

logger = logging.getLogger(__name__)


class VocabularyManager:
    """
    Manages vocabulary database state and session synchronization
    Handles database changes and provides refresh functionality
    """
    
    def __init__(self):
        self.path_manager = get_path_manager()
        self._current_db_path = None
        self._current_vocabulary = set()
        self._last_refresh_time = None
        self._refresh_stats = {}
    
    def get_current_database_path(self) -> Path:
        """Get the current vocabulary database path"""
        return self.path_manager.vocab_db_path
    
    def detect_database_change(self) -> bool:
        """
        Check if the vocabulary database has changed
        
        Returns:
            True if database path or content has changed
        """
        current_path = self.get_current_database_path()
        
        # Check if path changed
        if self._current_db_path != current_path:
            logger.info(f"Database path changed from {self._current_db_path} to {current_path}")
            return True
        
        # Check if database file modification time changed
        if current_path.exists():
            try:
                current_mtime = current_path.stat().st_mtime
                if hasattr(self, '_last_db_mtime'):
                    if current_mtime != self._last_db_mtime:
                        logger.info(f"Database file modification time changed")
                        return True
                self._last_db_mtime = current_mtime
            except Exception as e:
                logger.warning(f"Could not check database modification time: {e}")
        
        return False
    
    def get_database_vocabulary(self, db_path: Optional[Path] = None) -> Set[str]:
        """
        Get all vocabulary words from the database
        
        Args:
            db_path: Optional database path. Uses current database if None.
            
        Returns:
            Set of Chinese words in the database
        """
        if db_path is None:
            db_path = self.get_current_database_path()
        
        vocabulary = set()
        
        try:
            if not db_path.exists():
                logger.warning(f"Database file not found: {db_path}")
                return vocabulary
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Get all Chinese words from vocabulary table
            cursor.execute("SELECT ChineseWord FROM vocabulary WHERE ChineseWord IS NOT NULL")
            rows = cursor.fetchall()
            
            for row in rows:
                word = row[0]
                if word and word.strip():
                    # Clean the word - keep only Chinese characters
                    cleaned_word = re.sub(r'[^\u4e00-\u9fff]', '', word.strip())
                    if cleaned_word:
                        vocabulary.add(cleaned_word)
            
            conn.close()
            
            logger.info(f"Loaded {len(vocabulary)} vocabulary words from {db_path}")
            
        except Exception as e:
            logger.error(f"Error reading vocabulary from database {db_path}: {e}")
        
        return vocabulary
    
    def get_database_stats(self, db_path: Optional[Path] = None) -> Dict:
        """
        Get comprehensive statistics about the vocabulary database
        
        Args:
            db_path: Optional database path. Uses current database if None.
            
        Returns:
            Dictionary with detailed database statistics
        """
        if db_path is None:
            db_path = self.get_current_database_path()
        
        stats = {
            'path': str(db_path),
            'filename': db_path.name if db_path else 'Unknown',
            'directory': str(db_path.parent) if db_path else 'Unknown',
            'exists': False,
            'total_words': 0,
            'file_size': 0,
            'file_size_formatted': '0 B',
            'created_time': None,
            'last_modified': None,
            'last_modified_formatted': None,
            'database_age_days': None,
            'schema_info': {},
            'error': None
        }
        
        try:
            if not db_path.exists():
                stats['error'] = 'Database file not found'
                return stats
            
            stats['exists'] = True
            file_stat = db_path.stat()
            
            # File size information
            stats['file_size'] = file_stat.st_size
            stats['file_size_formatted'] = self._format_file_size(file_stat.st_size)
            
            # Timestamp information
            created_time = datetime.fromtimestamp(file_stat.st_ctime)
            modified_time = datetime.fromtimestamp(file_stat.st_mtime)
            
            stats['created_time'] = created_time.isoformat()
            stats['last_modified'] = modified_time.isoformat()
            stats['last_modified_formatted'] = self._format_datetime(modified_time)
            
            # Calculate database age
            now = datetime.now()
            age_delta = now - created_time
            stats['database_age_days'] = age_delta.days
            
            # Database content information
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Count total vocabulary entries
            cursor.execute("SELECT COUNT(*) FROM vocabulary WHERE ChineseWord IS NOT NULL")
            stats['total_words'] = cursor.fetchone()[0]
            
            # Get schema information
            cursor.execute("PRAGMA table_info(vocabulary)")
            columns = cursor.fetchall()
            stats['schema_info'] = {
                'columns': len(columns),
                'column_names': [col[1] for col in columns]
            }
            
            # Get additional metadata if available
            try:
                cursor.execute("SELECT COUNT(DISTINCT WordType) FROM vocabulary WHERE WordType IS NOT NULL AND WordType != ''")
                stats['word_types_count'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT WordType, COUNT(*) FROM vocabulary WHERE WordType IS NOT NULL AND WordType != '' GROUP BY WordType ORDER BY COUNT(*) DESC LIMIT 5")
                top_word_types = cursor.fetchall()
                stats['top_word_types'] = [{'type': wt[0], 'count': wt[1]} for wt in top_word_types]
                
                # Check for AI-generated words
                cursor.execute("SELECT COUNT(*) FROM vocabulary WHERE filename LIKE '%AI_Generated%' OR filename = 'AI_Generated'")
                ai_generated_count = cursor.fetchone()[0]
                stats['ai_generated_words'] = ai_generated_count
                
            except Exception as e:
                logger.debug(f"Could not get extended database stats: {e}")
            
            conn.close()
            
        except Exception as e:
            stats['error'] = str(e)
            logger.error(f"Error getting database stats for {db_path}: {e}")
        
        return stats
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def _format_datetime(self, dt: datetime) -> str:
        """Format datetime in human readable format"""
        now = datetime.now()
        diff = now - dt
        
        if diff.days > 0:
            return f"{dt.strftime('%Y-%m-%d %H:%M')} ({diff.days}d ago)"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{dt.strftime('%H:%M')} ({hours}h ago)"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{dt.strftime('%H:%M')} ({minutes}m ago)"
        else:
            return f"{dt.strftime('%H:%M')} (just now)"
    
    def get_session_directories(self) -> List[Path]:
        """
        Get all session directories
        
        Returns:
            List of session directory paths
        """
        sessions_dir = self.path_manager.sessions_dir
        session_dirs = []
        
        if sessions_dir.exists():
            for item in sessions_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    # Check if it has session files
                    if (item / "metadata.json").exists() or (item / "timestamps.json").exists():
                        session_dirs.append(item)
        
        return sorted(session_dirs, key=lambda x: x.name, reverse=True)
    
    def count_word_occurrences_in_sessions(self, word: str) -> Dict[str, int]:
        """
        Count how many times a word appears across all sessions
        
        Args:
            word: Chinese word to count
            
        Returns:
            Dictionary with session_id -> occurrence_count mapping
        """
        cleaned_word = re.sub(r'[^\u4e00-\u9fff]', '', word)
        if not cleaned_word:
            return {}
        
        occurrences = {}
        session_dirs = self.get_session_directories()
        
        for session_dir in session_dirs:
            session_id = session_dir.name
            count = 0
            
            timestamps_file = session_dir / "timestamps.json"
            if timestamps_file.exists():
                try:
                    with open(timestamps_file, 'r', encoding='utf-8') as f:
                        timestamps_data = json.load(f)
                    
                    for word_entry in timestamps_data:
                        if isinstance(word_entry, dict):
                            word_text = word_entry.get('word', '')
                            cleaned_entry_word = re.sub(r'[^\u4e00-\u9fff]', '', word_text)
                            if cleaned_entry_word == cleaned_word:
                                count += 1
                
                except Exception as e:
                    logger.error(f"Error reading timestamps for session {session_id}: {e}")
            
            if count > 0:
                occurrences[session_id] = count
        
        return occurrences
    
    async def refresh_vocabulary_state(self, progress_callback: Optional[callable] = None) -> Dict:
        """
        Refresh vocabulary state across all sessions
        Re-synchronizes all sessions with current database vocabulary
        
        Args:
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Dictionary with refresh results and statistics
        """
        start_time = datetime.now()
        
        try:
            # Get current database vocabulary
            current_db_path = self.get_current_database_path()
            vocabulary = self.get_database_vocabulary(current_db_path)
            
            if progress_callback:
                await progress_callback("Loading vocabulary database", 0, 100)
            
            # Get all session directories
            session_dirs = self.get_session_directories()
            total_sessions = len(session_dirs)
            
            if total_sessions == 0:
                return {
                    'success': True,
                    'message': 'No sessions found to refresh',
                    'sessions_processed': 0,
                    'words_updated': 0,
                    'duration_seconds': 0
                }
            
            # Process each session
            sessions_processed = 0
            total_words_updated = 0
            
            for i, session_dir in enumerate(session_dirs):
                session_id = session_dir.name
                
                if progress_callback:
                    progress = int((i / total_sessions) * 100)
                    await progress_callback(f"Processing session {session_id}", progress, 100)
                
                # Update session with all vocabulary words
                words_updated = await self._refresh_session_vocabulary(session_id, vocabulary)
                total_words_updated += words_updated
                sessions_processed += 1
                
                # Small delay to prevent blocking
                await asyncio.sleep(0.01)
            
            # Update internal state
            self._current_db_path = current_db_path
            self._current_vocabulary = vocabulary
            self._last_refresh_time = start_time
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Store refresh statistics
            self._refresh_stats = {
                'last_refresh': start_time.isoformat(),
                'database_path': str(current_db_path),
                'vocabulary_count': len(vocabulary),
                'sessions_processed': sessions_processed,
                'words_updated': total_words_updated,
                'duration_seconds': duration
            }
            
            if progress_callback:
                await progress_callback("Refresh completed", 100, 100)
            
            logger.info(f"Vocabulary refresh completed: {sessions_processed} sessions, "
                       f"{total_words_updated} word updates, {duration:.2f}s")
            
            return {
                'success': True,
                'message': f'Successfully refreshed {sessions_processed} sessions',
                'database_path': str(current_db_path),
                'vocabulary_count': len(vocabulary),
                'sessions_processed': sessions_processed,
                'words_updated': total_words_updated,
                'duration_seconds': duration
            }
            
        except Exception as e:
            logger.error(f"Error during vocabulary refresh: {e}")
            return {
                'success': False,
                'error': str(e),
                'sessions_processed': 0,
                'words_updated': 0,
                'duration_seconds': 0
            }
    
    async def _refresh_session_vocabulary(self, session_id: str, vocabulary: Set[str]) -> int:
        """
        Refresh vocabulary state for a single session
        
        Args:
            session_id: Session identifier
            vocabulary: Set of vocabulary words to mark as in database
            
        Returns:
            Number of words updated in the session
        """
        session_dir = self.path_manager.get_session_dir(session_id)
        timestamps_file = session_dir / "timestamps.json"
        
        if not timestamps_file.exists():
            return 0
        
        try:
            # Read current timestamps
            with open(timestamps_file, 'r', encoding='utf-8') as f:
                timestamps_data = json.load(f)
            
            words_updated = 0
            
            # Update each word entry
            for word_entry in timestamps_data:
                if isinstance(word_entry, dict):
                    word_text = word_entry.get('word', '')
                    cleaned_word = re.sub(r'[^\u4e00-\u9fff]', '', word_text)
                    
                    if cleaned_word and cleaned_word in vocabulary:
                        # Mark as in database
                        if not word_entry.get('isInDB', False):
                            word_entry['isInDB'] = True
                            words_updated += 1
                    else:
                        # Mark as not in database
                        if word_entry.get('isInDB', False):
                            word_entry['isInDB'] = False
                            words_updated += 1
            
            # Save updated timestamps if any changes were made
            if words_updated > 0:
                with open(timestamps_file, 'w', encoding='utf-8') as f:
                    json.dump(timestamps_data, f, ensure_ascii=False, indent=2)
                
                logger.debug(f"Updated {words_updated} words in session {session_id}")
            
            return words_updated
            
        except Exception as e:
            logger.error(f"Error refreshing vocabulary for session {session_id}: {e}")
            return 0
    
    def get_refresh_stats(self) -> Dict:
        """
        Get statistics from the last refresh operation
        
        Returns:
            Dictionary with refresh statistics
        """
        if not self._refresh_stats:
            return {
                'last_refresh': None,
                'database_path': str(self.get_current_database_path()),
                'vocabulary_count': 0,
                'sessions_processed': 0,
                'words_updated': 0,
                'duration_seconds': 0
            }
        
        return self._refresh_stats.copy()
    
    def needs_refresh(self) -> bool:
        """
        Check if a vocabulary refresh is recommended
        
        Returns:
            True if refresh is recommended
        """
        # Check if database has changed
        if self.detect_database_change():
            return True
        
        # Check if we've never refreshed
        if self._last_refresh_time is None:
            return True
        
        # Check if current vocabulary is different from database
        current_vocabulary = self.get_database_vocabulary()
        if current_vocabulary != self._current_vocabulary:
            return True
        
        return False


# Global vocabulary manager instance
_vocabulary_manager: Optional[VocabularyManager] = None


def get_vocabulary_manager() -> VocabularyManager:
    """
    Get the global vocabulary manager instance
    
    Returns:
        VocabularyManager instance
    """
    global _vocabulary_manager
    if _vocabulary_manager is None:
        _vocabulary_manager = VocabularyManager()
    return _vocabulary_manager