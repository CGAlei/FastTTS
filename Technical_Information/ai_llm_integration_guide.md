# FastTTS AI/LLM Integration Guide

## 📋 AI System Overview

FastTTS integrates advanced AI/LLM capabilities for intelligent vocabulary expansion and contextual learning. The system employs a dual-provider architecture with automatic fallback mechanisms to ensure reliable AI-powered definition generation and vocabulary enhancement.

**Primary Provider**: OpenRouter (multiple models available)  
**Fallback Provider**: OpenAI GPT-4o-mini  
**Architecture**: Factory pattern with provider abstraction  
**Integration**: Real-time vocabulary generation with database persistence  
**Response Format**: Structured JSON with comprehensive linguistic data  

---

## 🏗️ AI Architecture Components

### **LLM Manager** (`llm_manager.py`)

The LLM Manager serves as the central orchestrator for all AI operations, managing multiple LLM providers and handling service availability, fallback logic, and error recovery.

```python
class LLMManager:
    """
    Centralized manager for LLM services with automatic fallback.
    Handles API key validation, service initialization, and error recovery.
    """
    
    def __init__(self):
        self.primary_service = None      # OpenRouter service
        self.fallback_service = None     # OpenAI service
        self._init_services()
```

**Key Features**:
- **Dual Provider Support**: Primary (OpenRouter) + Fallback (OpenAI)
- **Automatic Failover**: Seamless switching between providers
- **Service Health Monitoring**: Real-time availability checking
- **Configuration Management**: Environment-based API key handling

### **Provider Architecture** (`llm/llm_provider.py`)

All LLM services implement a common interface ensuring consistent behavior and interchangeability.

```python
class LLMProvider(ABC):
    """Abstract base class for LLM service providers"""
    
    @abstractmethod
    def get_definition(self, word: str) -> Dict[str, str]:
        """Generate comprehensive word definition"""
        pass
    
    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Check service availability"""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return provider identification"""
        pass
```

---

## 🌐 OpenRouter Service Integration (`llm/openrouter_service.py`)

### **Service Characteristics**
- **Provider**: OpenRouter.ai (Multi-model aggregator)
- **Primary Model**: GPT-4o-mini (configurable)
- **Cost**: Pay-per-token pricing with model selection
- **Features**: Access to multiple LLM providers through single API
- **Reliability**: High availability with distributed infrastructure

### **Core Implementation**

#### **Service Initialization**
```python
class OpenRouterService(LLMProvider):
    def __init__(self, api_key: str, config=None):
        self._api_key = api_key
        self._model = "gpt-4o-mini"  # Default model
        self._base_url = "https://openrouter.ai/api/v1"
        self._available = False
        
        # Verify connection on initialization
        try:
            self._verify_connection()
            self._available = True
        except Exception as e:
            logger.error(f"OpenRouter initialization failed: {e}")
            raise

def _verify_connection(self):
    """Verify API key and service connectivity"""
    headers = {
        "Authorization": f"Bearer {self._api_key}",
        "HTTP-Referer": "https://github.com/yourusername/your-repo",
        "X-Title": "Chinese Vocabulary Meaning"
    }
    
    response = requests.get(f"{self._base_url}/models", headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to connect to OpenRouter: {response.text}")
```

#### **Definition Generation Process**
```python
def get_definition(self, word: str) -> Dict[str, str]:
    """Generate structured vocabulary definition using OpenRouter"""
    
    if not self.is_available:
        raise Exception("OpenRouter service is not available")
    
    # Prepare structured function calling payload
    payload = {
        "model": self._model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant specialized in Chinese language."},
            {"role": "user", "content": f"Please provide information about the Chinese word: {word}"}
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "get_word_information",
                    "description": "Get comprehensive information about a Chinese word",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "spanish_meaning": {
                                "type": "string",
                                "description": "The Spanish translation/meaning of the word"
                            },
                            "pinyin": {
                                "type": "string", 
                                "description": "The Pinyin pronunciation of the word"
                            },
                            "chinese_meaning": {
                                "type": "string",
                                "description": "The definition of the word in Chinese simplified"
                            },
                            "word_type": {
                                "type": "string",
                                "description": "The grammatical type (名词, 动词, 形容词, etc.)"
                            },
                            "synonyms": {
                                "type": "string",
                                "description": "Synonyms in Chinese (comma separated)"
                            },
                            "antonyms": {
                                "type": "string", 
                                "description": "Antonyms in Chinese (comma separated)"
                            },
                            "usage_example": {
                                "type": "string",
                                "description": "Example sentence using the word in Chinese"
                            }
                        },
                        "required": ["spanish_meaning", "pinyin", "chinese_meaning"]
                    }
                }
            }
        ],
        "tool_choice": {"type": "function", "function": {"name": "get_word_information"}}
    }
    
    # Make API request
    response = requests.post(
        f"{self._base_url}/chat/completions",
        headers=self._get_headers(),
        json=payload
    )
    
    if response.status_code != 200:
        raise Exception(f"OpenRouter API error: {response.text}")
    
    # Extract structured response
    result = response.json()
    tool_calls = result["choices"][0]["message"].get("tool_calls", [])
    
    if not tool_calls:
        raise Exception("No tool calls in response")
    
    return json.loads(tool_calls[0]["function"]["arguments"])
```

### **Request Headers Configuration**
```python
def _get_headers(self) -> Dict[str, str]:
    """Generate required headers for OpenRouter API"""
    return {
        "Authorization": f"Bearer {self._api_key}",
        "HTTP-Referer": "https://github.com/yourusername/your-repo",  # Required
        "X-Title": "Chinese Vocabulary Indexer",  # App identification
        "Content-Type": "application/json"
    }
```

---

## 🤖 OpenAI Service Integration (`llm/openai_service.py`)

### **Service Characteristics**
- **Provider**: OpenAI (Direct API)
- **Model**: GPT-4o-mini (optimized for cost/performance)
- **Role**: Fallback service for reliability
- **Features**: Native OpenAI SDK integration
- **Reliability**: High-availability primary LLM provider

### **Core Implementation**

#### **Service Initialization with Validation**
```python
class OpenAIService(LLMProvider):
    def __init__(self, api_key: str, config=None):
        self._api_key = api_key
        self._model = "gpt-4o-mini"
        self._available = False
        
        try:
            # Test API key validity with models.list()
            client = OpenAI(api_key=api_key)
            client.models.list()  # Will raise exception if key invalid
            
            self.client = client
            self._available = True
            logger.info("OpenAI service initialized successfully")
            
        except Exception as e:
            logger.error(f"OpenAI API key validation failed: {e}")
            self._available = False
            raise
```

#### **Definition Generation with OpenAI SDK**
```python
def get_definition(self, word: str) -> Dict[str, str]:
    """Generate vocabulary definition using OpenAI GPT-4o-mini"""
    
    if not self.is_available:
        raise Exception("OpenAI service is not available")
    
    try:
        # Use OpenAI's function calling feature for structured responses
        response = self.client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant specialized in Chinese language."},
                {"role": "user", "content": f"Please provide information about the Chinese word: {word}"}
            ],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "get_word_information",
                        "description": "Get comprehensive information about a Chinese word",
                        "parameters": {
                            # Same schema as OpenRouter for consistency
                            "type": "object",
                            "properties": {
                                "spanish_meaning": {"type": "string", "description": "Spanish translation"},
                                "pinyin": {"type": "string", "description": "Pinyin pronunciation"},
                                "chinese_meaning": {"type": "string", "description": "Chinese definition"},
                                "word_type": {"type": "string", "description": "Grammar type"},
                                "synonyms": {"type": "string", "description": "Chinese synonyms"},
                                "antonyms": {"type": "string", "description": "Chinese antonyms"},
                                "usage_example": {"type": "string", "description": "Example sentence"}
                            },
                            "required": ["spanish_meaning", "pinyin", "chinese_meaning"]
                        }
                    }
                }
            ],
            tool_choice={"type": "function", "function": {"name": "get_word_information"}}
        )
        
        # Extract function call results
        tool_calls = response.choices[0].message.tool_calls
        if not tool_calls:
            raise Exception("No tool calls in OpenAI response")
        
        return json.loads(tool_calls[0].function.arguments)
        
    except Exception as e:
        logger.error(f"OpenAI definition generation failed: {e}")
        raise
```

---

## 🔄 Service Management and Fallback Logic

### **Dual Provider Workflow** (`llm_manager.py`)

The LLM Manager implements sophisticated fallback logic to ensure reliable vocabulary generation even when primary services are unavailable.

```python
def get_word_definition(self, word: str) -> Dict[str, str]:
    """
    Get comprehensive word definition using available LLM services
    Implements primary → fallback → error progression
    """
    if not word or not word.strip():
        raise ValueError("Word cannot be empty")
    
    word = word.strip()
    
    # Primary service attempt (OpenRouter)
    if self.primary_service and self.primary_service.is_available:
        try:
            logger.info(f"Attempting definition generation with OpenRouter for: {word}")
            result = self.primary_service.get_definition(word)
            logger.info(f"OpenRouter successfully generated definition for: {word}")
            return result
        except Exception as e:
            logger.warning(f"OpenRouter failed for word '{word}': {e}")
    
    # Fallback service attempt (OpenAI)
    if self.fallback_service and self.fallback_service.is_available:
        try:
            logger.info(f"Attempting definition generation with OpenAI for: {word}")
            result = self.fallback_service.get_definition(word)
            logger.info(f"OpenAI successfully generated definition for: {word}")
            return result
        except Exception as e:
            logger.error(f"OpenAI also failed for word '{word}': {e}")
    
    # Both services failed
    raise Exception("All LLM services are unavailable or failed to generate definition")
```

### **Service Health Monitoring**
```python
def is_available(self) -> bool:
    """Check if at least one LLM service is operational"""
    return (self.primary_service and self.primary_service.is_available) or \
           (self.fallback_service and self.fallback_service.is_available)

def get_service_status(self) -> Dict[str, Any]:
    """Comprehensive service status for monitoring and debugging"""
    return {
        'primary_service': {
            'name': self.primary_service.provider_name if self.primary_service else None,
            'available': self.primary_service.is_available if self.primary_service else False,
            'model': self.primary_service.model_name if self.primary_service else None
        },
        'fallback_service': {
            'name': self.fallback_service.provider_name if self.fallback_service else None,
            'available': self.fallback_service.is_available if self.fallback_service else False,
            'model': self.fallback_service.model_name if self.fallback_service else None
        },
        'overall_available': self.is_available()
    }
```

---

## 📊 Structured Response Format

### **AI Definition Schema**
All LLM providers return vocabulary data in a standardized format for consistent database integration:

```json
{
    "spanish_meaning": "mundo",
    "pinyin": "shìjiè", 
    "chinese_meaning": "整个地球；全球",
    "word_type": "名词",
    "synonyms": "地球, 全球",
    "antonyms": "无",
    "usage_example": "世界很大，我想去看看。"
}
```

### **Field Specifications**

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `spanish_meaning` | string | ✓ | Primary Spanish translation | "mundo" |
| `pinyin` | string | ✓ | Romanized pronunciation with tones | "shìjiè" |
| `chinese_meaning` | string | ✓ | Chinese definition/explanation | "整个地球；全球" |
| `word_type` | string | ✗ | Grammatical classification | "名词" |
| `synonyms` | string | ✗ | Comma-separated Chinese synonyms | "地球, 全球" |
| `antonyms` | string | ✗ | Comma-separated Chinese antonyms | "无" |
| `usage_example` | string | ✗ | Contextual example sentence | "世界很大，我想去看看。" |

### **Database Integration Process**
```python
def insert_vocabulary_word(definition_data: dict) -> bool:
    """Insert AI-generated definition into vocabulary database"""
    
    # Prepare data with FastTTS extensions
    word_data = {
        'word': definition_data.get('word', ''),
        'pinyin': definition_data.get('pinyin', ''),
        'spanish_meaning': definition_data.get('spanish_meaning', ''),
        'chinese_meaning': definition_data.get('chinese_meaning', ''),
        'word_type': definition_data.get('word_type', ''),
        'synonyms': definition_data.get('synonyms', '无'),
        'antonyms': definition_data.get('antonyms', '无'),
        'usage_example': definition_data.get('usage_example', ''),
        'updated_at': datetime.now().isoformat(),
        'filename': 'AI_Generated',  # Source tracking
        'length': len(definition_data.get('word', ''))
    }
    
    # Database insertion with UPSERT logic
    cursor.execute("""
        INSERT OR REPLACE INTO vocabulary (
            ChineseWord, PinyinPronunciation, SpanishMeaning,
            ChineseMeaning, WordType, Sinonims, Antonims,
            UsageExample, UpdatedAt, filename, length
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, tuple(word_data.values()))
```

---

## 🔄 Function Calling Implementation

### **OpenAI Function Calling**
Both providers use OpenAI's function calling standard for structured output generation:

```python
# Function schema definition (consistent across providers)
WORD_INFORMATION_FUNCTION = {
    "type": "function",
    "function": {
        "name": "get_word_information",
        "description": "Get comprehensive information about a Chinese word",
        "parameters": {
            "type": "object",
            "properties": {
                "spanish_meaning": {
                    "type": "string",
                    "description": "The Spanish translation/meaning of the word"
                },
                "pinyin": {
                    "type": "string",
                    "description": "The Pinyin pronunciation with tone marks"
                },
                "chinese_meaning": {
                    "type": "string", 
                    "description": "The definition in Chinese simplified characters"
                },
                "word_type": {
                    "type": "string",
                    "description": "Grammatical type (名词, 动词, 形容词, 副词, etc.)"
                },
                "synonyms": {
                    "type": "string",
                    "description": "Synonyms in Chinese, comma separated"
                },
                "antonyms": {
                    "type": "string",
                    "description": "Antonyms in Chinese, comma separated"
                },
                "usage_example": {
                    "type": "string",
                    "description": "Example sentence using the word in context"
                }
            },
            "required": ["spanish_meaning", "pinyin", "chinese_meaning"]
        }
    }
}
```

### **Response Processing Pattern**
```python
def process_function_call_response(response_data: dict) -> dict:
    """Extract and validate function call results"""
    
    # Extract tool calls from response
    if "choices" not in response_data or not response_data["choices"]:
        raise Exception("Invalid response format: no choices")
    
    message = response_data["choices"][0]["message"]
    tool_calls = message.get("tool_calls", [])
    
    if not tool_calls:
        raise Exception("No function calls in response")
    
    # Parse function arguments
    function_call = tool_calls[0]
    if function_call["function"]["name"] != "get_word_information":
        raise Exception(f"Unexpected function called: {function_call['function']['name']}")
    
    # Validate JSON structure
    try:
        definition_data = json.loads(function_call["function"]["arguments"])
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON in function arguments: {e}")
    
    # Validate required fields
    required_fields = ["spanish_meaning", "pinyin", "chinese_meaning"]
    missing_fields = [field for field in required_fields if not definition_data.get(field)]
    
    if missing_fields:
        raise Exception(f"Missing required fields: {missing_fields}")
    
    return definition_data
```

---

## 🎯 Integration with FastTTS Application

### **Word Interaction Workflow** (`main.py:1367`)

The AI system integrates seamlessly with the karaoke word interaction system:

```python
@rt("/define-word", methods=["POST"])
async def define_word(request):
    """AI-powered definition generation endpoint"""
    try:
        data = await request.json()
        word = data.get('word', '').strip()
        word_id = data.get('wordId', '')
        
        if not word:
            return JSONResponse({
                'success': False,
                'error': 'No word provided'
            }, status_code=400)
        
        # Initialize LLM manager
        from llm_manager import LLMManager
        llm_manager = LLMManager()
        
        # Check service availability
        if not llm_manager.is_available():
            return JSONResponse({
                'success': False,
                'error': 'AI definition service unavailable'
            }, status_code=503)
        
        # Generate definition
        definition_data = llm_manager.get_word_definition(word)
        definition_data['word'] = word
        
        # Save to database
        success = insert_vocabulary_word(definition_data)
        
        if success:
            # Get complete vocabulary info for response
            vocab_info = get_vocabulary_info(word)
            
            # Trigger background session updates
            asyncio.create_task(update_all_sessions_with_word(word))
            
            return JSONResponse({
                'success': True,
                'message': 'Word definition generated and saved successfully',
                'word': word,
                'wordId': word_id,
                'vocabularyData': vocab_info
            })
        else:
            return JSONResponse({
                'success': False,
                'error': 'Failed to save definition to database'
            }, status_code=500)
            
    except Exception as e:
        logger.error(f"Error in define_word endpoint: {e}")
        return JSONResponse({
            'success': False,
            'error': 'Internal server error'
        }, status_code=500)
```

### **Frontend Integration** (`static/js/karaoke-interactions.js`)

JavaScript handles AI definition requests and UI updates:

```javascript
// AI definition generation from karaoke interactions
async function generateAIDefinition(wordText, wordId) {
    try {
        // Show loading state
        showLoadingState(wordId);
        
        const response = await fetch('/define-word', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                word: wordText,
                wordId: wordId,
                currentSessionId: getCurrentSession()
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Update word visual status
            markWordAsLearned(wordId, result.vocabularyData);
            
            // Display definition in right sidebar
            showVocabularyInfo(result.vocabularyData, wordId);
            
            // Show success notification
            showNotification(`Definition generated for "${wordText}"`, 'success');
        } else {
            throw new Error(result.error || 'Unknown error');
        }
        
    } catch (error) {
        console.error('AI definition generation failed:', error);
        showNotification(`Failed to generate definition: ${error.message}`, 'error');
    } finally {
        hideLoadingState(wordId);
    }
}
```

---

## 📊 Performance and Rate Limiting

### **Request Optimization**
```python
class LLMRequestOptimizer:
    def __init__(self):
        self.request_cache = {}
        self.cache_ttl = 3600  # 1 hour cache
        self.rate_limiter = RateLimiter()
    
    async def get_cached_definition(self, word: str) -> Optional[dict]:
        """Check cache before making API request"""
        cache_key = f"definition_{word}"
        cached_result = self.request_cache.get(cache_key)
        
        if cached_result and time.time() - cached_result['timestamp'] < self.cache_ttl:
            logger.info(f"Cache hit for word: {word}")
            return cached_result['data']
        
        return None
    
    async def cache_definition(self, word: str, definition: dict):
        """Cache successful definition for future requests"""
        cache_key = f"definition_{word}"
        self.request_cache[cache_key] = {
            'data': definition,
            'timestamp': time.time()
        }
```

### **Rate Limiting Strategy**
```python
class RateLimiter:
    def __init__(self, max_requests_per_minute=20):
        self.max_requests = max_requests_per_minute
        self.request_times = []
    
    async def check_rate_limit(self):
        """Enforce rate limiting for AI API calls"""
        current_time = time.time()
        
        # Remove requests older than 1 minute
        self.request_times = [
            req_time for req_time in self.request_times 
            if current_time - req_time < 60
        ]
        
        # Check if at rate limit
        if len(self.request_times) >= self.max_requests:
            wait_time = 60 - (current_time - self.request_times[0])
            logger.info(f"Rate limit reached, waiting {wait_time:.1f} seconds")
            await asyncio.sleep(wait_time)
        
        # Record this request
        self.request_times.append(current_time)
```

---

## 🔧 Configuration and Environment Setup

### **Environment Variables**
```bash
# Primary AI service (OpenRouter)
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Fallback AI service (OpenAI) 
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Rate limiting configuration
AI_REQUEST_RATE_LIMIT=20  # requests per minute
AI_CACHE_TTL=3600        # cache time-to-live in seconds
```

### **Service Configuration Validation**
```python
def validate_ai_configuration() -> Dict[str, Any]:
    """Validate AI service configuration at startup"""
    config_status = {
        'openrouter': {
            'configured': bool(os.getenv('OPENROUTER_API_KEY')),
            'available': False,
            'error': None
        },
        'openai': {
            'configured': bool(os.getenv('OPENAI_API_KEY')),
            'available': False,  
            'error': None
        }
    }
    
    # Test OpenRouter
    if config_status['openrouter']['configured']:
        try:
            service = OpenRouterService(os.getenv('OPENROUTER_API_KEY'))
            config_status['openrouter']['available'] = service.is_available
        except Exception as e:
            config_status['openrouter']['error'] = str(e)
    
    # Test OpenAI
    if config_status['openai']['configured']:
        try:
            service = OpenAIService(os.getenv('OPENAI_API_KEY'))
            config_status['openai']['available'] = service.is_available
        except Exception as e:
            config_status['openai']['error'] = str(e)
    
    return config_status
```

---

## 📈 Monitoring and Analytics

### **AI Performance Metrics**
```python
class AIMetrics:
    def __init__(self):
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'provider_usage': {
                'openrouter': 0,
                'openai': 0
            },
            'error_types': defaultdict(int)
        }
    
    def record_request(self, provider: str, success: bool, 
                      response_time: float, error_type: str = None):
        """Record AI request metrics"""
        self.metrics['total_requests'] += 1
        self.metrics['provider_usage'][provider] += 1
        
        if success:
            self.metrics['successful_requests'] += 1
        else:
            self.metrics['failed_requests'] += 1
            if error_type:
                self.metrics['error_types'][error_type] += 1
        
        # Update average response time
        total_time = (self.metrics['average_response_time'] * 
                     (self.metrics['total_requests'] - 1) + response_time)
        self.metrics['average_response_time'] = total_time / self.metrics['total_requests']
```

### **Error Tracking and Recovery**
```python
class AIErrorTracker:
    def __init__(self):
        self.error_patterns = {
            'rate_limit': ['rate limit', 'too many requests'],
            'auth_error': ['unauthorized', 'invalid api key', 'authentication'],
            'service_unavailable': ['service unavailable', 'timeout', 'connection'],
            'invalid_response': ['json', 'parsing', 'format']
        }
    
    def categorize_error(self, error_message: str) -> str:
        """Categorize errors for better handling"""
        error_lower = error_message.lower()
        
        for category, patterns in self.error_patterns.items():
            if any(pattern in error_lower for pattern in patterns):
                return category
        
        return 'unknown'
    
    def should_retry(self, error_category: str, attempt_count: int) -> bool:
        """Determine if request should be retried"""
        retry_policies = {
            'rate_limit': attempt_count < 3,
            'service_unavailable': attempt_count < 2,
            'auth_error': False,  # Don't retry auth errors
            'invalid_response': attempt_count < 2
        }
        
        return retry_policies.get(error_category, False)
```

---

## 🔮 Extension and Customization

### **Adding New LLM Providers**
```python
# Template for new LLM provider
class NewLLMProvider(LLMProvider):
    def __init__(self, api_key: str, config=None):
        self._api_key = api_key
        self._model = "default_model"
        self._available = False
        self._provider_name = "New Provider"
        
        # Initialize and validate
        self._verify_connection()
    
    def get_definition(self, word: str) -> Dict[str, str]:
        """Implement provider-specific definition generation"""
        # 1. Prepare request payload
        # 2. Make API call
        # 3. Process response
        # 4. Return standardized format
        pass
    
    @property
    def is_available(self) -> bool:
        return self._available
    
    @property
    def provider_name(self) -> str:
        return self._provider_name

# Register new provider
def register_new_provider():
    """Register new provider with LLM manager"""
    # Add to LLMManager initialization logic
    pass
```

### **Custom Prompt Engineering**
```python
class PromptManager:
    def __init__(self):
        self.prompts = {
            'chinese_definition': {
                'system': "You are a Chinese language expert specializing in vocabulary education.",
                'user_template': "Analyze the Chinese word '{word}' and provide comprehensive linguistic information including pronunciation, meaning, usage, and related words."
            },
            'specialized_domain': {
                'system': "You are an expert in {domain} terminology in Chinese.",
                'user_template': "Provide domain-specific definition for '{word}' in the context of {domain}."
            }
        }
    
    def get_prompt(self, prompt_type: str, **kwargs) -> Dict[str, str]:
        """Get formatted prompt for specific use case"""
        if prompt_type not in self.prompts:
            raise ValueError(f"Unknown prompt type: {prompt_type}")
        
        prompt = self.prompts[prompt_type]
        return {
            'system': prompt['system'].format(**kwargs),
            'user': prompt['user_template'].format(**kwargs)
        }
```

---

*This comprehensive guide provides complete AI/LLM integration documentation for AI coding assistants working with FastTTS. The dual-provider architecture ensures reliable vocabulary generation while maintaining flexibility for future enhancements.*