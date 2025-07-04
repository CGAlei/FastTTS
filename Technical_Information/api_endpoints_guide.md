# FastTTS API Endpoints Guide

## 📋 Endpoint Overview

FastTTS uses FastHTML with HTMX integration to provide a modern, reactive web application. This guide documents all API endpoints, their request/response formats, and usage patterns for AI coding assistants.

---

## 🏠 Main Application Routes

### **`GET /`** - Main Application Interface
- **Location**: `main.py:444`
- **Purpose**: Serve the main three-panel application interface
- **Parameters**: 
  - Query: `session` (optional) - Initial session to load
  - Query: `favorites`, `search` - Initial filter parameters
- **Response**: Complete HTML page with three-panel layout
- **Features**:
  - Dynamic session list with filtering
  - Karaoke text display area
  - ChatGPT-style floating input
  - Vocabulary sidebar
  - Theme and accessibility controls

**Request Example:**
```http
GET /?session=20250625_120000&favorites=true
```

**Response Structure:**
```html
<div class="app-container">
  <aside class="left-sidebar"><!-- Session management --></aside>
  <main class="main-content"><!-- Karaoke area + input --></main>
  <aside class="right-sidebar"><!-- Vocabulary display --></aside>
</div>
```

---

## 🎵 TTS Generation Endpoints

### **`POST /generate-custom-tts`** - TTS Audio Generation
- **Location**: `main.py:1201`
- **Purpose**: Generate TTS audio with word-level timing synchronization
- **Content-Type**: `application/x-www-form-urlencoded` or `application/json`
- **Parameters**:
  - `custom_text: str` - Chinese text for synthesis (required)
  - `voice: str` - Voice identifier (default: zh-CN-XiaoxiaoNeural)
  - `speed: float` - Speech rate 0.5-2.0 (default: 1.0)
  - `volume: float` - Audio volume 0.0-2.0 (default: 1.0)
  - `tts_engine: str` - Engine ('edge' or 'hailuo', default: 'edge')

**Request Example:**
```http
POST /generate-custom-tts
Content-Type: application/x-www-form-urlencoded

custom_text=你好世界&voice=zh-CN-XiaoxiaoNeural&speed=1.0&volume=1.0&tts_engine=edge
```

**Response**: FastHTML Div with embedded audio player and timing data
```html
<div>
  <audio id="audio-player" style="display: none;">
    <source src="data:audio/mp3;base64,..." type="audio/mpeg">
  </audio>
  <div id="word-data" data-words='[{"word":"你","startTime":0.1,"endTime":0.5}...]'></div>
  <div id="pinyin-data" data-pinyin='[{"char":"你","pinyin":"nǐ"}...]'></div>
</div>
```

**Error Response:**
```html
<div class="text-red-500 p-4 bg-red-50 border border-red-200 rounded-md">
  ❌ Error generating TTS: [error message]
</div>
```

### **`GET /minimax-progress`** - TTS Progress Polling
- **Location**: `main.py:1146`
- **Purpose**: HTMX-compatible progress updates for TTS generation
- **Method**: GET (called via HTMX polling)
- **Response**: HTML progress bar with message

**HTMX Integration:**
```html
<div hx-get="/minimax-progress" 
     hx-trigger="startProgress from:body, every 600ms" 
     hx-target="this" 
     hx-swap="innerHTML">
</div>
```

**Response Structure:**
```html
<div>
  <div id="progress-message" class="progress-message">Processing chunk 2 of 5...</div>
  <div class="progress">
    <div id="minimax-progress-bar" class="progress-bar" style="width:40%"></div>
  </div>
</div>
```

---

## 💾 Session Management Endpoints

### **`POST /save-session`** - Session Persistence
- **Location**: `main.py:1450`
- **Purpose**: Save complete session with audio, timing, and metadata
- **Content-Type**: `application/json`
- **Parameters**:
  - `text: str` - Original Chinese text
  - `wordData: list` - Word timing information
  - `audioData: str` - Base64-encoded audio file

**Request Example:**
```json
{
  "text": "你好世界",
  "wordData": [
    {"word": "你", "startTime": 0.1, "endTime": 0.5, "hasVocabulary": false},
    {"word": "好", "startTime": 0.5, "endTime": 0.9, "hasVocabulary": true}
  ],
  "audioData": "data:audio/mp3;base64,SUQzBAAAAAAAI1RTU0UAAAAP..."
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "20250625_143022"
}
```

### **`GET /load-session/{session_id}`** - Session Loading
- **Location**: `main.py:1676`
- **Purpose**: Load saved session with complete state restoration
- **Parameters**: `session_id: str` - Session identifier from URL path
- **Response**: FastHTML Div with audio player and out-of-band updates

**Request Example:**
```http
GET /load-session/20250625_143022
```

**Response Features:**
- Audio player with session audio
- Text display update (out-of-band)
- Input textarea update (out-of-band)
- Session list highlighting (out-of-band)
- Session metadata display

### **`POST /toggle-favorite/{session_id}`** - Favorite Management
- **Location**: `main.py:1499`
- **Purpose**: Toggle favorite status for session
- **Parameters**: `session_id: str` - Session identifier
- **Response**: Updated favorite button HTML with out-of-band session list update

**HTMX Integration:**
```html
<button hx-post="/toggle-favorite/20250625_143022" 
        hx-target="closest .favorite-btn" 
        hx-swap="outerHTML">⭐</button>
```

### **`DELETE /delete-session/{session_id}`** - Session Deletion
- **Location**: `main.py:1756`
- **Purpose**: Delete session with auto-selection logic
- **Parameters**: `session_id: str` - Session to delete
- **Response**: Updated session list with auto-selected next session

**Features:**
- Automatic next session selection
- JavaScript auto-loading of selected session
- Complete directory cleanup

### **`POST /rename-session/{session_id}`** - Session Renaming
- **Location**: `main.py:1818`
- **Purpose**: Update session custom name
- **Content-Type**: `application/x-www-form-urlencoded`
- **Parameters**:
  - `new_name: str` - Custom session name (max 100 chars)
  - `current_session_id: str` - Currently active session

**Response:**
```json
{
  "success": true,
  "session": {
    "id": "20250625_143022",
    "custom_name": "Chinese Grammar Lesson 1",
    "text": "你好世界",
    "date": "2025-06-25 14:30:22"
  }
}
```

---

## 🔍 Session Filtering and Search

### **`GET|POST /filter-sessions`** - Session Filtering
- **Location**: `main.py:365`
- **Purpose**: Real-time session filtering with multiple criteria
- **Methods**: Both GET (query params) and POST (form data)
- **Parameters**:
  - `search: str` - Text search query (max 100 chars)
  - `favorites: bool` - Show only favorites
  - `current_session: str` - Currently active session ID

**GET Request Example:**
```http
GET /filter-sessions?search=hello&favorites=true&current_session=20250625_143022
```

**POST Request Example (HTMX):**
```html
<input hx-post="/filter-sessions" 
       hx-target="#sessions-list" 
       hx-trigger="keyup changed delay:300ms"
       name="search" 
       placeholder="Search...">
```

**Response**: HTML session list matching filter criteria

---

## 🔤 Word Interaction Endpoints

### **`POST /word-interaction`** - Word Click Handling
- **Location**: `main.py:1270`
- **Purpose**: Process karaoke word interactions with context-aware responses
- **Content-Type**: `application/json`
- **Parameters**:
  - `action: str` - Interaction type ('left-click', 'right-click', 'hover-enter')
  - `data: object` - Word data (wordId, wordText, startTime, endTime, wordIndex)
  - `timestamp: number` - Interaction timestamp

**Request Example:**
```json
{
  "action": "right-click",
  "data": {
    "wordId": "word_3",
    "wordText": "世界",
    "wordIndex": 3,
    "startTime": 1.2,
    "endTime": 1.8
  },
  "timestamp": 1672531200000
}
```

**Response Actions:**
```json
{
  "success": true,
  "received": {
    "action": "right-click",
    "wordText": "世界",
    "wordId": "word_3"
  },
  "action": "show-translation-popup",
  "wordId": "word_3",
  "wordText": "世界",
  "translation": "world",
  "coordinates": {"x": 0, "y": 0}
}
```

**Response Types:**
- `show-vocabulary-info`: Display vocabulary from database
- `show-translation-popup`: Show Google Translate popup
- `play-word-audio`: Play specific audio segment
- `highlight-word`: Temporary visual highlight

### **`POST /define-word`** - AI Definition Generation
- **Location**: `main.py:1367`
- **Purpose**: Generate and save AI-powered word definitions
- **Content-Type**: `application/json`
- **Parameters**:
  - `word: str` - Chinese word to define
  - `wordId: str` - Frontend word identifier
  - `currentSessionId: str` - Active session context

**Request Example:**
```json
{
  "word": "世界",
  "wordId": "word_3",
  "currentSessionId": "20250625_143022"
}
```

**Success Response:**
```json
{
  "success": true,
  "message": "Word definition generated and saved successfully",
  "word": "世界",
  "wordId": "word_3",
  "vocabularyData": {
    "word": "世界",
    "pinyin": "shìjiè",
    "spanish_meaning": "mundo",
    "chinese_meaning": "整个地球；全球",
    "word_type": "名词",
    "synonyms": "地球, 全球",
    "antonyms": "无",
    "usage_example": "世界很大，我想去看看。"
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "AI definition service unavailable"
}
```

---

## 📚 Vocabulary Management Endpoints

### **`POST /vocabulary-display`** - Vocabulary HTML Rendering
- **Location**: `main.py:1859`
- **Purpose**: Generate HTML for vocabulary information display
- **Content-Type**: `application/json`
- **Parameters**: `vocabularyData: object` - Complete vocabulary information

**Request Example:**
```json
{
  "vocabularyData": {
    "word": "世界",
    "pinyin": "shìjiè",
    "spanish_meaning": "mundo",
    "chinese_meaning": "整个地球；全球",
    "word_type": "名词",
    "usage_example": "世界很大，我想去看看。"
  }
}
```

**Response**: Complete HTML structure for vocabulary cards in right sidebar

### **`POST /refresh-vocabulary`** - Vocabulary State Refresh
- **Location**: `main.py:1986`
- **Purpose**: Refresh vocabulary status across all sessions
- **Parameters**: None (triggers background processing)

**Response:**
```json
{
  "success": true,
  "message": "Refresh completed",
  "stats": {
    "vocabulary_count": 1534,
    "sessions_processed": 42,
    "words_updated": 128,
    "duration_seconds": 2.4
  }
}
```

### **`GET /vocab-stats`** - Vocabulary Statistics
- **Location**: `main.py:2014`
- **Purpose**: Get current vocabulary database statistics
- **Parameters**: None

**Response:**
```json
{
  "database": {
    "filename": "vocab.db",
    "word_count": 1534,
    "file_size_mb": 0.57,
    "last_modified": "2025-06-25T14:30:22Z",
    "last_modified_formatted": "2025-06-25 14:30"
  },
  "last_refresh": {
    "timestamp": "2025-06-25T14:25:15Z",
    "sessions_processed": 42,
    "words_updated": 128,
    "duration_seconds": 2.4
  },
  "needs_refresh": false
}
```

---

## 🔧 Configuration and Status Endpoints

### **`GET /tts-engines-info`** - TTS Engine Information
- **Location**: `main.py:1537`
- **Purpose**: Get available TTS engines and their capabilities
- **Parameters**: None

**Response:**
```json
{
  "success": true,
  "engines": {
    "edge": {
      "name": "Microsoft Edge TTS",
      "available": true,
      "voices": ["zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural"],
      "features": ["word_timing", "speed_control", "volume_control"]
    },
    "hailuo": {
      "name": "MiniMax Hailuo TTS",
      "available": true,
      "configured": true,
      "custom_voices": true,
      "features": ["custom_voices", "high_quality", "mfa_alignment"]
    }
  },
  "default_engine": "edge"
}
```

### **`GET /credentials-status`** - Credentials Configuration Status
- **Location**: `main.py:1592`
- **Purpose**: Check configuration status for all TTS engines
- **Parameters**: None

**Response:**
```json
{
  "success": true,
  "engines": {
    "minimax": {
      "configured": true,
      "has_api_key": true,
      "has_group_id": true,
      "last_validated": "2025-06-25T14:30:22Z",
      "status": "operational"
    },
    "openai": {
      "configured": true,
      "has_api_key": true,
      "status": "operational"
    }
  }
}
```

### **`POST /save-credentials`** - Save Engine Credentials
- **Location**: `main.py:1607`
- **Purpose**: Store and validate TTS engine credentials
- **Content-Type**: `application/json`
- **Parameters**:
  - `engine: str` - Engine identifier
  - `credentials: object` - Credential data

**Request Example:**
```json
{
  "engine": "minimax",
  "credentials": {
    "api_key": "sk-...",
    "group_id": "1234567890",
    "model": "speech-02-turbo",
    "chunk_size": 120,
    "custom_voice_id": ""
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Credentials saved and validated successfully",
  "validation": {
    "api_connection": true,
    "model_access": true,
    "voice_access": true
  }
}
```

### **`POST /validate-credentials`** - Test Engine Credentials
- **Location**: `main.py:1651`
- **Purpose**: Validate stored credentials without saving
- **Content-Type**: `application/json`
- **Parameters**: `engine: str` - Engine to validate

**Response:**
```json
{
  "success": true,
  "validation": {
    "api_connection": true,
    "authentication": true,
    "model_access": true,
    "error_details": null
  }
}
```

---

## 📊 Progress and Monitoring Endpoints

### **`GET /tts-progress/{session_id}`** - TTS Progress Streaming
- **Location**: `main.py:1050`
- **Purpose**: Server-Sent Events for real-time TTS progress
- **Parameters**: `session_id: str` - TTS session identifier
- **Response**: Server-Sent Events stream

**SSE Event Types:**
```javascript
// Connection established
{type: 'connected', session_id: 'session_123'}

// Progress update
{
  type: 'progress_update',
  session_id: 'session_123',
  current_chunk: 3,
  total_chunks: 8,
  percentage: 37,
  status: 'processing',
  message: 'Processing chunk 3 of 8...',
  timestamp: 1672531200.123
}

// Session completed
{type: 'session_ended', session_id: 'session_123'}

// Keep-alive ping
{type: 'ping', timestamp: 1672531200.456}

// Error occurred
{type: 'error', message: 'Processing failed'}
```

### **`GET /api/progress-sessions`** - Active Progress Sessions
- **Location**: `main.py:1123`
- **Purpose**: Get currently active TTS sessions for frontend SSE connection
- **Parameters**: None

**Response:**
```json
{
  "active_session": "session_123",
  "status": "processing",
  "total_chunks": 8
}
```

### **`GET /refresh-vocabulary-progress/{session_id}`** - Vocabulary Refresh Progress
- **Location**: `main.py:2035`
- **Purpose**: Server-Sent Events for vocabulary refresh progress
- **Parameters**: `session_id: str` - Refresh session identifier

**SSE Events:**
```javascript
// Progress update
{
  type: 'progress_update',
  session_id: 'refresh_123',
  progress: 45,
  message: 'Processing session 18 of 40...',
  completed: false,
  timestamp: 1672531200.789
}

// Completion with statistics
{
  type: 'completed',
  session_id: 'refresh_123',
  success: true,
  stats: {
    vocabulary_count: 1534,
    sessions_processed: 40,
    words_updated: 156,
    duration_seconds: 3.2
  }
}
```

---

## 🎯 Request/Response Patterns

### **HTMX Integration Pattern**
FastTTS uses HTMX for seamless partial page updates:

```html
<!-- Trigger endpoint with form data -->
<form hx-post="/endpoint" 
      hx-target="#target-element" 
      hx-swap="innerHTML"
      hx-indicator="#loading">
  
<!-- Include additional form elements -->
<button hx-include="[name='related-field']">Submit</button>

<!-- Out-of-band updates -->
<div hx-swap-oob="innerHTML:#sidebar">Updated content</div>
```

### **Error Response Pattern**
All endpoints follow consistent error response format:

```json
{
  "success": false,
  "error": "Human-readable error message",
  "error_code": "SPECIFIC_ERROR_CODE",
  "details": {
    "field": "validation error details"
  }
}
```

### **Progress Response Pattern**
Progress endpoints use consistent structure:

```json
{
  "session_id": "unique_identifier",
  "current": 3,
  "total": 10,
  "percentage": 30,
  "status": "processing|completed|error",
  "message": "Human-readable status",
  "timestamp": "ISO8601 or unix timestamp"
}
```

### **Out-of-Band Update Pattern**
HTMX out-of-band updates for multi-element updates:

```html
<div>
  <!-- Main response content -->
  <div>Primary update content</div>
  
  <!-- Out-of-band updates -->
  <div id="sessions-list" hx-swap-oob="innerHTML">
    <!-- Updated session list -->
  </div>
  
  <div id="vocabulary-content" hx-swap-oob="innerHTML">
    <!-- Updated vocabulary display -->
  </div>
</div>
```

---

## 🔐 Security and Validation

### **Input Validation**
- Text length limits (custom_text: 10,000 chars max)
- Session name length (100 chars max)
- Search query length (100 chars max)
- Parameter type validation (speed: float 0.5-2.0)
- SQL injection prevention (parameterized queries)

### **Rate Limiting**
- AI definition generation: Per-user rate limiting
- TTS generation: Concurrent request limiting
- Progress polling: 600ms minimum interval

### **Error Handling**
- Graceful degradation for service failures
- Detailed logging without exposing internals
- Fallback mechanisms for external services
- Client-side error recovery

---

## 📈 Performance Characteristics

### **Response Times**
- Static content: <50ms
- Session loading: <200ms
- TTS generation: 1-5s (depending on text length and engine)
- Vocabulary lookup: <100ms
- AI definition generation: 2-10s

### **Caching Strategy**
- Session metadata: File-based caching
- Vocabulary lookups: In-memory caching
- Static assets: Browser caching with versioning
- Progress data: Memory-based with automatic cleanup

### **Concurrent Handling**
- Multiple TTS sessions: Supported with progress tracking
- Session filtering: Non-blocking operations
- Background tasks: Async processing for AI definitions
- Database operations: Connection pooling

---

*This guide provides comprehensive endpoint documentation for AI coding assistants working with FastTTS. All endpoints include proper error handling, logging, and follow RESTful principles where applicable.*