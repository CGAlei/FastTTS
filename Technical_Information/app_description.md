# FastTTS - AI-Enhanced Chinese Language Learning System

## 📋 Application Overview

**FastTTS** is a production-ready, AI-enhanced Chinese language learning application that combines advanced text-to-speech technology with intelligent vocabulary expansion and real-time karaoke-style synchronization. The system provides an immersive learning experience through synchronized audio-visual feedback, precise word timing, and adaptive vocabulary acquisition.

## 🎯 Primary Purpose

FastTTS serves as a comprehensive Chinese language learning platform designed to:

- **Enhance Reading Comprehension**: Visual text display with synchronized audio playback
- **Improve Pronunciation**: High-quality TTS with multiple Chinese voice options
- **Expand Vocabulary**: AI-powered definition generation and intelligent word discovery
- **Track Learning Progress**: Session-based learning with complete persistence and analytics
- **Provide Accessibility**: Multi-theme support with WCAG compliance for diverse learners

## 👥 Target Users

- **Chinese Language Students**: Beginners to advanced learners seeking pronunciation and reading practice
- **Educational Institutions**: Teachers and schools requiring interactive Chinese learning tools
- **Self-Directed Learners**: Individuals studying Chinese independently with adaptive vocabulary expansion
- **Accessibility Users**: Learners requiring high contrast themes and screen reader compatibility
- **Content Creators**: Educators developing Chinese learning materials and curricula

## 🚀 Core Features & Capabilities

### **AI-Enhanced Learning Engine**
- **Dual LLM Integration**: OpenRouter (primary) + OpenAI (fallback) for robust vocabulary expansion
- **Dynamic Definition Generation**: Context-aware Chinese-Spanish translations with usage examples
- **Intelligent Word Discovery**: Real-time vocabulary gap analysis during text processing
- **Adaptive Learning**: System learns from user interactions to improve recommendations

### **Advanced Text-to-Speech System**
- **Multi-Engine Architecture**: Microsoft Edge TTS + MiniMax Hailuo TTS with Montreal Forced Alignment
- **Precision Timing**: 50ms synchronization accuracy with word-level highlighting
- **Voice Customization**: 8+ Chinese neural voices with speed (0.5x-2.0x) and volume controls
- **Smart Text Processing**: Automatic number conversion (180→一百八十) and symbol sanitization

### **Interactive Karaoke Interface**
- **Real-Time Highlighting**: Golden yellow word highlighting synchronized with audio playback
- **Click-to-Define**: Instant vocabulary lookup with Google Translate integration
- **Layout Stability**: Fixed-width containers prevent visual jumps during playback
- **Auto-Scroll**: Intelligent content navigation following audio progression

### **Comprehensive Session Management**
- **Complete Persistence**: Audio files, metadata, timing data, and vocabulary status preservation
- **Custom Naming**: User-defined session titles with inline editing capabilities
- **Favorites System**: Star-based organization with advanced filtering options
- **Search & Filter**: Real-time text matching across session content and metadata
- **URL State Management**: Persistent filter states for bookmarking and sharing

### **Professional Accessibility Features**
- **Three Theme Modes**: Default, dark mode, and high contrast for visual accessibility
- **WCAG Compliance**: Full keyboard navigation and screen reader compatibility
- **Responsive Design**: Mobile-first architecture with touch-friendly interactions
- **Auto-Hide Controls**: Context-aware UI elements that appear when needed

## 💻 Technology Stack

### **Backend Framework**
- **Primary Language**: Python 3.10+ (production environment)
- **Web Framework**: FastHTML (modern Python web framework with HTMX integration)
- **Async Support**: Native asyncio for concurrent TTS processing and API calls
- **Database**: SQLite with 1534+ vocabulary entries and session metadata persistence

### **Frontend Architecture**
- **JavaScript**: Modular ES6+ architecture with 8 specialized component files
- **Styling**: Custom modular CSS with Tailwind-inspired utility patterns
- **Interactivity**: HTMX for seamless server-client communication without full page reloads
- **Themes**: CSS custom properties system for accessible theme switching

### **External Integrations**
- **TTS Engines**: Microsoft Edge TTS (native timing) + MiniMax Hailuo TTS (custom voices)
- **Forced Alignment**: Montreal Forced Alignment (MFA) 3.2.3 for millisecond-precise timing
- **AI Services**: OpenRouter API (primary) + OpenAI GPT-4o-mini (fallback)
- **Translation**: Google Translate API integration for instant word lookup

### **Development Environments**

#### **Standard Environment (requirements.txt)**
```txt
python-fasthtml>=0.6.9    # Web framework
edge-tts>=6.1.9          # Microsoft TTS engine
pypinyin>=0.50.0         # Chinese phonetic notation
requests>=2.28.0         # HTTP client library
python-dotenv>=1.0.0     # Environment variable management
jieba>=0.42.1            # Chinese word segmentation
openai>=1.0.0            # AI service integration
```

#### **MFA-Enhanced Environment (environment.yml)**
```yaml
name: fasttts-mfa
dependencies:
  - python=3.10
  - montreal-forced-aligner=3.2.3  # Precision audio alignment
  - kaldi                          # Speech recognition toolkit
  - openfst                        # Finite state transducer library
  - ffmpeg                         # Audio processing
  - sox                           # Sound processing
  - pip dependencies...           # All standard requirements
```

## 🏗️ System Architecture

### **Modular Component Design**
- **Separation of Concerns**: Distinct modules for TTS, AI, database, and UI operations
- **Plugin Architecture**: Extensible TTS engine system supporting multiple providers
- **Service Layer**: Clean abstraction between frontend interactions and backend processing
- **Factory Pattern**: Dynamic TTS engine selection based on availability and user preferences

### **Data Flow Architecture**
1. **Text Input** → Text processing and number conversion
2. **TTS Generation** → Multi-engine audio synthesis with timing data
3. **Karaoke Display** → Synchronized highlighting with 50ms precision
4. **Vocabulary Interaction** → AI-powered definition generation and database updates
5. **Session Persistence** → Complete state preservation with metadata management

### **Performance Characteristics**
- **Application Size**: 439-line core application (60% reduction from original 1000+ lines)
- **Frontend Code**: ~3000 lines across 8 specialized JavaScript modules
- **Database Performance**: <100ms vocabulary lookups, 585KB SQLite database
- **TTS Generation**: <2s for Edge TTS, 2-5s for MiniMax with MFA processing
- **Memory Efficiency**: Constant memory footprint regardless of session count

## 🎨 User Interface Design

### **Three-Panel Layout System**
- **Left Sidebar (300px)**: Session management, filtering, and navigation controls
- **Center Panel (dynamic)**: Primary content area with karaoke interface and input controls
- **Right Sidebar (300px)**: Vocabulary display, definitions, and learning aids
- **Responsive Adaptation**: Panels collapse and reorganize for mobile/tablet viewing

### **Visual Design Principles**
- **Material Design Influence**: Clean cards, subtle shadows, and consistent spacing
- **Golden Ratio Timing**: 1.618s transition animations for natural feel
- **Color Psychology**: Blue for vocabulary, yellow for highlighting, consistent accent colors
- **Typography Scale**: Carefully crafted hierarchy from 12px to 18px for optimal readability

## 🔧 Configuration Management

### **Environment Variables**
```bash
OPENROUTER_API_KEY        # Primary AI service authentication
OPENAI_API_KEY           # Fallback AI service authentication
MINIMAX_API_KEY          # Custom TTS voice access
MINIMAX_GROUP_ID         # MiniMax service organization identifier
FASTTTS_LOG_LEVEL        # Logging verbosity control
MINIMAX_CHUNK_SIZE       # Text chunking for large content processing
```

### **Runtime Configuration**
- **Logging System**: Multi-handler logging with file rotation and error isolation
- **Session Storage**: File-based persistence with JSON metadata and binary audio
- **Cache Strategy**: LocalStorage for user preferences, server-side session caching
- **Error Handling**: Graceful degradation with fallback mechanisms at every level

## 🎯 Key Architectural Decisions

### **FastHTML Over Traditional Frameworks**
- **Server-Side Rendering**: Reduced JavaScript complexity and improved SEO
- **HTMX Integration**: Modern interactivity without SPA complexity
- **Python Ecosystem**: Leverages extensive ML/AI libraries for intelligent features

### **Multi-Engine TTS Architecture**
- **Edge TTS**: Fast, reliable timing with native word boundaries
- **MiniMax**: Custom voices with professional quality audio
- **MFA Integration**: Millisecond-precise alignment for optimal learning experience

### **Modular Frontend Design**
- **Component Separation**: Each JavaScript file handles specific UI responsibilities
- **Memory Management**: Proper cleanup and garbage collection patterns
- **Progressive Enhancement**: Core functionality works without JavaScript

### **Database Strategy**
- **SQLite Choice**: Zero-configuration, embedded database perfect for desktop deployment
- **Vocabulary Schema**: Optimized for fast lookup with minimal storage overhead
- **Session Management**: File-based approach enabling easy backup and synchronization

## 📊 Success Metrics

### **Technical Performance**
- **Load Time**: <2 seconds initial application load
- **Interaction Responsiveness**: <100ms UI response time
- **TTS Quality**: Professional-grade audio synthesis with multiple voice options
- **Timing Accuracy**: 50ms precision for educational effectiveness

### **Educational Effectiveness**
- **Vocabulary Retention**: AI-powered spaced repetition and context-aware definitions
- **Engagement Metrics**: Session duration, vocabulary interaction rates, return usage
- **Accessibility Compliance**: WCAG 2.1 AA standard compliance for inclusive learning
- **Cross-Platform Support**: Consistent experience across desktop, tablet, and mobile devices

## 🔮 Future Extensibility

### **Planned Enhancements**
- **Multi-Language Support**: Framework ready for additional languages beyond Chinese
- **Cloud Synchronization**: Session and vocabulary sync across devices
- **Advanced Analytics**: Learning progress tracking and personalized recommendations
- **Collaborative Features**: Shared sessions and community vocabulary contributions

### **Integration Opportunities**
- **LMS Integration**: Canvas, Moodle, and other educational platform compatibility
- **Mobile Applications**: Native iOS/Android apps sharing the same backend
- **API Ecosystem**: RESTful API for third-party educational tool integration
- **Offline Mode**: Local TTS and cached vocabulary for internet-independent learning

---

*This document serves as the primary technical introduction for AI coding assistants working with the FastTTS codebase. It provides comprehensive context for understanding system architecture, making development decisions, and maintaining code quality standards.*