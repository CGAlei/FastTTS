"""
Credentials Manager
Handles secure storage and retrieval of API credentials for TTS engines
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dotenv import load_dotenv, set_key, find_dotenv


class CredentialsManager:
    """Manages API credentials for various TTS engines"""
    
    def __init__(self, project_root: Optional[Union[str, Path]] = None):
        # Import path manager here to avoid circular imports
        from config.paths import get_path_manager
        
        if project_root:
            self.project_root = Path(project_root)
            self.env_file = self.project_root / ".env"
        else:
            path_manager = get_path_manager()
            self.project_root = path_manager.project_root
            self.env_file = path_manager.env_file
        self.credentials_cache = {}
        
        # Ensure .env file exists
        self._ensure_env_file()
        
        # Load current environment
        load_dotenv(self.env_file)
        
        # Load credentials into cache
        self._load_credentials()
    
    def _ensure_env_file(self):
        """Ensure .env file exists, create from template if needed"""
        if not self.env_file.exists():
            env_example = self.project_root / ".env.example"
            if env_example.exists():
                # Copy from .env.example
                with open(env_example, 'r') as example:
                    content = example.read()
                with open(self.env_file, 'w') as env:
                    env.write(content)
            else:
                # Create basic .env file
                self.env_file.write_text(
                    "# FastTTS Configuration\n"
                    "# MiniMax TTS API Configuration\n"
                    "MINIMAX_API_KEY=\n"
                    "MINIMAX_GROUP_ID=\n"
                    "DEFAULT_TTS_ENGINE=edge\n"
                    "DEBUG=false\n"
                )
    
    def _load_credentials(self):
        """Load credentials from environment variables into cache"""
        self.credentials_cache = {
            'minimax': {
                'api_key': os.getenv('MINIMAX_API_KEY', ''),
                'group_id': os.getenv('MINIMAX_GROUP_ID', ''),
                'custom_voice_id': os.getenv('MINIMAX_CUSTOM_VOICE_ID', ''),
                'model': os.getenv('MINIMAX_MODEL', 'speech-2.5-turbo-preview'),
                'configured': bool(os.getenv('MINIMAX_API_KEY') and os.getenv('MINIMAX_GROUP_ID'))
            },
            'edge': {
                'configured': True  # Edge TTS doesn't need credentials
            }
        }
    
    def get_credentials(self, engine: str) -> Dict[str, Any]:
        """
        Get credentials for specified TTS engine
        
        Args:
            engine: TTS engine name ('edge', 'minimax', 'hailuo')
            
        Returns:
            Dictionary with credentials and configuration status
        """
        engine_key = 'minimax' if engine in ['minimax', 'hailuo'] else engine
        return self.credentials_cache.get(engine_key, {})
    
    def set_credentials(self, engine: str, credentials: Dict[str, str]) -> Dict[str, Any]:
        """
        Set and persist credentials for specified TTS engine
        
        Args:
            engine: TTS engine name
            credentials: Dictionary with credential key-value pairs
            
        Returns:
            Result dictionary with success status and messages
        """
        try:
            if engine in ['minimax', 'hailuo']:
                return self._set_minimax_credentials(credentials)
            else:
                return {
                    'success': False,
                    'error': f'Credentials not required for {engine} engine'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to save credentials: {str(e)}'
            }
    
    def _set_minimax_credentials(self, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Set MiniMax credentials and settings"""
        api_key = credentials.get('api_key', '').strip()
        group_id = credentials.get('group_id', '').strip()
        custom_voice_id = credentials.get('custom_voice_id', '').strip()
        model = credentials.get('model', 'speech-2.5-turbo-preview').strip()
        chunk_size = credentials.get('chunk_size', 120)
        
        # Validation
        if not api_key:
            return {
                'success': False,
                'error': 'API Key is required'
            }
        
        if not group_id:
            return {
                'success': False,
                'error': 'Group ID is required'
            }
        
        # Validate custom voice ID format if provided
        if custom_voice_id and not self._validate_voice_id_format(custom_voice_id):
            return {
                'success': False,
                'error': 'Custom Voice ID format appears invalid'
            }
        
        # Validate chunk size
        try:
            chunk_size = int(chunk_size)
            if chunk_size < 50 or chunk_size > 300:
                return {
                    'success': False,
                    'error': 'Chunk size must be between 50 and 300 words'
                }
        except (ValueError, TypeError):
            chunk_size = 120  # Default fallback
        
        # Save to .env file
        try:
            set_key(str(self.env_file), 'MINIMAX_API_KEY', api_key)
            set_key(str(self.env_file), 'MINIMAX_GROUP_ID', group_id)
            set_key(str(self.env_file), 'MINIMAX_CUSTOM_VOICE_ID', custom_voice_id)
            set_key(str(self.env_file), 'MINIMAX_MODEL', model)
            set_key(str(self.env_file), 'MINIMAX_CHUNK_SIZE', str(chunk_size))
            
            # Update environment variables
            os.environ['MINIMAX_API_KEY'] = api_key
            os.environ['MINIMAX_GROUP_ID'] = group_id
            os.environ['MINIMAX_CUSTOM_VOICE_ID'] = custom_voice_id
            os.environ['MINIMAX_MODEL'] = model
            os.environ['MINIMAX_CHUNK_SIZE'] = str(chunk_size)
            
            # Update cache
            self.credentials_cache['minimax'] = {
                'api_key': api_key,
                'group_id': group_id,
                'custom_voice_id': custom_voice_id,
                'model': model,
                'chunk_size': chunk_size,
                'configured': True
            }
            
            return {
                'success': True,
                'message': 'MiniMax settings saved successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to save settings to .env file: {str(e)}'
            }
    
    def _validate_voice_id_format(self, voice_id: str) -> bool:
        """Validate MiniMax voice ID format"""
        if not voice_id:
            return True  # Empty is okay
        
        # MiniMax voice IDs typically have formats like:
        # - Standard voices: "male-qn-qingse", "female-shaonv"
        # - Custom voices: "moss_audio_4dc076ac-da6d-11ef-bd8d-f27a76fcd434"
        
        # Check for reasonable length and characters
        if len(voice_id) < 3 or len(voice_id) > 100:
            return False
        
        # Allow alphanumeric, hyphens, underscores
        import re
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, voice_id))
    
    def validate_credentials(self, engine: str) -> Dict[str, Any]:
        """
        Validate credentials for specified engine
        
        Args:
            engine: TTS engine name
            
        Returns:
            Validation result dictionary
        """
        credentials = self.get_credentials(engine)
        
        if engine in ['minimax', 'hailuo']:
            return self._validate_minimax_credentials(credentials)
        elif engine == 'edge':
            return {
                'valid': True,
                'message': 'Edge TTS does not require credentials'
            }
        else:
            return {
                'valid': False,
                'error': f'Unknown engine: {engine}'
            }
    
    def _validate_minimax_credentials(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Validate MiniMax credentials and settings"""
        api_key = credentials.get('api_key', '')
        group_id = credentials.get('group_id', '')
        custom_voice_id = credentials.get('custom_voice_id', '')
        model = credentials.get('model', 'speech-2.5-turbo-preview')
        
        if not api_key or not group_id:
            return {
                'valid': False,
                'error': 'API Key and Group ID are required',
                'missing_fields': [
                    field for field, value in [
                        ('api_key', api_key),
                        ('group_id', group_id)
                    ] if not value
                ]
            }
        
        # Basic format validation
        if len(api_key) < 10:
            return {
                'valid': False,
                'error': 'API Key appears to be too short'
            }
        
        if len(group_id) < 5:
            return {
                'valid': False,
                'error': 'Group ID appears to be too short'
            }
        
        # Validate custom voice ID if provided
        if custom_voice_id and not self._validate_voice_id_format(custom_voice_id):
            return {
                'valid': False,
                'error': 'Custom Voice ID format is invalid'
            }
        
        # Validate model selection
        valid_models = ['speech-2.5-turbo-preview', 'speech-02-hd', 'speech-01-turbo', 'speech-01-hd']
        if model not in valid_models:
            return {
                'valid': False,
                'error': f'Invalid model selection. Must be one of: {", ".join(valid_models)}'
            }
        
        return {
            'valid': True,
            'message': 'Settings appear valid (format check only)',
            'has_custom_voice': bool(custom_voice_id),
            'selected_model': model
        }
    
    def get_all_engine_status(self) -> Dict[str, Dict[str, Any]]:
        """Get configuration status for all TTS engines"""
        return {
            'edge': {
                'name': 'Microsoft Edge TTS',
                'configured': True,
                'requires_credentials': False
            },
            'hailuo': {
                'name': 'MiniMax Hailuo TTS',
                'configured': self.credentials_cache.get('minimax', {}).get('configured', False),
                'requires_credentials': True,
                'credentials': {
                    'api_key': bool(self.credentials_cache.get('minimax', {}).get('api_key')),
                    'group_id': bool(self.credentials_cache.get('minimax', {}).get('group_id'))
                },
                'model': self.credentials_cache.get('minimax', {}).get('model', 'speech-2.5-turbo-preview'),
                'custom_voice_id': self.credentials_cache.get('minimax', {}).get('custom_voice_id', ''),
                'chunk_size': self.credentials_cache.get('minimax', {}).get('chunk_size', 120)
            }
        }
    
    def clear_credentials(self, engine: str) -> Dict[str, Any]:
        """
        Clear credentials for specified engine
        
        Args:
            engine: TTS engine name
            
        Returns:
            Result dictionary
        """
        try:
            if engine in ['minimax', 'hailuo']:
                # Clear from .env file
                set_key(str(self.env_file), 'MINIMAX_API_KEY', '')
                set_key(str(self.env_file), 'MINIMAX_GROUP_ID', '')
                set_key(str(self.env_file), 'MINIMAX_CUSTOM_VOICE_ID', '')
                set_key(str(self.env_file), 'MINIMAX_MODEL', 'speech-2.5-turbo-preview')
                
                # Clear from environment
                os.environ.pop('MINIMAX_API_KEY', None)
                os.environ.pop('MINIMAX_GROUP_ID', None)
                os.environ.pop('MINIMAX_CUSTOM_VOICE_ID', None)
                os.environ['MINIMAX_MODEL'] = 'speech-2.5-turbo-preview'
                
                # Update cache
                self.credentials_cache['minimax'] = {
                    'api_key': '',
                    'group_id': '',
                    'custom_voice_id': '',
                    'model': 'speech-2.5-turbo-preview',
                    'configured': False
                }
                
                return {
                    'success': True,
                    'message': 'MiniMax settings cleared'
                }
            else:
                return {
                    'success': False,
                    'error': f'Cannot clear credentials for {engine} engine'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to clear credentials: {str(e)}'
            }