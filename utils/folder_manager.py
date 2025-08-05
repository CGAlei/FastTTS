"""
Folder management system for organizing sessions into topic-based folders.
Handles folder metadata, session-to-folder mapping, and folder operations.
"""

import json
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from config.paths import get_path_manager

logger = logging.getLogger(__name__)


class FolderManager:
    """
    Manages folder-based organization of sessions.
    
    Handles:
    - Folder creation, deletion, renaming
    - Session-to-folder mapping
    - Folder expand/collapse states
    - Migration of existing sessions
    """
    
    UNCATEGORIZED_FOLDER = "Uncategorized"
    FOLDERS_METADATA_FILE = "folders.json"
    
    def __init__(self):
        """Initialize folder manager with path manager."""
        self.path_manager = get_path_manager()
        self.folders_file = self.path_manager.sessions_dir / self.FOLDERS_METADATA_FILE
        self._metadata = self._load_metadata()
        
    def _load_metadata(self) -> Dict:
        """Load folder metadata from JSON file."""
        if not self.folders_file.exists():
            # Create initial metadata with Uncategorized folder
            metadata = {
                "folders": {
                    self.UNCATEGORIZED_FOLDER: {
                        "created": datetime.now().isoformat(),
                        "expanded": True  # Start expanded
                    }
                },
                "session_folders": {},  # session_id -> folder_name mapping
                "last_modified": datetime.now().isoformat()
            }
            self._save_metadata(metadata)
            return metadata
            
        try:
            with open(self.folders_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Ensure Uncategorized folder exists
            if self.UNCATEGORIZED_FOLDER not in metadata.get("folders", {}):
                metadata.setdefault("folders", {})[self.UNCATEGORIZED_FOLDER] = {
                    "created": datetime.now().isoformat(),
                    "expanded": True
                }
                self._save_metadata(metadata)
                
            return metadata
            
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading folder metadata: {e}")
            # Return default metadata
            return {
                "folders": {self.UNCATEGORIZED_FOLDER: {"created": datetime.now().isoformat(), "expanded": True}},
                "session_folders": {},
                "last_modified": datetime.now().isoformat()
            }
    
    def _save_metadata(self, metadata: Dict) -> None:
        """Save folder metadata to JSON file."""
        try:
            metadata["last_modified"] = datetime.now().isoformat()
            
            # Create backup of existing file
            if self.folders_file.exists():
                backup_file = self.folders_file.with_suffix('.json.backup')
                self.folders_file.rename(backup_file)
            
            # Write new metadata
            with open(self.folders_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
                
            logger.debug(f"Folder metadata saved successfully")
            
        except IOError as e:
            logger.error(f"Error saving folder metadata: {e}")
            raise
    
    def get_folders(self) -> Dict[str, Dict]:
        """Get all folders with their metadata."""
        return self._metadata.get("folders", {})
    
    def get_session_folder(self, session_id: str) -> str:
        """Get the folder name for a session."""
        return self._metadata.get("session_folders", {}).get(session_id, self.UNCATEGORIZED_FOLDER)
    
    def create_folder(self, folder_name: str) -> bool:
        """
        Create a new folder.
        
        Args:
            folder_name: Name of the folder to create
            
        Returns:
            bool: True if created successfully, False if already exists
        """
        if not folder_name or folder_name.strip() == "":
            raise ValueError("Folder name cannot be empty")
            
        folder_name = folder_name.strip()
        
        # Check for invalid characters
        invalid_chars = '<>:"/\\|?*'
        if any(char in folder_name for char in invalid_chars):
            raise ValueError(f"Folder name contains invalid characters: {invalid_chars}")
        
        if folder_name in self._metadata.get("folders", {}):
            return False  # Folder already exists
            
        # Create folder metadata
        self._metadata.setdefault("folders", {})[folder_name] = {
            "created": datetime.now().isoformat(),
            "expanded": True  # New folders start expanded
        }
        
        # Create physical directory
        folder_path = self.path_manager.sessions_dir / folder_name
        folder_path.mkdir(exist_ok=True)
        
        self._save_metadata(self._metadata)
        logger.info(f"Created folder: {folder_name}")
        return True
    
    def delete_folder(self, folder_name: str, move_sessions_to: str = None) -> bool:
        """
        Delete a folder and optionally move its sessions.
        
        Args:
            folder_name: Name of folder to delete
            move_sessions_to: Folder to move sessions to (default: Uncategorized)
            
        Returns:
            bool: True if deleted successfully
        """
        if folder_name == self.UNCATEGORIZED_FOLDER:
            raise ValueError("Cannot delete the Uncategorized folder")
            
        if folder_name not in self._metadata.get("folders", {}):
            return False  # Folder doesn't exist
            
        move_to = move_sessions_to or self.UNCATEGORIZED_FOLDER
        
        # Move all sessions from this folder
        sessions_in_folder = [
            session_id for session_id, session_folder 
            in self._metadata.get("session_folders", {}).items()
            if session_folder == folder_name
        ]
        
        for session_id in sessions_in_folder:
            self.move_session(session_id, move_to)
        
        # Remove folder metadata
        del self._metadata["folders"][folder_name]
        
        # Remove physical directory if empty
        folder_path = self.path_manager.sessions_dir / folder_name
        try:
            if folder_path.exists() and folder_path.is_dir():
                if not any(folder_path.iterdir()):  # Only delete if empty
                    folder_path.rmdir()
        except OSError as e:
            logger.warning(f"Could not remove folder directory {folder_path}: {e}")
        
        self._save_metadata(self._metadata)
        logger.info(f"Deleted folder: {folder_name}, moved {len(sessions_in_folder)} sessions to {move_to}")
        return True
    
    def rename_folder(self, old_name: str, new_name: str) -> bool:
        """
        Rename a folder.
        
        Args:
            old_name: Current folder name
            new_name: New folder name
            
        Returns:
            bool: True if renamed successfully
        """
        if old_name == self.UNCATEGORIZED_FOLDER:
            raise ValueError("Cannot rename the Uncategorized folder")
            
        if old_name not in self._metadata.get("folders", {}):
            return False  # Source folder doesn't exist
            
        if new_name in self._metadata.get("folders", {}):
            raise ValueError(f"Folder '{new_name}' already exists")
        
        new_name = new_name.strip()
        if not new_name:
            raise ValueError("New folder name cannot be empty")
        
        # Update folder metadata
        folder_data = self._metadata["folders"][old_name]
        self._metadata["folders"][new_name] = folder_data
        del self._metadata["folders"][old_name]
        
        # Update session mappings
        for session_id, folder_name in self._metadata.get("session_folders", {}).items():
            if folder_name == old_name:
                self._metadata["session_folders"][session_id] = new_name
        
        # Rename physical directory
        old_path = self.path_manager.sessions_dir / old_name
        new_path = self.path_manager.sessions_dir / new_name
        try:
            if old_path.exists():
                old_path.rename(new_path)
        except OSError as e:
            logger.warning(f"Could not rename folder directory from {old_path} to {new_path}: {e}")
        
        self._save_metadata(self._metadata)
        logger.info(f"Renamed folder: {old_name} -> {new_name}")
        return True
    
    def move_session(self, session_id: str, target_folder: str) -> bool:
        """
        Move a session to a different folder.
        
        Args:
            session_id: ID of session to move
            target_folder: Target folder name
            
        Returns:
            bool: True if moved successfully
        """
        if target_folder not in self._metadata.get("folders", {}):
            raise ValueError(f"Target folder '{target_folder}' does not exist")
        
        # Update session mapping
        self._metadata.setdefault("session_folders", {})[session_id] = target_folder
        
        # TODO: Move physical session directory when we implement nested structure
        # For now, we only update the logical mapping
        
        self._save_metadata(self._metadata)
        logger.debug(f"Moved session {session_id} to folder {target_folder}")
        return True
    
    def set_folder_expanded(self, folder_name: str, expanded: bool) -> None:
        """Set the expanded state of a folder."""
        if folder_name in self._metadata.get("folders", {}):
            self._metadata["folders"][folder_name]["expanded"] = expanded
            self._save_metadata(self._metadata)
    
    def is_folder_expanded(self, folder_name: str) -> bool:
        """Check if a folder is expanded."""
        return self._metadata.get("folders", {}).get(folder_name, {}).get("expanded", False)
    
    def get_folders_with_sessions(self, sessions: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Group sessions by folder.
        
        Args:
            sessions: List of session dictionaries
            
        Returns:
            Dict mapping folder names to lists of sessions
        """
        folders_with_sessions = {}
        
        # Initialize all folders (even empty ones)
        for folder_name in self._metadata.get("folders", {}):
            folders_with_sessions[folder_name] = []
        
        # Ensure Uncategorized folder is always present and visible
        if self.UNCATEGORIZED_FOLDER not in folders_with_sessions:
            folders_with_sessions[self.UNCATEGORIZED_FOLDER] = []
        
        # Group sessions by folder
        for session in sessions:
            session_id = session.get('id')
            folder_name = self.get_session_folder(session_id)
            
            # Ensure folder exists in results
            if folder_name not in folders_with_sessions:
                folders_with_sessions[folder_name] = []
            
            folders_with_sessions[folder_name].append(session)
        
        return folders_with_sessions
    
    def migrate_existing_sessions(self, session_ids: List[str]) -> int:
        """
        Migrate existing sessions to Uncategorized folder.
        
        Args:
            session_ids: List of session IDs to migrate
            
        Returns:
            int: Number of sessions migrated
        """
        migrated_count = 0
        
        for session_id in session_ids:
            if session_id not in self._metadata.get("session_folders", {}):
                self._metadata.setdefault("session_folders", {})[session_id] = self.UNCATEGORIZED_FOLDER
                migrated_count += 1
        
        if migrated_count > 0:
            self._save_metadata(self._metadata)
            logger.info(f"Migrated {migrated_count} sessions to {self.UNCATEGORIZED_FOLDER} folder")
        
        return migrated_count
    
    def sync_with_physical_structure(self) -> Dict[str, int]:
        """
        Synchronize folder metadata with physical directory structure.
        Detects sessions organized in physical folders and updates metadata accordingly.
        
        Returns:
            Dict with sync statistics: {
                'folders_discovered': int,
                'sessions_remapped': int,
                'folders_created': int
            }
        """
        stats = {
            'folders_discovered': 0,
            'sessions_remapped': 0,
            'folders_created': 0
        }
        
        # Get all sessions with their physical locations
        session_locations = self.path_manager.find_all_sessions()
        
        # Track discovered folders
        discovered_folders = set()
        sessions_to_remap = {}
        
        for session_id, folder_name in session_locations.items():
            if folder_name:  # Session is in a subfolder
                discovered_folders.add(folder_name)
                
                # Check if session mapping needs update
                current_folder = self.get_session_folder(session_id)
                if current_folder != folder_name:
                    sessions_to_remap[session_id] = folder_name
                    stats['sessions_remapped'] += 1
            else:  # Session is at root level
                # Check if session mapping needs update to Uncategorized
                current_folder = self.get_session_folder(session_id)
                if current_folder != self.UNCATEGORIZED_FOLDER:
                    sessions_to_remap[session_id] = self.UNCATEGORIZED_FOLDER
                    stats['sessions_remapped'] += 1
        
        stats['folders_discovered'] = len(discovered_folders)
        
        # Create missing folders in metadata
        for folder_name in discovered_folders:
            if folder_name not in self._metadata.get("folders", {}):
                self._metadata.setdefault("folders", {})[folder_name] = {
                    "created": datetime.now().isoformat(),
                    "expanded": True  # Start expanded so user can see content
                }
                stats['folders_created'] += 1
                logger.info(f"Discovered and registered physical folder: {folder_name}")
        
        # Update session mappings
        for session_id, folder_name in sessions_to_remap.items():
            self._metadata.setdefault("session_folders", {})[session_id] = folder_name
            logger.debug(f"Remapped session {session_id} to folder {folder_name}")
        
        # Save updated metadata
        if stats['folders_created'] > 0 or stats['sessions_remapped'] > 0:
            self._save_metadata(self._metadata)
            logger.info(f"Synced physical structure: {stats['folders_created']} folders created, {stats['sessions_remapped']} sessions remapped")
        
        return stats
    
    def get_folder_stats(self) -> Dict[str, Dict]:
        """Get statistics about folders and sessions."""
        return {
            "total_folders": len(self._metadata.get("folders", {})),
            "total_mapped_sessions": len(self._metadata.get("session_folders", {})),
            "folders": list(self._metadata.get("folders", {}).keys()),
            "last_modified": self._metadata.get("last_modified")
        }


# Global instance
_folder_manager = None

def get_folder_manager() -> FolderManager:
    """Get the global folder manager instance."""
    global _folder_manager
    if _folder_manager is None:
        _folder_manager = FolderManager()
    return _folder_manager