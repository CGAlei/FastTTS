# FastTTS Development Patterns & Best Practices Guide

## 📋 Development Philosophy

FastTTS follows modern software development principles with emphasis on modularity, maintainability, and performance. This guide outlines the coding patterns, architectural decisions, and best practices that ensure consistent, high-quality code across the entire application.

**Core Principles**: Clean Architecture, Separation of Concerns, Performance First, Security by Design  
**Code Style**: Python PEP 8, JavaScript ES6+, Functional Programming Elements  
**Testing Strategy**: Unit Testing, Integration Testing, Performance Testing  
**Documentation**: Comprehensive inline documentation and architectural guides  

---

## 🏗️ Architectural Patterns

### **Factory Pattern** - TTS Engine Management
FastTTS uses the Factory Pattern extensively for creating and managing TTS engine instances.

```python
# TTS Factory Pattern Implementation
class TTSFactory:
    """Factory for creating TTS engine instances with singleton management"""
    
    _engines = {
        "edge": EdgeTTSEngine,
        "hailuo": MinimaxTTSEngine
    }
    
    _instances = {}  # Singleton pattern for performance
    
    @classmethod
    def create_engine(cls, engine_type: str) -> BaseTTSEngine:
        """Create engine instance with validation and caching"""
        engine_type = engine_type.lower()
        
        if engine_type not in cls._engines:
            supported = ", ".join(cls._engines.keys())
            raise ValueError(f"Unsupported engine: {engine_type}. Supported: {supported}")
        
        # Use singleton pattern for efficiency
        if engine_type not in cls._instances:
            cls._instances[engine_type] = cls._engines[engine_type]()
        
        return cls._instances[engine_type]
```

**Benefits**:
- **Extensibility**: Easy addition of new TTS engines
- **Performance**: Singleton pattern prevents unnecessary instantiation
- **Validation**: Centralized engine validation and error handling
- **Abstraction**: Clients don't need to know specific engine classes

### **Abstract Base Class Pattern** - Service Interfaces
All major services implement abstract base classes for consistent interfaces.

```python
# Abstract Base Class Pattern for LLM Providers
class LLMProvider(ABC):
    """Abstract interface for all LLM service providers"""
    
    @abstractmethod
    def get_definition(self, word: str) -> Dict[str, str]:
        """Generate word definition - must be implemented by all providers"""
        pass
    
    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Check service availability - must be implemented"""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return provider identification"""
        pass

# Concrete implementation
class OpenRouterService(LLMProvider):
    def get_definition(self, word: str) -> Dict[str, str]:
        # Implementation specific to OpenRouter
        pass
```

**Benefits**:
- **Consistency**: All providers follow the same interface
- **Interchangeability**: Easy switching between providers
- **Testing**: Mock implementations for unit testing
- **Documentation**: Clear contracts for implementation

### **Repository Pattern** - Database Operations
Database operations follow the Repository Pattern for clean data access abstraction.

```python
# Repository Pattern for Vocabulary Data
class VocabularyRepository:
    """Repository for vocabulary database operations"""
    
    def __init__(self):
        self.connection_manager = DatabaseConnectionManager()
    
    def find_by_word(self, word: str) -> Optional[VocabularyEntry]:
        """Find vocabulary entry by Chinese word"""
        with self.connection_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM vocabulary WHERE ChineseWord = ?", 
                (word,)
            )
            row = cursor.fetchone()
            return VocabularyEntry.from_dict(dict(row)) if row else None
    
    def save(self, entry: VocabularyEntry) -> bool:
        """Save vocabulary entry with UPSERT logic"""
        with self.connection_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO vocabulary 
                (ChineseWord, PinyinPronunciation, SpanishMeaning, ...)
                VALUES (?, ?, ?, ...)
            """, entry.to_tuple())
            conn.commit()
            return True
```

**Benefits**:
- **Separation**: Business logic separated from data access
- **Testing**: Easy mocking of data layer
- **Maintenance**: Database changes isolated to repository
- **Consistency**: Uniform data access patterns

---

## 🎯 Error Handling Patterns

### **Hierarchical Exception Handling**
FastTTS implements a comprehensive exception hierarchy for precise error handling.

```python
# Custom Exception Hierarchy
class FastTTSError(Exception):
    """Base exception for all FastTTS errors"""
    pass

class TTSError(FastTTSError):
    """Base exception for TTS-related errors"""
    pass

class TTSEngineNotAvailableError(TTSError):
    """Raised when TTS engine is not available"""
    pass

class TTSConfigurationError(TTSError):
    """Raised when TTS engine is misconfigured"""
    pass

class AIServiceError(FastTTSError):
    """Base exception for AI service errors"""
    pass

class AIServiceUnavailableError(AIServiceError):
    """Raised when AI service is not available"""
    pass

# Usage in TTS Engine
async def generate_speech(self, text: str, voice: str) -> Tuple[bytes, List]:
    try:
        # TTS generation logic
        return audio_data, timings
    except ConnectionError as e:
        raise TTSEngineNotAvailableError(f"Engine connection failed: {e}")
    except ValueError as e:
        raise TTSConfigurationError(f"Invalid configuration: {e}")
    except Exception as e:
        logger.error(f"Unexpected TTS error: {e}")
        raise TTSError(f"TTS generation failed: {e}")
```

### **Graceful Degradation Pattern**
The application implements graceful degradation for non-critical failures.

```python
# Graceful Degradation for AI Services
def get_word_definition(self, word: str) -> Dict[str, str]:
    """Get definition with graceful fallback"""
    
    # Try primary service (OpenRouter)
    if self.primary_service and self.primary_service.is_available:
        try:
            return self.primary_service.get_definition(word)
        except Exception as e:
            logger.warning(f"Primary service failed: {e}")
    
    # Fallback to secondary service (OpenAI)
    if self.fallback_service and self.fallback_service.is_available:
        try:
            return self.fallback_service.get_definition(word)
        except Exception as e:
            logger.error(f"Fallback service failed: {e}")
    
    # Final fallback - return basic structure
    return {
        'spanish_meaning': 'Translation unavailable',
        'pinyin': 'Pronunciation unavailable',
        'chinese_meaning': 'Definition unavailable',
        'word_type': 'Unknown',
        'synonyms': 'N/A',
        'antonyms': 'N/A',
        'usage_example': 'No example available'
    }
```

---

## 🔄 Asynchronous Programming Patterns

### **Async/Await Best Practices**
FastTTS uses modern async/await patterns for performance-critical operations.

```python
# Async Pattern for TTS Generation
async def generate_custom_tts(request):
    """Async TTS generation with proper error handling"""
    try:
        # Parse request data asynchronously
        text, voice, speed, volume, engine = await parse_request_data(request)
        
        # Preprocess text (sync operation)
        cleaned_text = preprocess_text_for_tts(text)
        
        # Generate TTS asynchronously
        audio_data, timings = await _generate_tts_response(
            cleaned_text, voice, speed, volume, engine
        )
        
        # Process response (sync operation)
        return create_tts_response(audio_data, timings, cleaned_text)
        
    except Exception as e:
        logger.error(f"TTS generation failed: {e}")
        return error_response(str(e))

# Async Context Manager for Database
class AsyncDatabaseManager:
    async def __aenter__(self):
        self.connection = await get_async_db_connection()
        return self.connection
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            await self.connection.close()

# Usage
async def async_database_operation():
    async with AsyncDatabaseManager() as db:
        result = await db.execute("SELECT * FROM vocabulary")
        return result
```

### **Background Task Management**
Background tasks are properly managed to prevent resource leaks.

```python
# Background Task Pattern
class BackgroundTaskManager:
    def __init__(self):
        self.active_tasks = set()
    
    def create_task(self, coro, name: str = None):
        """Create managed background task"""
        task = asyncio.create_task(coro, name=name)
        self.active_tasks.add(task)
        
        # Remove from active set when done
        task.add_done_callback(self.active_tasks.discard)
        
        return task
    
    async def shutdown(self):
        """Gracefully shutdown all background tasks"""
        if self.active_tasks:
            await asyncio.gather(*self.active_tasks, return_exceptions=True)

# Usage in main application
task_manager = BackgroundTaskManager()

async def update_session_vocabulary(word: str):
    """Background vocabulary update task"""
    await task_manager.create_task(
        update_all_sessions_with_word(word),
        name=f"vocab_update_{word}"
    )
```

---

## 📊 Performance Optimization Patterns

### **Caching Strategy**
Multiple levels of caching for optimal performance.

```python
# Multi-Level Caching Pattern
class CacheManager:
    def __init__(self):
        self.memory_cache = {}  # L1: In-memory cache
        self.redis_cache = None  # L2: Redis cache (if available)
        self.file_cache = {}    # L3: File-based cache
    
    async def get(self, key: str):
        """Get from cache with fallback levels"""
        # L1: Memory cache (fastest)
        if key in self.memory_cache:
            return self.memory_cache[key]
        
        # L2: Redis cache (if available)
        if self.redis_cache:
            value = await self.redis_cache.get(key)
            if value:
                self.memory_cache[key] = value  # Promote to L1
                return value
        
        # L3: File cache (slowest but persistent)
        return self._get_from_file_cache(key)
    
    async def set(self, key: str, value, ttl: int = 3600):
        """Set in all cache levels"""
        self.memory_cache[key] = value
        
        if self.redis_cache:
            await self.redis_cache.setex(key, ttl, value)
        
        self._set_file_cache(key, value, ttl)

# Vocabulary caching implementation
class VocabularyCacheManager(CacheManager):
    async def get_word_info(self, word: str):
        """Get vocabulary info with caching"""
        cache_key = f"vocab:{word}"
        
        # Try cache first
        cached = await self.get(cache_key)
        if cached:
            return cached
        
        # Cache miss - fetch from database
        vocab_info = get_vocabulary_info(word)
        if vocab_info:
            await self.set(cache_key, vocab_info, ttl=7200)  # 2 hours
        
        return vocab_info
```

### **Database Connection Pooling**
Efficient database connection management.

```python
# Connection Pool Pattern
class DatabaseConnectionPool:
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.pool = asyncio.Queue(maxsize=max_connections)
        self.created_connections = 0
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Pre-create connections for immediate availability"""
        for _ in range(self.max_connections // 2):
            conn = self._create_connection()
            self.pool.put_nowait(conn)
            self.created_connections += 1
    
    async def get_connection(self):
        """Get connection from pool or create new one"""
        try:
            # Try to get existing connection
            return self.pool.get_nowait()
        except asyncio.QueueEmpty:
            # Create new connection if under limit
            if self.created_connections < self.max_connections:
                conn = self._create_connection()
                self.created_connections += 1
                return conn
            else:
                # Wait for available connection
                return await self.pool.get()
    
    async def return_connection(self, conn):
        """Return connection to pool"""
        # Validate connection before returning
        if self._is_connection_valid(conn):
            await self.pool.put(conn)
        else:
            # Replace invalid connection
            self.created_connections -= 1
            new_conn = self._create_connection()
            await self.pool.put(new_conn)

# Usage with context manager
@asynccontextmanager
async def get_db_connection():
    conn = await db_pool.get_connection()
    try:
        yield conn
    finally:
        await db_pool.return_connection(conn)
```

---

## 🎨 Frontend Patterns

### **Module Pattern** - JavaScript Architecture
JavaScript code follows ES6+ module patterns with proper encapsulation.

```javascript
// Module Pattern for Audio Player
class AudioPlayerManager {
    constructor() {
        this.currentAudio = null;
        this.wordData = [];
        this.isHighlighting = false;
        this.eventListeners = new Map();
        
        // Bind methods to preserve context
        this.handleAudioPlay = this.handleAudioPlay.bind(this);
        this.handleAudioPause = this.handleAudioPause.bind(this);
        this.highlightCurrentWord = this.highlightCurrentWord.bind(this);
    }
    
    // Public API methods
    async loadAudio(audioData, wordTimings) {
        try {
            await this._setupAudioElement(audioData);
            this._setupWordTimings(wordTimings);
            this._attachEventListeners();
            
            logger.info('Audio loaded successfully');
        } catch (error) {
            logger.error('Audio loading failed:', error);
            throw new AudioLoadError(error.message);
        }
    }
    
    // Private methods (convention: underscore prefix)
    _setupAudioElement(audioData) {
        this._cleanupPreviousAudio();
        
        this.currentAudio = new Audio(audioData);
        this.currentAudio.preload = 'auto';
        
        return new Promise((resolve, reject) => {
            this.currentAudio.oncanplaythrough = resolve;
            this.currentAudio.onerror = reject;
        });
    }
    
    _cleanupPreviousAudio() {
        if (this.currentAudio) {
            this._removeEventListeners();
            this.currentAudio.pause();
            this.currentAudio = null;
        }
    }
    
    // Memory management
    destroy() {
        this._cleanupPreviousAudio();
        this._clearWordData();
        this.eventListeners.clear();
    }
}

// Singleton pattern for audio manager
const audioManager = new AudioPlayerManager();
export default audioManager;
```

### **Observer Pattern** - Event Management
Frontend uses observer pattern for component communication.

```javascript
// Event System for Component Communication
class EventEmitter {
    constructor() {
        this.events = new Map();
    }
    
    on(event, callback) {
        if (!this.events.has(event)) {
            this.events.set(event, new Set());
        }
        this.events.get(event).add(callback);
        
        // Return unsubscribe function
        return () => this.off(event, callback);
    }
    
    off(event, callback) {
        if (this.events.has(event)) {
            this.events.get(event).delete(callback);
        }
    }
    
    emit(event, data) {
        if (this.events.has(event)) {
            this.events.get(event).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`Event handler error for ${event}:`, error);
                }
            });
        }
    }
}

// Global event bus
const eventBus = new EventEmitter();

// Usage in modules
class VocabularyManager {
    constructor() {
        // Listen for word definition events
        eventBus.on('word:defined', this.handleWordDefined.bind(this));
        eventBus.on('session:loaded', this.refreshVocabularyState.bind(this));
    }
    
    async defineWord(word) {
        try {
            const definition = await this._generateDefinition(word);
            
            // Emit event for other components
            eventBus.emit('word:defined', {
                word: word,
                definition: definition,
                timestamp: Date.now()
            });
            
            return definition;
        } catch (error) {
            eventBus.emit('word:definition-failed', {
                word: word,
                error: error.message
            });
            throw error;
        }
    }
}
```

---

## 🔐 Security Patterns

### **Input Validation and Sanitization**
Comprehensive input validation at all entry points.

```python
# Input Validation Pattern
class InputValidator:
    """Centralized input validation with security focus"""
    
    @staticmethod
    def validate_chinese_text(text: str, max_length: int = 10000) -> str:
        """Validate and sanitize Chinese text input"""
        if not text or not isinstance(text, str):
            raise ValueError("Text must be a non-empty string")
        
        # Length validation
        if len(text) > max_length:
            raise ValueError(f"Text exceeds maximum length of {max_length}")
        
        # Remove potentially harmful characters
        sanitized = re.sub(r'[<>"\';\\]', '', text)
        
        # Ensure some Chinese characters remain
        if not re.search(r'[\u4e00-\u9fff]', sanitized):
            raise ValueError("Text must contain Chinese characters")
        
        return sanitized.strip()
    
    @staticmethod
    def validate_audio_parameters(voice: str, speed: float, volume: float) -> Dict[str, Any]:
        """Validate TTS audio parameters"""
        errors = []
        
        # Voice validation
        if not voice or not isinstance(voice, str):
            errors.append("Voice must be a non-empty string")
        elif len(voice) > 100:
            errors.append("Voice ID too long")
        
        # Speed validation
        if not isinstance(speed, (int, float)):
            errors.append("Speed must be a number")
        elif not 0.5 <= speed <= 2.0:
            errors.append("Speed must be between 0.5 and 2.0")
        
        # Volume validation
        if not isinstance(volume, (int, float)):
            errors.append("Volume must be a number")
        elif not 0.0 <= volume <= 2.0:
            errors.append("Volume must be between 0.0 and 2.0")
        
        if errors:
            raise ValueError("; ".join(errors))
        
        return {
            'voice': voice,
            'speed': float(speed),
            'volume': float(volume)
        }

# Usage in endpoints
@rt("/generate-custom-tts", methods=["POST"])
async def generate_custom_tts(request):
    try:
        # Parse and validate input
        form_data = await request.form()
        
        text = InputValidator.validate_chinese_text(
            form_data.get('custom_text', '')
        )
        
        audio_params = InputValidator.validate_audio_parameters(
            form_data.get('voice', DEFAULT_VOICE),
            float(form_data.get('speed', DEFAULT_SPEED)),
            float(form_data.get('volume', DEFAULT_VOLUME))
        )
        
        # Process with validated input
        return await _generate_tts_response(text, **audio_params)
        
    except ValueError as e:
        logger.warning(f"Input validation failed: {e}")
        return error_response(f"Invalid input: {e}", 400)
```

### **API Key Management**
Secure handling of API keys and credentials.

```python
# Secure API Key Pattern
class SecureCredentialManager:
    """Secure management of API credentials"""
    
    def __init__(self):
        self.encrypted_cache = {}
        self.key_rotation_schedule = {}
    
    def store_api_key(self, service: str, api_key: str) -> bool:
        """Store API key with encryption"""
        try:
            # Validate key format
            if not self._validate_key_format(service, api_key):
                raise ValueError(f"Invalid key format for {service}")
            
            # Encrypt before storage
            encrypted_key = self._encrypt_key(api_key)
            
            # Store in environment (not in code)
            os.environ[f"{service.upper()}_API_KEY"] = encrypted_key
            
            # Cache for session (memory only)
            self.encrypted_cache[service] = encrypted_key
            
            return True
        except Exception as e:
            logger.error(f"Failed to store API key for {service}: {e}")
            return False
    
    def get_api_key(self, service: str) -> Optional[str]:
        """Retrieve and decrypt API key"""
        try:
            # Try cache first
            encrypted_key = self.encrypted_cache.get(service)
            
            # Fallback to environment
            if not encrypted_key:
                encrypted_key = os.getenv(f"{service.upper()}_API_KEY")
            
            if not encrypted_key:
                return None
            
            # Decrypt key
            return self._decrypt_key(encrypted_key)
        except Exception as e:
            logger.error(f"Failed to retrieve API key for {service}: {e}")
            return None
    
    def _validate_key_format(self, service: str, key: str) -> bool:
        """Validate API key format"""
        patterns = {
            'openai': r'^sk-[A-Za-z0-9]{48}$',
            'openrouter': r'^sk-or-v1-[A-Za-z0-9]{64}$',
            'minimax': r'^[A-Za-z0-9]{32,64}$'
        }
        
        if service not in patterns:
            return len(key) > 10  # Basic length check
        
        return re.match(patterns[service], key) is not None
    
    def _encrypt_key(self, key: str) -> str:
        """Encrypt API key (implementation specific)"""
        # Use proper encryption in production
        # This is a simplified example
        import base64
        return base64.b64encode(key.encode()).decode()
    
    def _decrypt_key(self, encrypted_key: str) -> str:
        """Decrypt API key (implementation specific)"""
        import base64
        return base64.b64decode(encrypted_key.encode()).decode()
```

---

## 🧪 Testing Patterns

### **Unit Testing Structure**
Comprehensive unit testing with proper mocking.

```python
# Unit Testing Pattern
import unittest
from unittest.mock import Mock, patch, AsyncMock
import pytest

class TestTTSFactory(unittest.TestCase):
    """Test TTS Factory functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Clear singleton instances for clean tests
        TTSFactory._instances.clear()
        
        # Mock external dependencies
        self.mock_edge_engine = Mock(spec=EdgeTTSEngine)
        self.mock_minimax_engine = Mock(spec=MinimaxTTSEngine)
    
    def test_create_valid_engine(self):
        """Test creation of valid TTS engine"""
        with patch.object(TTSFactory, '_engines', {'edge': Mock(return_value=self.mock_edge_engine)}):
            engine = TTSFactory.create_engine('edge')
            self.assertEqual(engine, self.mock_edge_engine)
    
    def test_create_invalid_engine(self):
        """Test error handling for invalid engine"""
        with self.assertRaises(ValueError) as context:
            TTSFactory.create_engine('invalid_engine')
        
        self.assertIn("Unsupported TTS engine", str(context.exception))
    
    def test_singleton_behavior(self):
        """Test that same instance is returned for repeated calls"""
        with patch.object(TTSFactory, '_engines', {'edge': Mock(return_value=self.mock_edge_engine)}):
            engine1 = TTSFactory.create_engine('edge')
            engine2 = TTSFactory.create_engine('edge')
            self.assertIs(engine1, engine2)

# Async Testing Pattern
class TestLLMManager(unittest.IsolatedAsyncioTestCase):
    """Test LLM Manager with async operations"""
    
    async def asyncSetUp(self):
        """Set up async test environment"""
        self.mock_openrouter = AsyncMock(spec=OpenRouterService)
        self.mock_openai = AsyncMock(spec=OpenAIService)
        
        # Mock successful definition
        self.sample_definition = {
            'spanish_meaning': 'world',
            'pinyin': 'shìjiè',
            'chinese_meaning': '整个地球'
        }
    
    async def test_primary_service_success(self):
        """Test successful definition generation with primary service"""
        self.mock_openrouter.is_available = True
        self.mock_openrouter.get_definition.return_value = self.sample_definition
        
        manager = LLMManager()
        manager.primary_service = self.mock_openrouter
        
        result = manager.get_word_definition('世界')
        
        self.assertEqual(result, self.sample_definition)
        self.mock_openrouter.get_definition.assert_called_once_with('世界')
    
    async def test_fallback_service_activation(self):
        """Test fallback to secondary service when primary fails"""
        self.mock_openrouter.is_available = True
        self.mock_openrouter.get_definition.side_effect = Exception("Primary service failed")
        
        self.mock_openai.is_available = True
        self.mock_openai.get_definition.return_value = self.sample_definition
        
        manager = LLMManager()
        manager.primary_service = self.mock_openrouter
        manager.fallback_service = self.mock_openai
        
        result = manager.get_word_definition('世界')
        
        self.assertEqual(result, self.sample_definition)
        self.mock_openai.get_definition.assert_called_once_with('世界')

# Integration Testing Pattern
class TestTTSIntegration(unittest.TestCase):
    """Integration tests for TTS system"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.test_text = "测试文本"
        self.test_voice = "zh-CN-XiaoxiaoNeural"
    
    @patch('requests.post')
    def test_minimax_integration(self, mock_post):
        """Test actual MiniMax API integration"""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'fake_audio_data'
        mock_post.return_value = mock_response
        
        engine = MinimaxTTSEngine()
        if engine.is_configured():
            # Only run if credentials are available
            result = asyncio.run(engine.generate_speech(
                self.test_text, 
                self.test_voice
            ))
            
            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 2)  # audio_data, timings
```

### **Performance Testing**
Load testing and performance validation.

```python
# Performance Testing Pattern
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

class PerformanceTestSuite:
    """Performance testing for critical operations"""
    
    def __init__(self):
        self.results = {}
    
    async def test_tts_generation_performance(self):
        """Test TTS generation under load"""
        test_texts = [
            "短文本",
            "中等长度的文本用于测试TTS性能",
            "这是一个相对较长的文本用于测试TTS引擎在处理大量文本时的性能表现和响应时间"
        ]
        
        results = []
        
        for text in test_texts:
            start_time = time.time()
            
            # Test Edge TTS
            edge_engine = TTSFactory.create_engine('edge')
            audio_data, timings = await edge_engine.generate_speech(text)
            
            end_time = time.time()
            
            results.append({
                'text_length': len(text),
                'generation_time': end_time - start_time,
                'audio_size': len(audio_data),
                'timing_count': len(timings)
            })
        
        self.results['tts_performance'] = results
        return results
    
    async def test_concurrent_requests(self, concurrent_count: int = 5):
        """Test system under concurrent load"""
        async def make_request():
            start_time = time.time()
            try:
                # Simulate TTS request
                engine = TTSFactory.create_engine('edge')
                await engine.generate_speech("测试文本")
                return time.time() - start_time
            except Exception as e:
                return {'error': str(e)}
        
        # Create concurrent tasks
        tasks = [make_request() for _ in range(concurrent_count)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analyze results
        successful_requests = [r for r in results if isinstance(r, float)]
        failed_requests = [r for r in results if isinstance(r, dict) and 'error' in r]
        
        return {
            'total_requests': concurrent_count,
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'average_response_time': sum(successful_requests) / len(successful_requests) if successful_requests else 0,
            'max_response_time': max(successful_requests) if successful_requests else 0
        }
```

---

## 📝 Documentation Patterns

### **Comprehensive Docstring Standard**
All functions and classes include detailed documentation.

```python
def generate_speech(
    self, 
    text: str, 
    voice: str = None, 
    speed: float = 1.0,
    volume: float = 1.0,
    **kwargs
) -> Tuple[bytes, List[Dict[str, Any]]]:
    """
    Generate speech audio from Chinese text with word-level timing.
    
    This method processes Chinese text through the TTS engine and returns
    both the generated audio data and precise word timing information for
    karaoke-style highlighting.
    
    Args:
        text (str): Chinese text to convert to speech. Must contain at least
            some Chinese characters. Maximum length: 10,000 characters.
        voice (str, optional): Voice identifier for TTS engine. Must be one
            of the supported voices. Defaults to engine's default voice.
        speed (float, optional): Speech speed multiplier. Range: 0.5-2.0.
            Values < 1.0 slow down speech, > 1.0 speed up. Defaults to 1.0.
        volume (float, optional): Audio volume level. Range: 0.0-2.0.
            1.0 is normal volume. Defaults to 1.0.
        **kwargs: Additional engine-specific parameters.
    
    Returns:
        Tuple[bytes, List[Dict[str, Any]]]: A tuple containing:
            - bytes: MP3 audio data ready for playback
            - List[Dict]: Word timing data with keys:
                - 'word' (str): Individual Chinese word/character
                - 'start_time' (float): Start time in seconds
                - 'end_time' (float): End time in seconds
                - 'duration' (float): Word duration in seconds
    
    Raises:
        ValueError: If text is empty, contains no Chinese characters,
            or parameters are outside valid ranges.
        TTSEngineNotAvailableError: If the TTS engine is not available
            or not properly configured.
        TTSGenerationError: If TTS generation fails due to service
            issues or malformed input.
    
    Example:
        >>> engine = TTSFactory.create_engine('edge')
        >>> audio_data, timings = await engine.generate_speech(
        ...     "你好世界", 
        ...     voice="zh-CN-XiaoxiaoNeural",
        ...     speed=1.2
        ... )
        >>> print(f"Generated {len(audio_data)} bytes of audio")
        >>> print(f"Word timings: {len(timings)} entries")
    
    Note:
        - Text is automatically preprocessed to convert numbers to Chinese
        - Timing precision depends on TTS engine capabilities
        - Large texts may be chunked for optimal processing
    """
```

### **Architecture Decision Records (ADRs)**
Document important architectural decisions.

```markdown
# ADR-001: Choice of TTS Engine Architecture

## Status
Accepted

## Context
FastTTS requires high-quality Chinese text-to-speech with precise word timing
for karaoke-style highlighting. Multiple TTS engines are available with 
different characteristics.

## Decision
Implement a multi-engine architecture with:
- Microsoft Edge TTS as primary engine (free, fast, good timing)
- MiniMax Hailuo TTS as secondary engine (premium quality, custom voices)
- Factory pattern for engine management
- Abstract base class for consistent interface

## Consequences
### Positive
- Flexibility to choose best engine for specific use cases
- Redundancy if one engine becomes unavailable
- Easy addition of new engines in future
- Consistent API regardless of underlying engine

### Negative
- Additional complexity in engine management
- Need to handle different timing formats
- Increased testing surface area

## Implementation Notes
- Use singleton pattern for engine instances to improve performance
- Implement graceful fallback between engines
- Standardize timing data format across engines
```

---

## 🔄 Code Review Guidelines

### **Code Review Checklist**
Standardized checklist for all code reviews.

```markdown
## FastTTS Code Review Checklist

### Security
- [ ] Input validation implemented for all user inputs
- [ ] No hardcoded API keys or credentials
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention in frontend code
- [ ] Error messages don't expose internal details

### Performance
- [ ] Database queries are efficient (check execution plan)
- [ ] Async/await used for I/O operations
- [ ] Memory leaks prevented (proper cleanup)
- [ ] Large data sets handled with pagination/chunking
- [ ] Caching implemented for expensive operations

### Maintainability
- [ ] Code follows established patterns
- [ ] Functions have single responsibility
- [ ] Complex logic is commented
- [ ] Magic numbers replaced with named constants
- [ ] Error handling is comprehensive

### Testing
- [ ] Unit tests cover new functionality
- [ ] Edge cases are tested
- [ ] Mock objects used for external dependencies
- [ ] Integration tests for critical paths
- [ ] Performance tests for critical operations

### Documentation
- [ ] Docstrings follow established format
- [ ] Complex algorithms explained
- [ ] API changes documented
- [ ] Configuration changes noted
```

### **Git Workflow**
Standardized Git workflow for collaboration.

```bash
# Feature development workflow
git checkout main
git pull origin main
git checkout -b feature/new-tts-engine

# Make changes with atomic commits
git add specific_files
git commit -m "feat: add new TTS engine interface

- Implement abstract base class for TTS engines
- Add factory method for engine creation
- Include comprehensive error handling

Closes #123"

# Before merge - rebase and test
git rebase main
npm test  # or python -m pytest
git push origin feature/new-tts-engine

# Create pull request with template
```

---

## 🎯 Best Practices Summary

### **Code Quality Principles**
1. **SOLID Principles**: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
2. **DRY (Don't Repeat Yourself)**: Extract common functionality into reusable components
3. **KISS (Keep It Simple, Stupid)**: Prefer simple solutions over complex ones
4. **YAGNI (You Aren't Gonna Need It)**: Don't build features until they're actually needed
5. **Performance First**: Consider performance implications of architectural decisions

### **Security Guidelines**
1. **Input Validation**: Validate all inputs at system boundaries
2. **Output Encoding**: Properly encode outputs to prevent injection attacks
3. **Least Privilege**: Components should have minimal necessary permissions
4. **Defense in Depth**: Multiple layers of security controls
5. **Secure Defaults**: Default configurations should be secure

### **Performance Guidelines**
1. **Async Programming**: Use async/await for I/O operations
2. **Database Optimization**: Use appropriate indexes and query optimization
3. **Caching Strategy**: Implement multi-level caching where appropriate
4. **Memory Management**: Proper cleanup and garbage collection
5. **Load Testing**: Regular performance testing under realistic loads

### **Maintainability Guidelines**
1. **Modular Architecture**: Clear separation of concerns
2. **Consistent Patterns**: Follow established architectural patterns
3. **Comprehensive Testing**: Unit, integration, and performance tests
4. **Documentation**: Keep documentation current and comprehensive
5. **Code Reviews**: All code changes reviewed by peers

---

*This comprehensive development patterns guide provides the foundation for consistent, high-quality development practices in the FastTTS project, ensuring maintainable, secure, and performant code across all components.*