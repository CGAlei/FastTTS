# FastTTS TTS Engine Architecture Guide

## 📋 TTS System Overview

FastTTS employs a sophisticated multi-engine TTS architecture designed for flexibility, performance, and precision. The system supports multiple TTS providers through a unified interface, each optimized for different use cases and quality requirements.

**Supported Engines**: Microsoft Edge TTS, MiniMax Hailuo TTS  
**Architecture Pattern**: Factory Pattern with Abstract Base Class  
**Key Features**: Word-level timing, Montreal Forced Alignment, Voice customization  
**Performance**: <2s Edge TTS, 2-5s MiniMax with MFA  

---

## 🏗️ Architecture Components

### **Factory Pattern Implementation** (`tts/tts_factory.py`)

The TTS system uses the Factory Pattern to manage engine instantiation and provide a consistent interface across different TTS providers.

```python
class TTSFactory:
    """Factory class for creating TTS engine instances"""
    
    _engines = {
        "edge": EdgeTTSEngine,
        "hailuo": MinimaxTTSEngine,
        "minimax": MinimaxTTSEngine  # Alias for compatibility
    }
    
    _instances = {}  # Singleton pattern for engine instances
```

**Key Features**:
- **Singleton Pattern**: Single instance per engine type
- **Dynamic Loading**: Engines created on first use
- **Error Handling**: Graceful fallback for unavailable engines
- **Configuration Validation**: Real-time engine status checking

### **Abstract Base Class** (`tts/base_tts.py`)

All TTS engines implement the `BaseTTSEngine` interface, ensuring consistent behavior and API compatibility.

```python
class BaseTTSEngine(ABC):
    """Abstract base class for TTS engines"""
    
    @abstractmethod
    async def generate_speech(
        self, 
        text: str, 
        voice: str = None, 
        speed: float = 1.0,
        **kwargs
    ) -> Tuple[bytes, List[Dict[str, Any]]]:
        """Generate speech with word-level timing data"""
        pass
```

**Required Methods**:
- `generate_speech()`: Core TTS generation with timing
- `get_supported_voices()`: Available voice configurations
- `validate_voice()`: Voice ID validation
- `clean_text()`: Engine-specific text preprocessing

---

## 🎙️ Microsoft Edge TTS Engine (`tts/edge_tts_engine.py`)

### **Engine Characteristics**
- **Provider**: Microsoft Cognitive Services
- **Speed**: Fast (~1-2 seconds for typical texts)
- **Timing**: Native word boundary support
- **Voices**: 8 Chinese neural voices with regional variants
- **Cost**: Free (rate-limited)
- **Quality**: High-quality neural synthesis

### **Core Implementation**

#### **Speech Generation Process**
```python
async def generate_speech(
    self, 
    text: str, 
    voice: str = None, 
    speed: float = 1.0,
    volume: float = 0.8,
    **kwargs
) -> Tuple[bytes, List[Dict[str, Any]]]:
    """Generate speech using Edge TTS with word-level timing"""
    
    # Voice validation
    if not self.validate_voice(voice):
        raise ValueError(f"Unsupported voice: {voice}")
    
    # Parameter conversion for Edge TTS format
    rate = self._convert_speed_to_rate(speed)
    volume_str = self._convert_volume_to_edge_format(volume)
    
    # Create Edge TTS communication object
    communicate = edge_tts.Communicate(text, voice, rate=rate, volume=volume_str)
    
    audio_chunks = []
    word_timings = []
    
    # Stream processing for real-time data
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_chunks.append(chunk["data"])
        elif chunk["type"] == "WordBoundary":
            word_data = {
                "word": chunk["text"],
                "start_time": chunk["offset"] / 10000,  # 100ns to ms
                "end_time": (chunk["offset"] + chunk["duration"]) / 10000,
                "offset": chunk["offset"] / 10000,
                "duration": chunk["duration"] / 10000
            }
            word_timings.append(word_data)
    
    return b''.join(audio_chunks), word_timings
```

#### **Supported Voice Configurations**
```python
self.supported_voices = [
    {"id": "zh-CN-XiaoxiaoNeural", "name": "Microsoft Xiaoxiao (Female)", "language": "zh-CN"},
    {"id": "zh-CN-XiaoyiNeural", "name": "Microsoft Xiaoyi (Female)", "language": "zh-CN"},
    {"id": "zh-CN-YunjianNeural", "name": "Microsoft Yunjian (Male)", "language": "zh-CN"},
    {"id": "zh-CN-YunxiNeural", "name": "Microsoft Yunxi (Male)", "language": "zh-CN"},
    {"id": "zh-CN-YunxiaNeural", "name": "Microsoft Yunxia (Female)", "language": "zh-CN"},
    {"id": "zh-CN-YunyangNeural", "name": "Microsoft Yunyang (Male)", "language": "zh-CN"},
    {"id": "zh-CN-liaoning-XiaobeiNeural", "name": "Microsoft Xiaobei (Female - Northeastern)", "language": "zh-CN"},
    {"id": "zh-CN-shaanxi-XiaoniNeural", "name": "Microsoft Xiaoni (Female - Shaanxi)", "language": "zh-CN"}
]
```

#### **Parameter Conversion Functions**
```python
def _convert_speed_to_rate(self, speed: float) -> str:
    """Convert numeric speed to Edge TTS rate format"""
    if speed <= 0.5:
        return "-50%"
    elif speed >= 2.0:
        return "+100%"
    else:
        # Convert 1.0 = 0%, 1.5 = +50%, 0.8 = -20%
        percentage = int((speed - 1.0) * 100)
        return f"{percentage:+d}%"

def _convert_volume_to_edge_format(self, volume: float) -> str:
    """Convert numeric volume to Edge TTS volume format"""
    if volume <= 0.0:
        return "-100%"
    elif volume >= 2.0:
        return "+100%"
    else:
        # Convert 1.0 = 0%, 1.5 = +50%, 0.5 = -50%
        percentage = int((volume - 1.0) * 100)
        return f"{percentage:+d}%"
```

### **Performance Characteristics**
- **Average Generation Time**: 1-2 seconds
- **Word Timing Accuracy**: ±10ms (native boundary detection)
- **Maximum Text Length**: ~1000 characters per request
- **Rate Limiting**: ~60 requests per minute
- **Audio Quality**: 24kHz 16-bit MP3

---

## 🚀 MiniMax Hailuo TTS Engine (`tts/minimax_tts_engine.py`)

### **Engine Characteristics**
- **Provider**: MiniMax AI (China)
- **Speed**: Moderate (2-5 seconds depending on text length)
- **Timing**: Montreal Forced Alignment (MFA) for precise word timing
- **Voices**: Custom voice cloning and premium neural voices
- **Cost**: API-based pricing
- **Quality**: Superior custom voice quality and emotional expression

### **Core Implementation**

#### **Configuration and Credentials**
```python
def __init__(self):
    super().__init__("MiniMax Hailuo")
    self.base_url = "https://api.minimax.io/v1/t2a_v2"
    
    # Load credentials from environment
    self._load_credentials()
    
    # Chunking configuration for long texts
    self.chunk_size_words = int(os.getenv("MINIMAX_CHUNK_SIZE", "120"))
    
    # Rate limiting
    self.max_requests_per_minute = 55
    self.request_timestamps = []

def _load_credentials(self):
    """Load credentials and settings from environment variables"""
    self.api_key = os.getenv("MINIMAX_API_KEY")
    self.group_id = os.getenv("MINIMAX_GROUP_ID")
    self.custom_voice_id = os.getenv("MINIMAX_CUSTOM_VOICE_ID", "")
    self.preferred_model = os.getenv("MINIMAX_MODEL", "speech-02-turbo")
```

#### **Speech Generation with Chunking**
```python
async def generate_speech(
    self, 
    text: str, 
    voice: str = None, 
    speed: float = 1.0,
    volume: float = 0.8,
    **kwargs
) -> Tuple[bytes, List[Dict[str, Any]]]:
    """Generate speech using MiniMax API with chunking and MFA"""
    
    if not self.is_configured():
        raise RuntimeError("MiniMax TTS engine not configured")
    
    # Use custom voice if available, otherwise default
    actual_voice = self.custom_voice_id if self.custom_voice_id else voice
    
    # Text chunking for long content
    chunks = self._chunk_text(text, self.chunk_size_words)
    
    # Progress tracking
    session_id = self._start_progress_tracking(len(chunks))
    
    try:
        all_audio_bytes = []
        all_word_timings = []
        cumulative_time_offset = 0.0
        
        for i, chunk in enumerate(chunks):
            # Update progress
            self._update_progress(session_id, i + 1, f"Processing chunk {i+1} of {len(chunks)}")
            
            # Generate audio for chunk
            audio_bytes = await self._generate_chunk_audio(chunk, actual_voice, speed)
            all_audio_bytes.append(audio_bytes)
            
            # Generate timing data using MFA
            if self._mfa_available():
                chunk_timings = await self._extract_word_timings_mfa(audio_bytes, chunk)
                
                # Adjust timing offsets for multi-chunk texts
                for timing in chunk_timings:
                    timing['start_time'] += cumulative_time_offset
                    timing['end_time'] += cumulative_time_offset
                
                all_word_timings.extend(chunk_timings)
                
                # Update cumulative offset
                if chunk_timings:
                    cumulative_time_offset = chunk_timings[-1]['end_time']
            else:
                # Fallback timing estimation
                estimated_timings = self._estimate_word_timings(chunk, cumulative_time_offset)
                all_word_timings.extend(estimated_timings)
                cumulative_time_offset += len(chunk) * 0.15  # Estimate 150ms per character
        
        # Combine audio chunks
        combined_audio = self._combine_audio_chunks(all_audio_bytes)
        
        return combined_audio, all_word_timings
        
    finally:
        self._complete_progress_tracking(session_id)
```

#### **Montreal Forced Alignment Integration**
```python
async def _extract_word_timings_mfa(self, audio_bytes: bytes, text: str) -> List[Dict[str, Any]]:
    """Extract precise word timings using Montreal Forced Alignment"""
    try:
        from alignment import MFAAligner
        aligner = MFAAligner()
        
        if not aligner.is_available:
            logger.warning("MFA not available, falling back to estimation")
            return self._estimate_word_timings(text, 0.0)
        
        # Save audio to temporary file
        temp_audio_path = self._save_temp_audio(audio_bytes)
        
        # Perform forced alignment
        alignment_result = await aligner.align_text_audio(text, temp_audio_path)
        
        # Convert MFA output to FastTTS timing format
        word_timings = []
        for word_info in alignment_result['words']:
            word_timings.append({
                'word': word_info['word'],
                'start_time': word_info['start_time'],
                'end_time': word_info['end_time'],
                'confidence': word_info.get('confidence', 1.0)
            })
        
        return word_timings
        
    except Exception as e:
        logger.error(f"MFA alignment failed: {e}")
        return self._estimate_word_timings(text, 0.0)
```

#### **Text Chunking Strategy**
```python
def _chunk_text(self, text: str, chunk_size_words: int) -> List[str]:
    """Intelligent text chunking for optimal TTS processing"""
    import jieba  # Chinese word segmentation
    
    # Segment text into words
    words = list(jieba.cut(text, cut_all=False))
    
    chunks = []
    current_chunk = []
    current_word_count = 0
    
    for word in words:
        # Check for natural break points (punctuation)
        if current_word_count >= chunk_size_words and word in ['。', '！', '？', '；']:
            current_chunk.append(word)
            chunks.append(''.join(current_chunk))
            current_chunk = []
            current_word_count = 0
        elif current_word_count >= chunk_size_words * 1.2:  # Hard limit
            chunks.append(''.join(current_chunk))
            current_chunk = [word]
            current_word_count = 1
        else:
            current_chunk.append(word)
            current_word_count += 1
    
    # Add remaining words
    if current_chunk:
        chunks.append(''.join(current_chunk))
    
    return chunks
```

### **Supported Models and Voices**
```python
self.supported_models = [
    {"id": "speech-02-turbo", "name": "Speech-02 Turbo", "description": "Enhanced multilingual with low latency"},
    {"id": "speech-02-hd", "name": "Speech-02 HD", "description": "Superior quality with outstanding rhythm"},
    {"id": "speech-01-turbo", "name": "Speech-01 Turbo", "description": "Excellent performance and low latency"},
    {"id": "speech-01-hd", "name": "Speech-01 HD", "description": "Rich voices with expressive emotions"}
]

self.supported_voices = [
    {"id": "moss_audio_96a80421-22ea-11f0-92db-0e8893cbb430", "name": "Aria (Custom Female)", "type": "custom"},
    {"id": "moss_audio_afeaf743-22e7-11f0-b934-42db1b8d9b3b", "name": "Kevin (Custom Male)", "type": "custom"},
    {"id": "Chinese (Mandarin)_Lyrical_Voice", "name": "Liyue (Lyrical Voice)", "type": "custom"},
    {"id": "Chinese (Mandarin)_Gentleman", "name": "Willi (Gentleman)", "type": "custom"}
]
```

### **Rate Limiting and Performance**
```python
async def _check_rate_limit(self):
    """Implement rate limiting for MiniMax API"""
    current_time = time.time()
    
    # Remove timestamps older than 1 minute
    self.request_timestamps = [
        ts for ts in self.request_timestamps 
        if current_time - ts < 60
    ]
    
    # Check if we're at the limit
    if len(self.request_timestamps) >= self.max_requests_per_minute:
        wait_time = 60 - (current_time - self.request_timestamps[0])
        logger.info(f"Rate limit reached, waiting {wait_time:.1f} seconds")
        await asyncio.sleep(wait_time)
    
    # Record this request
    self.request_timestamps.append(current_time)
```

---

## 🔧 Engine Configuration and Management

### **Factory Methods**

#### **Engine Creation**
```python
@classmethod
def create_engine(cls, engine_type: str) -> BaseTTSEngine:
    """Create TTS engine instance with validation"""
    engine_type = engine_type.lower()
    
    if engine_type not in cls._engines:
        supported = ", ".join(cls._engines.keys())
        raise ValueError(f"Unsupported TTS engine: {engine_type}. Supported: {supported}")
    
    # Singleton pattern for efficiency
    if engine_type not in cls._instances:
        cls._instances[engine_type] = cls._engines[engine_type]()
    
    return cls._instances[engine_type]
```

#### **Engine Information**
```python
@classmethod
def get_supported_engines(cls) -> Dict[str, Dict[str, Any]]:
    """Get comprehensive engine information"""
    engines_info = {}
    
    for engine_type, engine_class in cls._engines.items():
        try:
            engine = cls.create_engine(engine_type)
            engines_info[engine_type] = {
                "name": engine.name,
                "voices": engine.get_supported_voices(),
                "default_voice": engine.get_default_voice(),
                "available": True,
                "configured": getattr(engine, 'is_configured', lambda: True)()
            }
        except Exception as e:
            engines_info[engine_type] = {
                "name": engine_class.__name__,
                "available": False,
                "error": str(e)
            }
    
    return engines_info
```

### **Configuration Validation**
```python
@classmethod
def validate_engine_config(cls, engine_type: str) -> Dict[str, Any]:
    """Comprehensive engine configuration validation"""
    try:
        engine = cls.create_engine(engine_type)
        
        result = {
            "valid": True,
            "engine": engine.name,
            "voices_count": len(engine.get_supported_voices()),
            "default_voice": engine.get_default_voice()
        }
        
        # Check engine-specific configuration
        if hasattr(engine, 'is_configured'):
            result["configured"] = engine.is_configured()
            if not result["configured"]:
                result["valid"] = False
                result["error"] = "Engine credentials not configured"
        
        return result
        
    except Exception as e:
        return {"valid": False, "error": str(e)}
```

---

## 📊 Progress Tracking and Monitoring (`progress_manager.py`)

### **Progress Management System**
The TTS system includes comprehensive progress tracking for real-time user feedback, especially important for longer MiniMax processing.

```python
class ProgressManager:
    def __init__(self):
        self.active_sessions = {}
        self.cleanup_interval = 300  # 5 minutes
    
    def start_session(self, session_id: str, total_chunks: int):
        """Initialize progress tracking for TTS session"""
        self.active_sessions[session_id] = {
            'current_chunk': 0,
            'total_chunks': total_chunks,
            'percentage': 0,
            'status': 'starting',
            'message': 'Initializing TTS generation...',
            'start_time': time.time(),
            'last_update': time.time()
        }
    
    def update_progress(self, session_id: str, current_chunk: int, message: str = None):
        """Update progress for active session"""
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        session['current_chunk'] = current_chunk
        session['percentage'] = int((current_chunk / session['total_chunks']) * 100)
        session['status'] = 'processing'
        session['message'] = message or f"Processing chunk {current_chunk} of {session['total_chunks']}"
        session['last_update'] = time.time()
```

### **Server-Sent Events Integration**
```python
async def tts_progress_stream(session_id: str):
    """SSE endpoint for real-time progress updates"""
    
    async def generate_sse_response():
        # Send initial connection
        yield f"data: {json.dumps({'type': 'connected', 'session_id': session_id})}\n\n"
        
        while True:
            session_data = progress_manager.get_session_progress(session_id)
            if not session_data:
                yield f"data: {json.dumps({'type': 'session_ended'})}\n\n"
                break
            
            # Send progress update
            event_data = {
                'type': 'progress_update',
                'session_id': session_id,
                'current_chunk': session_data['current_chunk'],
                'total_chunks': session_data['total_chunks'],
                'percentage': session_data['percentage'],
                'status': session_data['status'],
                'message': session_data['message']
            }
            yield f"data: {json.dumps(event_data)}\n\n"
            
            if session_data['status'] in ['completed', 'error']:
                break
            
            await asyncio.sleep(0.5)  # Update every 500ms
    
    return StreamingResponse(generate_sse_response(), media_type="text/event-stream")
```

---

## 🎯 Timing Data Format and Standards

### **Unified Timing Format**
All TTS engines return timing data in a standardized format for frontend consumption:

```python
# Standard word timing format
{
    "word": "世界",              # Chinese word/character
    "start_time": 1.200,        # Start time in seconds (float)
    "end_time": 1.650,          # End time in seconds (float)
    "wordId": "word_3",         # Unique identifier for frontend
    "wordIndex": 3,             # Position in text (0-based)
    "hasVocabulary": true,      # Vocabulary database status
    "vocabularySource": "database", # Source: "database", "ai_generated", "unknown"
    "confidence": 0.95          # Timing confidence (MFA only)
}
```

### **Timing Accuracy Comparison**

| Engine | Method | Accuracy | Typical Precision | Processing Time |
|--------|--------|----------|------------------|----------------|
| Edge TTS | Native word boundaries | High | ±10ms | <1s |
| MiniMax + MFA | Forced alignment | Very High | ±5ms | 2-5s |
| MiniMax (fallback) | Character estimation | Moderate | ±50ms | 2-3s |

### **Frontend Integration**
```javascript
// Karaoke highlighting integration
function processTimingData(wordData) {
    return wordData.map((word, index) => ({
        ...word,
        wordId: `word_${index}`,
        wordIndex: index,
        // Add frontend-specific properties
        highlighted: false,
        hasVocabulary: checkVocabularyStatus(word.word)
    }));
}
```

---

## 🔄 Montreal Forced Alignment (MFA) Integration

### **MFA System Overview**
Montreal Forced Alignment provides millisecond-precise word timing by analyzing the relationship between text and generated audio.

```python
# MFA Integration Module (alignment/mfa_aligner.py)
class MFAAligner:
    def __init__(self):
        self.model_path = "models/chinese_cv"
        self.dictionary_path = "models/chinese_dict.txt"
        self.is_available = self._check_mfa_installation()
    
    async def align_text_audio(self, text: str, audio_path: str) -> Dict[str, Any]:
        """Perform forced alignment on text and audio"""
        
        # Prepare text for MFA (segmentation)
        segmented_text = self._prepare_text_for_mfa(text)
        
        # Create temporary files for MFA
        text_file = self._create_temp_text_file(segmented_text)
        
        # Run MFA alignment
        alignment_result = await self._run_mfa_alignment(text_file, audio_path)
        
        # Parse and format results
        return self._parse_mfa_output(alignment_result)
```

### **MFA Configuration**
```yaml
# MFA environment configuration (environment.yml)
name: fasttts-mfa
dependencies:
  - python=3.10
  - montreal-forced-aligner=3.2.3
  - kaldi
  - openfst
  - ffmpeg
  - sox
```

### **Chinese Language Support**
```python
def _prepare_text_for_mfa(self, text: str) -> str:
    """Prepare Chinese text for MFA processing"""
    import jieba
    
    # Segment text using jieba
    words = jieba.cut(text, cut_all=False)
    
    # Convert to space-separated format required by MFA
    segmented = ' '.join(words)
    
    # Handle punctuation for better alignment
    segmented = re.sub(r'([。！？；，])', r' \1 ', segmented)
    
    return segmented.strip()
```

---

## 📈 Performance Optimization Strategies

### **Edge TTS Optimizations**
```python
# Connection pooling for Edge TTS
class EdgeTTSPool:
    def __init__(self, max_concurrent=3):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.request_queue = asyncio.Queue()
    
    async def generate_with_pooling(self, text, voice, speed, volume):
        async with self.semaphore:
            return await self._generate_internal(text, voice, speed, volume)
```

### **MiniMax Optimizations**
```python
# Intelligent chunking for MiniMax
def _optimize_chunk_size(self, text: str) -> int:
    """Dynamic chunk size based on text characteristics"""
    
    # Shorter chunks for complex text with many punctuation marks
    punctuation_density = len(re.findall(r'[。！？；，]', text)) / len(text)
    
    if punctuation_density > 0.05:  # High punctuation density
        return min(80, self.chunk_size_words)
    elif len(text) > 500:  # Long text
        return min(150, self.chunk_size_words)
    else:
        return self.chunk_size_words
```

### **Memory Management**
```python
# Cleanup strategies for large audio files
class AudioMemoryManager:
    def __init__(self, max_cache_size=100 * 1024 * 1024):  # 100MB
        self.cache = {}
        self.max_size = max_cache_size
        self.current_size = 0
    
    def cache_audio(self, session_id: str, audio_data: bytes):
        """Cache audio with automatic cleanup"""
        if self.current_size + len(audio_data) > self.max_size:
            self._cleanup_oldest()
        
        self.cache[session_id] = {
            'data': audio_data,
            'timestamp': time.time(),
            'size': len(audio_data)
        }
        self.current_size += len(audio_data)
```

---

## 🔧 Extension and Customization

### **Adding New TTS Engines**
```python
# Template for new TTS engine implementation
class NewTTSEngine(BaseTTSEngine):
    def __init__(self):
        super().__init__("New TTS Engine")
        self.default_voice = "default_voice_id"
        self.supported_voices = [
            {"id": "voice1", "name": "Voice 1", "language": "zh-CN"}
        ]
    
    async def generate_speech(self, text, voice=None, speed=1.0, **kwargs):
        """Implement engine-specific TTS generation"""
        # 1. Validate parameters
        # 2. Call external TTS API/service
        # 3. Process audio and timing data
        # 4. Return standardized format
        pass
    
    def get_supported_voices(self):
        return self.supported_voices.copy()
    
    def validate_voice(self, voice_id):
        return any(v["id"] == voice_id for v in self.supported_voices)

# Register new engine in factory
TTSFactory._engines["new_engine"] = NewTTSEngine
```

### **Custom Voice Configuration**
```python
# Engine-specific voice management
class VoiceManager:
    def __init__(self, engine):
        self.engine = engine
        self.custom_voices = {}
    
    def add_custom_voice(self, voice_id: str, voice_config: dict):
        """Add custom voice configuration"""
        self.custom_voices[voice_id] = voice_config
        self.engine.supported_voices.append({
            "id": voice_id,
            "name": voice_config["display_name"],
            "language": voice_config["language"],
            "type": "custom"
        })
```

### **Timing Enhancement Modules**
```python
# Post-processing timing enhancement
class TimingEnhancer:
    def __init__(self):
        self.enhancement_methods = {
            'mfa': self._enhance_with_mfa,
            'ml_model': self._enhance_with_ml,
            'statistical': self._enhance_statistical
        }
    
    async def enhance_timing(self, audio_data: bytes, text: str, 
                           raw_timings: list, method: str = 'mfa') -> list:
        """Enhance timing accuracy using specified method"""
        if method in self.enhancement_methods:
            return await self.enhancement_methods[method](audio_data, text, raw_timings)
        return raw_timings
```

---

## 📊 Monitoring and Diagnostics

### **Engine Health Monitoring**
```python
class TTSHealthMonitor:
    def __init__(self):
        self.metrics = {
            'requests_total': 0,
            'requests_success': 0,
            'requests_failed': 0,
            'average_response_time': 0.0,
            'engine_availability': {}
        }
    
    async def check_engine_health(self, engine_type: str) -> Dict[str, Any]:
        """Comprehensive engine health check"""
        try:
            engine = TTSFactory.create_engine(engine_type)
            
            # Test basic functionality
            test_text = "测试"
            start_time = time.time()
            
            audio_data, timings = await engine.generate_speech(test_text)
            
            response_time = time.time() - start_time
            
            return {
                'engine': engine_type,
                'status': 'healthy',
                'response_time': response_time,
                'audio_size': len(audio_data),
                'timing_count': len(timings),
                'configured': getattr(engine, 'is_configured', lambda: True)()
            }
            
        except Exception as e:
            return {
                'engine': engine_type,
                'status': 'unhealthy',
                'error': str(e)
            }
```

### **Performance Metrics Collection**
```python
# TTS performance tracking
class TTSMetrics:
    def __init__(self):
        self.session_metrics = {}
    
    def record_generation(self, engine: str, text_length: int, 
                         processing_time: float, success: bool):
        """Record TTS generation metrics"""
        if engine not in self.session_metrics:
            self.session_metrics[engine] = {
                'total_requests': 0,
                'successful_requests': 0,
                'total_processing_time': 0.0,
                'total_text_length': 0,
                'average_chars_per_second': 0.0
            }
        
        metrics = self.session_metrics[engine]
        metrics['total_requests'] += 1
        metrics['total_text_length'] += text_length
        metrics['total_processing_time'] += processing_time
        
        if success:
            metrics['successful_requests'] += 1
        
        # Calculate performance metrics
        if metrics['total_processing_time'] > 0:
            metrics['average_chars_per_second'] = (
                metrics['total_text_length'] / metrics['total_processing_time']
            )
```

---

*This comprehensive guide provides the complete TTS engine architecture for AI coding assistants working with FastTTS. The multi-engine design ensures flexibility, performance, and extensibility for diverse TTS requirements.*