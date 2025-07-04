# FastTTS Core Functions Reference

## 📋 Function Catalog Overview

This reference provides a comprehensive catalog of core functions in the FastTTS application, organized by module and functionality. Each function includes its location, purpose, parameters, and return values to help AI coding assistants quickly understand and work with the codebase.

---

## 🚀 Main Application Functions (`main.py`)

### **Setup and Configuration Functions**

#### `setup_logging()` - `main.py:27`
- **Purpose**: Configure enhanced logging system with file rotation and multiple handlers
- **Parameters**: None
- **Returns**: `logging.Logger` - Configured logger instance
- **Features**: 
  - Console handler for development
  - Rotating file handlers (fasttts.log, error.log)
  - Daily rotation with 10-day retention
  - Environment-configurable log levels

#### `get_session_metadata()` - `main.py:218`
- **Purpose**: Load session metadata from JSON file with error handling
- **Parameters**: None
- **Returns**: `dict` - Session metadata dictionary or empty dict on error
- **File**: `session_metadata.json` in sessions directory

#### `save_session_metadata(metadata_dict)` - `main.py:229`
- **Purpose**: Atomic save of session metadata to JSON file
- **Parameters**: `metadata_dict: dict` - Complete metadata dictionary
- **Returns**: None (raises IOError on failure)
- **Features**: Atomic operations using temporary files

#### `update_session_metadata(session_id, **updates)` - `main.py:248`
- **Purpose**: Update metadata for specific session with automatic timestamps
- **Parameters**: 
  - `session_id: str` - Session identifier
  - `**updates` - Key-value pairs to update
- **Returns**: `dict` - Updated session metadata
- **Auto-creates**: Missing session entries with defaults

### **Session Management Functions**

#### `get_sessions()` - `main.py:268`
- **Purpose**: Retrieve all saved sessions with complete metadata
- **Parameters**: None
- **Returns**: `list[dict]` - List of session objects with UI metadata
- **Format**: `{'id', 'text', 'date', 'is_favorite', 'custom_name'}`
- **Sorting**: Reverse chronological order (newest first)

#### `render_session_list(sessions, filter_params=None, current_session_id=None)` - `main.py:305`
- **Purpose**: Generate HTML for session list with interactive elements
- **Parameters**:
  - `sessions: list` - Session data from get_sessions()
  - `filter_params: dict` - Optional filtering parameters
  - `current_session_id: str` - Currently active session ID
- **Returns**: `fasthtml.Div` - Complete HTML structure for session list
- **Features**: HTMX integration, favorite buttons, edit/delete controls

### **TTS Generation Functions**

#### `_generate_tts_response(text, voice, speed, volume, engine)` - `main.py:1223`
- **Purpose**: Core TTS generation with engine abstraction
- **Parameters**:
  - `text: str` - Preprocessed Chinese text
  - `voice: str` - Voice identifier (default: DEFAULT_VOICE)
  - `speed: float` - Speech speed multiplier (0.5-2.0)
  - `volume: float` - Audio volume level (0.0-2.0)
  - `engine: str` - TTS engine name ('edge' or 'hailuo')
- **Returns**: `fasthtml.Div` - Complete audio player with timing data
- **Features**: Error handling, progress tracking, base64 audio encoding

### **Word Interaction Functions**

#### `word_interaction(request)` - `main.py:1270`
- **Purpose**: Handle frontend word click events with vocabulary lookup
- **Parameters**: `request` - FastAPI request with JSON payload
- **Returns**: `dict` - Action response for frontend processing
- **Actions**: 
  - `left-click`: Play audio segment or show vocabulary
  - `right-click`: Show translation popup or vocabulary info
  - `hover-enter`: Subtle highlight effect
- **Integration**: Google Translate API, vocabulary database lookup

#### `define_word(request)` - `main.py:1367`
- **Purpose**: AI-powered definition generation and database insertion
- **Parameters**: `request` - JSON with word, wordId, currentSessionId
- **Returns**: `JSONResponse` - Success/error status with vocabulary data
- **Features**: 
  - Dual LLM provider support (OpenRouter/OpenAI)
  - Automatic database insertion
  - Background session updates
  - Error fallback handling

---

## 🗄️ Database Operations (`utils/db_helpers.py`)

### **Connection Management**

#### `get_database_connection()` - `utils/db_helpers.py`
- **Purpose**: Establish SQLite database connection with error handling
- **Parameters**: None
- **Returns**: `sqlite3.Connection` - Database connection object
- **Features**: 
  - Automatic database file creation
  - Row factory for dictionary access
  - Connection pooling support

#### `close_database_connection(conn)` - `utils/db_helpers.py`
- **Purpose**: Safely close database connection with commit
- **Parameters**: `conn: sqlite3.Connection` - Active database connection
- **Returns**: None
- **Features**: Automatic commit before close, exception handling

---

## 📝 Text Processing (`text_processor.py`)

### **Text Cleaning Functions**

#### `preprocess_text_for_tts(text)` - `text_processor.py`
- **Purpose**: Clean and convert text for optimal TTS processing
- **Parameters**: `text: str` - Raw Chinese text input
- **Returns**: `str` - Cleaned text ready for TTS engines
- **Features**:
  - Number conversion (180 → 一百八十)
  - Symbol sanitization for TTS compatibility
  - Range support: 1-9999 for number conversion
  - Removes problematic characters for audio synthesis

---

## 🎙️ TTS Engine System (`tts/`)

### **Factory Pattern Functions**

#### `TTSFactory.create_engine(engine_name)` - `tts/tts_factory.py`
- **Purpose**: Create TTS engine instance using factory pattern
- **Parameters**: `engine_name: str` - Engine identifier ('edge' or 'hailuo')
- **Returns**: `BaseTTS` - Configured TTS engine instance
- **Engines**: 
  - `edge`: Microsoft Edge TTS (fast, reliable timing)
  - `hailuo`: MiniMax TTS (custom voices, high quality)

#### `TTSFactory.get_supported_engines()` - `tts/tts_factory.py`
- **Purpose**: Get available TTS engines with capability information
- **Parameters**: None
- **Returns**: `dict` - Engine capabilities and configuration status
- **Features**: Dynamic availability checking, configuration validation

### **Base TTS Interface**

#### `BaseTTS.generate_speech(text, voice, speed, volume)` - `tts/base_tts.py`
- **Purpose**: Abstract interface for TTS generation across engines
- **Parameters**:
  - `text: str` - Text to synthesize
  - `voice: str` - Voice identifier
  - `speed: float` - Speech rate multiplier
  - `volume: float` - Audio volume level
- **Returns**: `tuple[bytes, list]` - Audio data and word timing information
- **Implementation**: Must be overridden by concrete engine classes

---

## 🤖 AI/LLM Integration (`llm_manager.py`)

### **LLM Management Functions**

#### `LLMManager.get_word_definition(word)` - `llm_manager.py`
- **Purpose**: Generate structured vocabulary definitions using AI
- **Parameters**: `word: str` - Chinese word to define
- **Returns**: `dict` - Structured definition with pinyin, meanings, examples
- **Features**:
  - Dual provider support (OpenRouter primary, OpenAI fallback)
  - Structured JSON output validation
  - Error handling and service availability checking
  - Rate limiting and retry logic

#### `LLMManager.is_available()` - `llm_manager.py`
- **Purpose**: Check if any LLM service is currently available
- **Parameters**: None
- **Returns**: `bool` - True if at least one service is operational
- **Features**: Real-time availability testing, credential validation

---

## 🔧 Utility Functions (`utils/`)

### **Text Helper Functions** (`utils/text_helpers.py`)

#### `check_word_in_vocabulary(word)` - `utils/text_helpers.py`
- **Purpose**: Fast vocabulary lookup for word existence checking
- **Parameters**: `word: str` - Chinese word to check
- **Returns**: `bool` - True if word exists in vocabulary database
- **Performance**: Optimized for frequent karaoke highlighting checks

#### `get_vocabulary_info(word)` - `utils/text_helpers.py`
- **Purpose**: Retrieve complete vocabulary information for word
- **Parameters**: `word: str` - Chinese word to lookup
- **Returns**: `dict` - Complete vocabulary data or None if not found
- **Fields**: `word, pinyin, spanish_meaning, chinese_meaning, word_type, synonyms, antonyms, usage_example`

#### `insert_vocabulary_word(definition_data)` - `utils/text_helpers.py`
- **Purpose**: Insert AI-generated definition into vocabulary database
- **Parameters**: `definition_data: dict` - Structured definition from LLM
- **Returns**: `bool` - Success status of database insertion
- **Features**: Automatic timestamp generation, duplicate handling

#### `get_google_translate(word)` - `utils/text_helpers.py`
- **Purpose**: Get quick translation using Google Translate API
- **Parameters**: `word: str` - Chinese word to translate
- **Returns**: `str` - Spanish translation or error message
- **Features**: Error handling, encoding support, rate limiting

#### `extract_pinyin_for_characters(text)` - `utils/text_helpers.py`
- **Purpose**: Generate pinyin pronunciation data for Chinese text
- **Parameters**: `text: str` - Chinese text
- **Returns**: `list[dict]` - Character-by-character pinyin mapping
- **Library**: Uses pypinyin with tone marks and romanization

#### `parse_filter_params(request)` - `utils/text_helpers.py`
- **Purpose**: Extract and validate session filtering parameters
- **Parameters**: `request` - FastAPI request object
- **Returns**: `dict` - Validated filter parameters
- **Filters**: `show_favorites, search_text, sort_by`

#### `apply_session_filters(sessions, filter_params)` - `utils/text_helpers.py`
- **Purpose**: Apply filtering logic to session list
- **Parameters**:
  - `sessions: list` - List of session objects
  - `filter_params: dict` - Filter criteria
- **Returns**: `list` - Filtered session list
- **Features**: Text search, favorite filtering, multiple criteria support

#### `update_all_sessions_with_word(word)` - `utils/text_helpers.py`
- **Purpose**: Background task to update vocabulary status across all sessions
- **Parameters**: `word: str` - Newly added vocabulary word
- **Returns**: None (async operation)
- **Features**: Non-blocking execution, batch processing, error recovery

### **Response Helper Functions** (`utils/response_helpers.py`)

#### `parse_request_data(request)` - `utils/response_helpers.py`
- **Purpose**: Extract and validate TTS request parameters
- **Parameters**: `request` - FastAPI request with form or JSON data
- **Returns**: `tuple` - (text, voice, speed, volume, engine)
- **Features**: Default value handling, parameter validation, type conversion

#### `convert_timings_to_word_data(word_timings)` - `utils/response_helpers.py`
- **Purpose**: Transform engine timing data to frontend-compatible format
- **Parameters**: `word_timings: list` - Raw timing data from TTS engine
- **Returns**: `list[dict]` - Frontend word timing objects
- **Format**: Standardized across different TTS engines

#### `save_timestamps_json(word_data)` - `utils/response_helpers.py`
- **Purpose**: Save timing data to JSON file for session persistence
- **Parameters**: `word_data: list` - Frontend-formatted timing data
- **Returns**: `str` - Path to saved JSON file
- **Features**: Atomic file operations, error handling

#### `create_tts_response(audio_base64, word_data, pinyin_data, text, json_file_path)` - `utils/response_helpers.py`
- **Purpose**: Generate complete HTML response for TTS generation
- **Parameters**:
  - `audio_base64: str` - Base64-encoded audio data
  - `word_data: list` - Word timing information
  - `pinyin_data: list` - Pinyin pronunciation data
  - `text: str` - Original Chinese text
  - `json_file_path: str` - Path to timing data file
- **Returns**: `fasthtml.Div` - Complete audio player with controls and data
- **Features**: HTMX integration, karaoke highlighting setup, progress indicators

---

## 📊 Progress Management (`progress_manager.py`)

### **Progress Tracking Functions**

#### `ProgressManager.start_session(session_id, total_chunks)` - `progress_manager.py`
- **Purpose**: Initialize progress tracking for TTS generation session
- **Parameters**:
  - `session_id: str` - Unique session identifier
  - `total_chunks: int` - Total number of text chunks to process
- **Returns**: None
- **Features**: Thread-safe operations, automatic cleanup scheduling

#### `ProgressManager.update_progress(session_id, current_chunk, message)` - `progress_manager.py`
- **Purpose**: Update progress for active TTS session
- **Parameters**:
  - `session_id: str` - Session identifier
  - `current_chunk: int` - Current chunk being processed
  - `message: str` - Status message for user display
- **Returns**: None
- **Features**: Percentage calculation, timestamp tracking, thread safety

#### `ProgressManager.get_minimax_progress()` - `progress_manager.py`
- **Purpose**: Get current MiniMax TTS progress for UI updates
- **Parameters**: None
- **Returns**: `dict` - Progress data with percentage and message
- **Integration**: Used by HTMX progress bar polling

---

## 🎛️ Configuration Management (`config/`)

### **Credentials Management** (`config/credentials_manager.py`)

#### `CredentialsManager.get_credentials(engine)` - `config/credentials_manager.py`
- **Purpose**: Retrieve stored credentials for TTS engine
- **Parameters**: `engine: str` - Engine name ('minimax', 'openai', etc.)
- **Returns**: `dict` - Credential dictionary or empty dict
- **Security**: Environment variable integration, secure storage

#### `CredentialsManager.set_credentials(engine, credentials)` - `config/credentials_manager.py`
- **Purpose**: Store and validate engine credentials
- **Parameters**:
  - `engine: str` - Engine identifier
  - `credentials: dict` - Credential data to store
- **Returns**: `dict` - Success/error result with validation status
- **Features**: Input validation, secure storage, availability testing

#### `CredentialsManager.validate_credentials(engine)` - `config/credentials_manager.py`
- **Purpose**: Test stored credentials for engine availability
- **Parameters**: `engine: str` - Engine to validate
- **Returns**: `dict` - Validation result with detailed status
- **Features**: Real API testing, error categorization, timeout handling

### **Path Management** (`config/paths.py`)

#### `get_path_manager()` - `config/paths.py`
- **Purpose**: Get singleton path manager instance
- **Parameters**: None
- **Returns**: `PathManager` - Configured path manager
- **Features**: Cross-platform path handling, automatic directory creation

#### `PathManager.get_session_dir(session_id)` - `config/paths.py`
- **Purpose**: Get session directory path with automatic creation
- **Parameters**: `session_id: str` - Session identifier
- **Returns**: `pathlib.Path` - Session directory path
- **Features**: Automatic parent directory creation, validation

---

## 🔍 Vocabulary Management (`utils/vocabulary_manager.py`)

### **Database State Management**

#### `VocabularyManager.get_database_stats()` - `utils/vocabulary_manager.py`
- **Purpose**: Get comprehensive vocabulary database statistics
- **Parameters**: None
- **Returns**: `dict` - Database metrics including count, size, modification time
- **Features**: File system monitoring, performance metrics

#### `VocabularyManager.refresh_vocabulary_state()` - `utils/vocabulary_manager.py`
- **Purpose**: Refresh vocabulary status across all sessions
- **Parameters**: `progress_callback: callable` - Optional progress reporting function
- **Returns**: `dict` - Refresh results with statistics
- **Features**: Background processing, progress reporting, error recovery

#### `VocabularyManager.needs_refresh()` - `utils/vocabulary_manager.py`
- **Purpose**: Determine if vocabulary state needs refreshing
- **Parameters**: None
- **Returns**: `bool` - True if refresh is recommended
- **Criteria**: Database modification time, cache staleness, error states

---

## 🎯 Function Usage Patterns

### **Error Handling Pattern**
```python
try:
    # Core operation
    result = perform_operation()
    logger.info(f"Operation successful: {result}")
    return {"success": True, "data": result}
except SpecificException as e:
    logger.error(f"Specific error: {e}")
    return {"success": False, "error": str(e)}
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return {"success": False, "error": "Internal server error"}
```

### **Database Operation Pattern**
```python
conn = get_database_connection()
try:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM table WHERE condition = ?", (param,))
    result = cursor.fetchall()
    return result
finally:
    close_database_connection(conn)
```

### **Async Function Pattern**
```python
async def async_operation(param):
    logger.info(f"Starting async operation: {param}")
    try:
        result = await external_service.call(param)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Async operation failed: {e}")
        return {"success": False, "error": str(e)}
```

### **HTMX Response Pattern**
```python
def htmx_endpoint(request):
    try:
        data = process_request(request)
        return Div(
            # Main content
            content_html,
            # Out-of-band updates
            Div(
                updated_sidebar_content,
                id="sidebar-target",
                **{"hx-swap-oob": "innerHTML"}
            )
        )
    except Exception as e:
        return Div(f"Error: {str(e)}", cls="error-message")
```

---

## 📚 Function Categories Summary

### **FastHTML Route Handlers**: 15 endpoints
- Session management (6 routes)
- TTS generation (3 routes) 
- Word interaction (2 routes)
- Progress tracking (2 routes)
- Configuration (2 routes)

### **Database Operations**: 8 core functions
- Connection management (2 functions)
- Vocabulary operations (4 functions)
- Session persistence (2 functions)

### **Text Processing**: 6 functions
- Cleaning and conversion (2 functions)
- Pinyin generation (1 function)
- Filtering and search (3 functions)

### **TTS Engine Interface**: 12 functions
- Factory pattern (3 functions)
- Engine implementations (6 functions)
- Progress tracking (3 functions)

### **AI/LLM Integration**: 4 functions
- Definition generation (2 functions)
- Service management (2 functions)

### **Configuration Management**: 10 functions
- Credentials (4 functions)
- Paths (3 functions)
- Defaults (3 functions)

---

*This reference serves as the primary function lookup guide for AI coding assistants working with FastTTS. All functions include error handling, logging, and follow established patterns for consistency and maintainability.*