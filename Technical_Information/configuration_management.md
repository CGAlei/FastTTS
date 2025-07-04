# FastTTS Configuration Management Guide

## 📋 Configuration Overview

FastTTS employs a comprehensive configuration management system that handles environment variables, default settings, path management, and credentials across multiple services and engines. The system is designed for flexibility, security, and ease of deployment across different environments.

**Configuration Sources**: Environment variables, defaults.py, credentials manager  
**Scope**: TTS engines, AI services, paths, application settings  
**Security**: Secure credential storage and validation  
**Environment Support**: Development, production, testing environments  

---

## 🏗️ Configuration Architecture

### **Configuration Hierarchy**
```
Environment Variables (.env file)
    ↓
Configuration Modules (config/)
    ↓  
Runtime Settings (localStorage + server state)
    ↓
Default Values (fallback)
```

### **Configuration Modules Structure**
```
config/
├── __init__.py                 # Module initialization and exports
├── defaults.py                 # Default values and constants
├── paths.py                    # Path management and directories
└── credentials_manager.py      # Secure credential handling
```

---

## 🔧 Environment Variables (`/.env`)

### **Core Application Settings**
```bash
# === Application Core ===
FASTTTS_LOG_LEVEL=INFO                    # Logging verbosity (DEBUG, INFO, WARN, ERROR)
FASTTTS_LOG_DIR=logs                      # Log directory path (relative or absolute)
FASTTTS_DEFAULT_VOICE=zh-CN-XiaoxiaoNeural # Default TTS voice
FASTTTS_DEFAULT_TEXT=就像心里起的小波浪，是你突然想到的念头  # Default text content

# === Database Configuration ===
FASTTTS_DB_PATH=db/vocab.db               # Vocabulary database path
FASTTTS_SESSION_DIR=sessions              # Session storage directory

# === AI/LLM Services ===
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# === MiniMax TTS Configuration ===
MINIMAX_API_KEY=your_minimax_api_key_here
MINIMAX_GROUP_ID=your_group_id_here
MINIMAX_MODEL=speech-02-turbo             # TTS model selection
MINIMAX_CHUNK_SIZE=120                    # Text chunking size (words)
MINIMAX_CUSTOM_VOICE_ID=                  # Optional custom voice ID

# === Development Settings ===
FASTTTS_DEBUG=false                       # Enable debug mode
FASTTTS_HOST=0.0.0.0                     # Server bind address
FASTTTS_PORT=8000                        # Server port
```

### **Environment File Template** (`.env.example`)
```bash
# FastTTS Configuration Template
# Copy this file to .env and configure your settings

# === Required: AI Services ===
# Get your OpenRouter API key from: https://openrouter.ai/
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Get your OpenAI API key from: https://platform.openai.com/
OPENAI_API_KEY=your_openai_api_key_here

# === Optional: MiniMax TTS (for custom voices) ===
# Get your MiniMax credentials from: https://platform.minimax.co/
MINIMAX_API_KEY=your_minimax_api_key_here
MINIMAX_GROUP_ID=your_group_id_here

# === Application Settings (with defaults) ===
FASTTTS_LOG_LEVEL=INFO
FASTTTS_DEFAULT_VOICE=zh-CN-XiaoxiaoNeural
MINIMAX_MODEL=speech-02-turbo
MINIMAX_CHUNK_SIZE=120

# === Development (optional) ===
FASTTTS_DEBUG=false
FASTTTS_HOST=0.0.0.0
FASTTTS_PORT=8000
```

---

## ⚙️ Default Configuration (`config/defaults.py`)

### **Application Defaults**
```python
"""
Default configuration values for FastTTS application
These values are used as fallbacks when environment variables are not set
"""

import os
from pathlib import Path

# === Audio and TTS Defaults ===
DEFAULT_VOLUME = 1.0                      # Audio volume level (0.0-2.0)
DEFAULT_SPEED = 1.0                       # Speech speed multiplier (0.5-2.0)  
DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"    # Microsoft Edge TTS default voice
DEFAULT_ENGINE = "edge"                   # Default TTS engine (edge|hailuo)
DEFAULT_VOLUME_DISPLAY = "100%"          # Volume display format

# === Text Processing Defaults ===
DEFAULT_TEXT = "就像心里起的小波浪，是你突然想到的念头"  # Demo text content
MAX_TEXT_LENGTH = 10000                   # Maximum input text length
DEFAULT_CHUNK_SIZE = 120                  # Words per chunk for long texts

# === AI/LLM Defaults ===
DEFAULT_AI_MODEL = "gpt-4o-mini"          # Default AI model for definitions
AI_REQUEST_TIMEOUT = 30                   # AI request timeout (seconds)
AI_MAX_RETRIES = 2                        # Maximum retry attempts

# === Session Management Defaults ===
DEFAULT_SESSION_RETENTION_DAYS = 30      # Session cleanup after N days
MAX_SESSIONS_PER_USER = 1000             # Maximum stored sessions
SESSION_METADATA_VERSION = "1.0"         # Metadata format version

# === UI/Frontend Defaults ===
DEFAULT_THEME = "default"                 # UI theme (default|dark-mode|high-contrast)
DEFAULT_FONT_SIZE = "medium"              # Text size (small|medium|large|xlarge)
DEFAULT_AUTO_HIDE_DELAY = 3000           # UI auto-hide delay (milliseconds)

# === Logging Defaults ===
DEFAULT_LOG_LEVEL = "INFO"                # Logging level
DEFAULT_LOG_RETENTION_DAYS = 10          # Log file retention
DEFAULT_LOG_MAX_SIZE = "10MB"            # Maximum log file size

# === Performance Defaults ===
DEFAULT_CACHE_SIZE = 100 * 1024 * 1024   # Audio cache size (100MB)
DEFAULT_DB_CONNECTION_POOL = 5           # Database connection pool size
DEFAULT_CONCURRENT_TTS = 3               # Max concurrent TTS requests

def get_default_config() -> dict:
    """Get complete default configuration dictionary"""
    return {
        # Audio/TTS
        'volume': DEFAULT_VOLUME,
        'speed': DEFAULT_SPEED,
        'voice': DEFAULT_VOICE,
        'engine': DEFAULT_ENGINE,
        'chunk_size': DEFAULT_CHUNK_SIZE,
        
        # AI/LLM
        'ai_model': DEFAULT_AI_MODEL,
        'ai_timeout': AI_REQUEST_TIMEOUT,
        'ai_max_retries': AI_MAX_RETRIES,
        
        # UI/UX
        'theme': DEFAULT_THEME,
        'font_size': DEFAULT_FONT_SIZE,
        'auto_hide_delay': DEFAULT_AUTO_HIDE_DELAY,
        
        # Performance
        'cache_size': DEFAULT_CACHE_SIZE,
        'db_pool_size': DEFAULT_DB_CONNECTION_POOL,
        'max_concurrent_tts': DEFAULT_CONCURRENT_TTS,
        
        # Logging
        'log_level': DEFAULT_LOG_LEVEL,
        'log_retention': DEFAULT_LOG_RETENTION_DAYS
    }

def get_env_or_default(key: str, default_value):
    """Get environment variable with typed default fallback"""
    env_value = os.getenv(key)
    
    if env_value is None:
        return default_value
    
    # Type conversion based on default value type
    if isinstance(default_value, bool):
        return env_value.lower() in ('true', '1', 'yes', 'on')
    elif isinstance(default_value, int):
        try:
            return int(env_value)
        except ValueError:
            return default_value
    elif isinstance(default_value, float):
        try:
            return float(env_value)
        except ValueError:
            return default_value
    else:
        return env_value

# === Computed Configuration ===
# These values are computed at runtime based on environment

def get_current_config():
    """Get current configuration with environment overrides"""
    return {
        'volume': get_env_or_default('FASTTTS_DEFAULT_VOLUME', DEFAULT_VOLUME),
        'speed': get_env_or_default('FASTTTS_DEFAULT_SPEED', DEFAULT_SPEED),
        'voice': get_env_or_default('FASTTTS_DEFAULT_VOICE', DEFAULT_VOICE),
        'engine': get_env_or_default('FASTTTS_DEFAULT_ENGINE', DEFAULT_ENGINE),
        'text': get_env_or_default('FASTTTS_DEFAULT_TEXT', DEFAULT_TEXT),
        'log_level': get_env_or_default('FASTTTS_LOG_LEVEL', DEFAULT_LOG_LEVEL),
        'debug': get_env_or_default('FASTTTS_DEBUG', False),
        'host': get_env_or_default('FASTTTS_HOST', '0.0.0.0'),
        'port': get_env_or_default('FASTTTS_PORT', 8000)
    }
```

---

## 📁 Path Management (`config/paths.py`)

### **Centralized Path Configuration**
```python
"""
Centralized path management for FastTTS application
Handles cross-platform path resolution and directory creation
"""

import os
from pathlib import Path
from typing import Optional

class PathManager:
    """Centralized manager for all application paths"""
    
    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize path manager with configurable base directory"""
        if base_dir is None:
            # Use the directory containing main.py as base
            self.base_dir = Path(__file__).parent.parent
        else:
            self.base_dir = Path(base_dir)
        
        # Ensure base directory exists
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize core paths
        self._init_core_paths()
    
    def _init_core_paths(self):
        """Initialize core application paths"""
        # Database paths
        self.db_dir = self._resolve_path(os.getenv('FASTTTS_DB_DIR', 'db'))
        self.vocab_db_path = self.db_dir / 'vocab.db'
        
        # Session storage
        self.sessions_dir = self._resolve_path(os.getenv('FASTTTS_SESSION_DIR', 'sessions'))
        self.session_metadata_file = self.sessions_dir / 'session_metadata.json'
        
        # Logging
        self.log_dir = self._resolve_path(os.getenv('FASTTTS_LOG_DIR', 'logs'))
        self.app_log_file = self.log_dir / 'fasttts.log'
        self.error_log_file = self.log_dir / 'error.log'
        
        # Static assets
        self.static_dir = self.base_dir / 'static'
        self.css_dir = self.static_dir / 'css'
        self.js_dir = self.static_dir / 'js'
        
        # Templates (if using separate template directory)
        self.templates_dir = self.base_dir / 'templates'
        
        # Temporary files
        self.temp_dir = self._resolve_path(os.getenv('FASTTTS_TEMP_DIR', 'temp'))
        
        # Cache directory
        self.cache_dir = self._resolve_path(os.getenv('FASTTTS_CACHE_DIR', 'cache'))
        
        # Configuration
        self.config_dir = self.base_dir / 'config'
        
        # Create all necessary directories
        self._create_directories()
    
    def _resolve_path(self, path_str: str) -> Path:
        """Resolve path string to absolute Path object"""
        path = Path(path_str)
        
        if path.is_absolute():
            return path
        else:
            return self.base_dir / path
    
    def _create_directories(self):
        """Create all necessary directories if they don't exist"""
        directories = [
            self.db_dir,
            self.sessions_dir,
            self.log_dir,
            self.temp_dir,
            self.cache_dir,
            self.static_dir,
            self.css_dir,
            self.js_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_session_dir(self, session_id: str) -> Path:
        """Get path for specific session directory"""
        session_path = self.sessions_dir / session_id
        session_path.mkdir(parents=True, exist_ok=True)
        return session_path
    
    def get_temp_file(self, filename: str) -> Path:
        """Get path for temporary file"""
        return self.temp_dir / filename
    
    def get_cache_file(self, filename: str) -> Path:
        """Get path for cache file"""
        return self.cache_dir / filename
    
    def get_log_file(self, log_type: str = 'app') -> Path:
        """Get path for specific log file"""
        log_files = {
            'app': self.app_log_file,
            'error': self.error_log_file
        }
        return log_files.get(log_type, self.app_log_file)
    
    def cleanup_temp_files(self, max_age_hours: int = 24):
        """Clean up old temporary files"""
        import time
        current_time = time.time()
        cutoff_time = current_time - (max_age_hours * 3600)
        
        for temp_file in self.temp_dir.iterdir():
            if temp_file.is_file() and temp_file.stat().st_mtime < cutoff_time:
                try:
                    temp_file.unlink()
                except OSError:
                    pass  # File might be in use
    
    def get_directory_info(self) -> dict:
        """Get information about all managed directories"""
        return {
            'base_dir': str(self.base_dir),
            'db_dir': str(self.db_dir),
            'sessions_dir': str(self.sessions_dir),
            'log_dir': str(self.log_dir),
            'static_dir': str(self.static_dir),
            'temp_dir': str(self.temp_dir),
            'cache_dir': str(self.cache_dir),
            'config_dir': str(self.config_dir)
        }

# Singleton instance
_path_manager = None

def get_path_manager() -> PathManager:
    """Get singleton PathManager instance"""
    global _path_manager
    if _path_manager is None:
        _path_manager = PathManager()
    return _path_manager

def reset_path_manager(base_dir: Optional[Path] = None):
    """Reset path manager with new base directory (for testing)"""
    global _path_manager
    _path_manager = PathManager(base_dir)
    return _path_manager
```

---

## 🔐 Credentials Management (`config/credentials_manager.py`)

### **Secure Credential Handling**
```python
"""
Secure credentials management for TTS engines and AI services
Handles API key storage, validation, and configuration persistence
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv, set_key

logger = logging.getLogger(__name__)

class CredentialsManager:
    """Secure manager for API credentials and engine configurations"""
    
    def __init__(self):
        """Initialize credentials manager with environment loading"""
        # Load environment variables
        load_dotenv()
        
        # Supported engines and their credential requirements
        self.engine_requirements = {
            'minimax': {
                'required_fields': ['api_key', 'group_id'],
                'optional_fields': ['model', 'custom_voice_id', 'chunk_size'],
                'env_mapping': {
                    'api_key': 'MINIMAX_API_KEY',
                    'group_id': 'MINIMAX_GROUP_ID',
                    'model': 'MINIMAX_MODEL',
                    'custom_voice_id': 'MINIMAX_CUSTOM_VOICE_ID',
                    'chunk_size': 'MINIMAX_CHUNK_SIZE'
                }
            },
            'openai': {
                'required_fields': ['api_key'],
                'optional_fields': ['model', 'organization'],
                'env_mapping': {
                    'api_key': 'OPENAI_API_KEY',
                    'model': 'OPENAI_MODEL',
                    'organization': 'OPENAI_ORGANIZATION'
                }
            },
            'openrouter': {
                'required_fields': ['api_key'],
                'optional_fields': ['model', 'app_name'],
                'env_mapping': {
                    'api_key': 'OPENROUTER_API_KEY',
                    'model': 'OPENROUTER_MODEL',
                    'app_name': 'OPENROUTER_APP_NAME'
                }
            }
        }
    
    def get_credentials(self, engine: str) -> Dict[str, Any]:
        """Get credentials for specified engine"""
        if engine not in self.engine_requirements:
            logger.warning(f"Unknown engine: {engine}")
            return {}
        
        requirements = self.engine_requirements[engine]
        credentials = {}
        
        # Load credentials from environment variables
        for field, env_var in requirements['env_mapping'].items():
            value = os.getenv(env_var)
            if value and value != f'your_{field}_here':
                # Type conversion for specific fields
                if field == 'chunk_size':
                    try:
                        credentials[field] = int(value)
                    except ValueError:
                        credentials[field] = 120  # Default
                else:
                    credentials[field] = value
        
        # Add default values for missing optional fields
        defaults = {
            'minimax': {
                'model': 'speech-02-turbo',
                'chunk_size': 120,
                'custom_voice_id': ''
            },
            'openai': {
                'model': 'gpt-4o-mini',
                'organization': ''
            },
            'openrouter': {
                'model': 'gpt-4o-mini',
                'app_name': 'FastTTS'
            }
        }
        
        if engine in defaults:
            for field, default_value in defaults[engine].items():
                if field not in credentials:
                    credentials[field] = default_value
        
        return credentials
    
    def set_credentials(self, engine: str, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Set and validate credentials for specified engine"""
        try:
            if engine not in self.engine_requirements:
                return {
                    'success': False,
                    'error': f'Unknown engine: {engine}'
                }
            
            requirements = self.engine_requirements[engine]
            
            # Validate required fields
            missing_fields = []
            for field in requirements['required_fields']:
                if field not in credentials or not credentials[field]:
                    missing_fields.append(field)
            
            if missing_fields:
                return {
                    'success': False,
                    'error': f'Missing required fields: {missing_fields}'
                }
            
            # Update environment variables
            env_file = Path('.env')
            
            for field, value in credentials.items():
                if field in requirements['env_mapping']:
                    env_var = requirements['env_mapping'][field]
                    
                    # Update .env file
                    if env_file.exists():
                        set_key(str(env_file), env_var, str(value))
                    
                    # Update current environment
                    os.environ[env_var] = str(value)
            
            # Validate credentials with actual service
            validation_result = self._validate_engine_credentials(engine, credentials)
            
            if validation_result['valid']:
                logger.info(f"Successfully configured {engine} credentials")
                return {
                    'success': True,
                    'message': f'{engine} credentials configured successfully',
                    'validation': validation_result
                }
            else:
                logger.error(f"Credential validation failed for {engine}: {validation_result.get('error')}")
                return {
                    'success': False,
                    'error': f'Credential validation failed: {validation_result.get("error")}'
                }
        
        except Exception as e:
            logger.error(f"Error setting credentials for {engine}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _validate_engine_credentials(self, engine: str, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Validate credentials by testing actual service connection"""
        try:
            if engine == 'minimax':
                return self._validate_minimax_credentials(credentials)
            elif engine == 'openai':
                return self._validate_openai_credentials(credentials)
            elif engine == 'openrouter':
                return self._validate_openrouter_credentials(credentials)
            else:
                return {'valid': False, 'error': f'Unknown engine: {engine}'}
        
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def _validate_minimax_credentials(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Validate MiniMax API credentials"""
        import requests
        
        try:
            headers = {
                'Authorization': f'Bearer {credentials["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            # Test with a simple request
            response = requests.get(
                'https://api.minimax.io/v1/text2speech/models',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return {'valid': True, 'message': 'MiniMax credentials valid'}
            elif response.status_code == 401:
                return {'valid': False, 'error': 'Invalid API key or unauthorized'}
            else:
                return {'valid': False, 'error': f'API returned status {response.status_code}'}
        
        except requests.RequestException as e:
            return {'valid': False, 'error': f'Connection failed: {e}'}
    
    def _validate_openai_credentials(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Validate OpenAI API credentials"""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=credentials['api_key'])
            
            # Test with models list
            models = client.models.list()
            
            return {'valid': True, 'message': 'OpenAI credentials valid'}
        
        except Exception as e:
            error_msg = str(e)
            if 'authentication' in error_msg.lower() or 'api key' in error_msg.lower():
                return {'valid': False, 'error': 'Invalid API key'}
            else:
                return {'valid': False, 'error': f'Validation failed: {error_msg}'}
    
    def _validate_openrouter_credentials(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Validate OpenRouter API credentials"""
        import requests
        
        try:
            headers = {
                'Authorization': f'Bearer {credentials["api_key"]}',
                'HTTP-Referer': 'https://github.com/your-username/fasttts',
                'X-Title': 'FastTTS'
            }
            
            response = requests.get(
                'https://openrouter.ai/api/v1/models',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return {'valid': True, 'message': 'OpenRouter credentials valid'}
            elif response.status_code == 401:
                return {'valid': False, 'error': 'Invalid API key or unauthorized'}
            else:
                return {'valid': False, 'error': f'API returned status {response.status_code}'}
        
        except requests.RequestException as e:
            return {'valid': False, 'error': f'Connection failed: {e}'}
    
    def validate_credentials(self, engine: str) -> Dict[str, Any]:
        """Validate existing credentials for engine"""
        credentials = self.get_credentials(engine)
        
        if not credentials:
            return {'valid': False, 'error': 'No credentials configured'}
        
        return self._validate_engine_credentials(engine, credentials)
    
    def get_all_engine_status(self) -> Dict[str, Dict[str, Any]]:
        """Get configuration and validation status for all engines"""
        status = {}
        
        for engine in self.engine_requirements.keys():
            credentials = self.get_credentials(engine)
            requirements = self.engine_requirements[engine]
            
            # Check if required fields are present
            has_required_fields = all(
                credentials.get(field) for field in requirements['required_fields']
            )
            
            status[engine] = {
                'configured': has_required_fields,
                'credentials_present': bool(credentials),
                'required_fields': requirements['required_fields'],
                'optional_fields': requirements['optional_fields']
            }
            
            # Add validation status if configured
            if has_required_fields:
                validation = self.validate_credentials(engine)
                status[engine]['validation'] = validation
        
        return status
    
    def clear_credentials(self, engine: str) -> Dict[str, Any]:
        """Clear credentials for specified engine"""
        try:
            if engine not in self.engine_requirements:
                return {'success': False, 'error': f'Unknown engine: {engine}'}
            
            requirements = self.engine_requirements[engine]
            env_file = Path('.env')
            
            # Clear environment variables
            for field in requirements['env_mapping'].values():
                if field in os.environ:
                    del os.environ[field]
                
                # Update .env file
                if env_file.exists():
                    set_key(str(env_file), field, '')
            
            logger.info(f"Cleared credentials for {engine}")
            return {'success': True, 'message': f'Credentials cleared for {engine}'}
        
        except Exception as e:
            logger.error(f"Error clearing credentials for {engine}: {e}")
            return {'success': False, 'error': str(e)}
```

---

## 🎛️ Runtime Configuration Management

### **Settings Integration** (`main.py` integration)
```python
# Runtime configuration loading in main.py
from config.defaults import get_current_config
from config.paths import get_path_manager
from config.credentials_manager import CredentialsManager

# Initialize configuration managers
path_manager = get_path_manager()
credentials_manager = CredentialsManager()
current_config = get_current_config()

# Use configuration values
DEFAULT_VOICE = current_config['voice']
DEFAULT_TEXT = current_config['text']
```

### **Frontend Settings Persistence** (`localStorage`)
```javascript
// Frontend configuration management
class SettingsManager {
    constructor() {
        this.storagePrefix = 'fasttts_';
        this.settings = this.loadSettings();
    }
    
    loadSettings() {
        return {
            selectedVoice: localStorage.getItem(`${this.storagePrefix}voice`) || 'zh-CN-XiaoxiaoNeural',
            speechSpeed: parseFloat(localStorage.getItem(`${this.storagePrefix}speed`)) || 1.0,
            audioVolume: parseFloat(localStorage.getItem(`${this.storagePrefix}volume`)) || 1.0,
            ttsEngine: localStorage.getItem(`${this.storagePrefix}engine`) || 'edge',
            theme: localStorage.getItem(`${this.storagePrefix}theme`) || 'default',
            fontSize: localStorage.getItem(`${this.storagePrefix}fontSize`) || 'medium',
            autoHideDelay: parseInt(localStorage.getItem(`${this.storagePrefix}autoHideDelay`)) || 3000
        };
    }
    
    saveSetting(key, value) {
        this.settings[key] = value;
        localStorage.setItem(`${this.storagePrefix}${key}`, value);
    }
    
    getSetting(key) {
        return this.settings[key];
    }
    
    exportSettings() {
        return JSON.stringify(this.settings, null, 2);
    }
    
    importSettings(settingsJson) {
        try {
            const imported = JSON.parse(settingsJson);
            Object.assign(this.settings, imported);
            
            // Save all to localStorage
            for (const [key, value] of Object.entries(this.settings)) {
                localStorage.setItem(`${this.storagePrefix}${key}`, value);
            }
            
            return { success: true };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }
}
```

---

## 🔄 Configuration Validation and Testing

### **Configuration Validator**
```python
class ConfigValidator:
    """Comprehensive configuration validation"""
    
    def __init__(self):
        self.validation_results = {}
    
    def validate_all(self) -> Dict[str, Any]:
        """Validate entire configuration"""
        results = {
            'paths': self.validate_paths(),
            'credentials': self.validate_credentials(),
            'environment': self.validate_environment(),
            'dependencies': self.validate_dependencies()
        }
        
        results['overall_status'] = all(
            result.get('valid', False) for result in results.values()
        )
        
        return results
    
    def validate_paths(self) -> Dict[str, Any]:
        """Validate all path configurations"""
        path_manager = get_path_manager()
        
        issues = []
        
        # Check directory existence and permissions
        directories = [
            ('database', path_manager.db_dir),
            ('sessions', path_manager.sessions_dir),
            ('logs', path_manager.log_dir),
            ('temp', path_manager.temp_dir),
            ('cache', path_manager.cache_dir)
        ]
        
        for name, directory in directories:
            if not directory.exists():
                issues.append(f"{name} directory does not exist: {directory}")
            elif not os.access(directory, os.W_OK):
                issues.append(f"{name} directory is not writable: {directory}")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'directories_checked': len(directories)
        }
    
    def validate_credentials(self) -> Dict[str, Any]:
        """Validate all configured credentials"""
        credentials_manager = CredentialsManager()
        engine_status = credentials_manager.get_all_engine_status()
        
        valid_engines = 0
        total_engines = len(engine_status)
        issues = []
        
        for engine, status in engine_status.items():
            if status['configured']:
                if status.get('validation', {}).get('valid', False):
                    valid_engines += 1
                else:
                    error = status.get('validation', {}).get('error', 'Unknown error')
                    issues.append(f"{engine}: {error}")
        
        return {
            'valid': valid_engines > 0,  # At least one engine should work
            'valid_engines': valid_engines,
            'total_engines': total_engines,
            'issues': issues
        }
    
    def validate_environment(self) -> Dict[str, Any]:
        """Validate environment variables and settings"""
        config = get_current_config()
        issues = []
        
        # Check critical environment variables
        critical_vars = ['OPENROUTER_API_KEY', 'OPENAI_API_KEY']
        has_ai_service = any(os.getenv(var) for var in critical_vars)
        
        if not has_ai_service:
            issues.append("No AI service configured (OpenRouter or OpenAI)")
        
        # Validate numeric ranges
        if not 0.5 <= config['speed'] <= 2.0:
            issues.append(f"Invalid speed value: {config['speed']} (must be 0.5-2.0)")
        
        if not 0.0 <= config['volume'] <= 2.0:
            issues.append(f"Invalid volume value: {config['volume']} (must be 0.0-2.0)")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'has_ai_service': has_ai_service
        }
    
    def validate_dependencies(self) -> Dict[str, Any]:
        """Validate required dependencies"""
        required_modules = [
            'fasthtml',
            'edge_tts',
            'openai',
            'requests',
            'sqlite3',
            'pathlib'
        ]
        
        missing_modules = []
        
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)
        
        return {
            'valid': len(missing_modules) == 0,
            'missing_modules': missing_modules,
            'total_checked': len(required_modules)
        }
```

---

## 📊 Configuration Monitoring and Health Checks

### **Health Check Endpoint**
```python
@rt("/health-check")
def health_check():
    """Comprehensive system health check"""
    validator = ConfigValidator()
    health_status = validator.validate_all()
    
    return {
        'status': 'healthy' if health_status['overall_status'] else 'unhealthy',
        'timestamp': datetime.now().isoformat(),
        'details': health_status
    }

@rt("/config-status")
def get_config_status():
    """Get current configuration status"""
    path_manager = get_path_manager()
    credentials_manager = CredentialsManager()
    
    return {
        'paths': path_manager.get_directory_info(),
        'credentials': credentials_manager.get_all_engine_status(),
        'environment': get_current_config(),
        'defaults': get_default_config()
    }
```

---

## 🔧 Development and Deployment Configuration

### **Development Environment Setup**
```bash
# Development environment (.env.development)
FASTTTS_DEBUG=true
FASTTTS_LOG_LEVEL=DEBUG
FASTTTS_HOST=127.0.0.1
FASTTTS_PORT=8000

# Use development database
FASTTTS_DB_PATH=db/vocab_dev.db
FASTTTS_SESSION_DIR=sessions_dev

# Development AI keys (with lower rate limits)
OPENROUTER_API_KEY=dev_openrouter_key
OPENAI_API_KEY=dev_openai_key
```

### **Production Environment Setup**
```bash
# Production environment (.env.production)
FASTTTS_DEBUG=false
FASTTTS_LOG_LEVEL=INFO
FASTTTS_HOST=0.0.0.0
FASTTTS_PORT=8000

# Production paths
FASTTTS_DB_PATH=/app/data/vocab.db
FASTTTS_SESSION_DIR=/app/data/sessions
FASTTTS_LOG_DIR=/app/logs

# Production AI keys
OPENROUTER_API_KEY=prod_openrouter_key
OPENAI_API_KEY=prod_openai_key
MINIMAX_API_KEY=prod_minimax_key
MINIMAX_GROUP_ID=prod_group_id
```

### **Docker Configuration**
```dockerfile
# Environment configuration in Dockerfile
ENV FASTTTS_LOG_LEVEL=INFO
ENV FASTTTS_HOST=0.0.0.0
ENV FASTTTS_PORT=8000
ENV FASTTTS_DB_PATH=/app/data/vocab.db
ENV FASTTTS_SESSION_DIR=/app/data/sessions
ENV FASTTTS_LOG_DIR=/app/logs

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/cache /app/temp

# Copy environment file
COPY .env.production /app/.env
```

---

*This comprehensive configuration management guide provides complete documentation for AI coding assistants working with FastTTS configuration systems, enabling proper setup, validation, and maintenance across different environments.*