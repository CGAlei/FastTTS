#!/usr/bin/env python3
"""
Manual folder synchronization script - runs the sync logic directly
"""

import json
import os
from datetime import datetime
from pathlib import Path

def main():
    """Manually sync folders.json with physical directory structure"""
    
    # Project paths
    project_root = Path(__file__).parent
    sessions_dir = project_root / "sessions"
    folders_file = sessions_dir / "folders.json"
    
    print("=== Manual Folder Sync ===\n")
    print(f"Sessions directory: {sessions_dir}")
    print(f"Folders metadata: {folders_file}")
    print()
    
    # Load current metadata
    with open(folders_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    print("=== Current Metadata ===")
    print(f"Folders: {list(metadata.get('folders', {}).keys())}")
    session_mappings = metadata.get("session_folders", {})
    mapping_counts = {}
    for session_id, folder_name in session_mappings.items():
        mapping_counts[folder_name] = mapping_counts.get(folder_name, 0) + 1
    for folder, count in mapping_counts.items():
        print(f"  {folder}: {count} sessions")
    print()
    
    # Discover physical structure
    print("=== Physical Structure Discovery ===")
    session_locations = {}
    
    # Check root level sessions
    for item in sessions_dir.iterdir():
        if item.is_dir() and not item.name.startswith('.') and item.name != 'folders.json':
            metadata_file = item / "metadata.json"
            if metadata_file.exists():
                session_locations[item.name] = None  # Root level
                print(f"  Root level: {item.name}")
    
    # Check folder-based sessions
    physical_folders = set()
    for folder in sessions_dir.iterdir():
        if folder.is_dir() and not folder.name.startswith('.') and folder.name not in ['folders.json']:
            # Check if this folder contains sessions
            has_sessions = False
            for session_dir in folder.iterdir():
                if session_dir.is_dir():
                    metadata_file = session_dir / "metadata.json"
                    if metadata_file.exists():
                        session_locations[session_dir.name] = folder.name
                        physical_folders.add(folder.name)
                        has_sessions = True
            if has_sessions:
                print(f"  Folder '{folder.name}': found sessions")
    
    print(f"Discovered {len(physical_folders)} physical folders: {list(physical_folders)}")
    print(f"Found {len(session_locations)} total sessions")
    print()
    
    # Sync metadata
    print("=== Synchronizing Metadata ===")
    folders_created = 0
    sessions_remapped = 0
    
    # Add missing folders to metadata
    for folder_name in physical_folders:
        if folder_name not in metadata.get("folders", {}):
            metadata.setdefault("folders", {})[folder_name] = {
                "created": datetime.now().isoformat(),
                "expanded": True
            }
            folders_created += 1
            print(f"  Created folder: {folder_name}")
    
    # Update session mappings
    for session_id, physical_folder in session_locations.items():
        target_folder = physical_folder if physical_folder else "Uncategorized"
        current_folder = metadata.get("session_folders", {}).get(session_id, "Uncategorized")
        
        if current_folder != target_folder:
            metadata.setdefault("session_folders", {})[session_id] = target_folder
            sessions_remapped += 1
            print(f"  Remapped {session_id}: {current_folder} -> {target_folder}")
    
    # Update timestamp
    metadata["last_modified"] = datetime.now().isoformat()
    
    # Save updated metadata
    if folders_created > 0 or sessions_remapped > 0:
        # Create backup
        backup_file = folders_file.with_suffix('.json.backup2')
        if folders_file.exists():
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Save new metadata
        with open(folders_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"\nSync completed: {folders_created} folders created, {sessions_remapped} sessions remapped")
    else:
        print("\nNo changes needed - metadata already in sync")
    
    # Show final state
    print("\n=== Updated Metadata ===")
    print(f"Folders: {list(metadata.get('folders', {}).keys())}")
    updated_mappings = metadata.get("session_folders", {})
    updated_counts = {}
    for session_id, folder_name in updated_mappings.items():
        updated_counts[folder_name] = updated_counts.get(folder_name, 0) + 1
    for folder, count in updated_counts.items():
        print(f"  {folder}: {count} sessions")
    
    print("\n=== Ready to Test ===")
    print("The folder metadata has been synchronized. Start the FastTTS app to see the updated UI.")

if __name__ == "__main__":
    main()