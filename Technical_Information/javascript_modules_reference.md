# FastTTS JavaScript Modules Reference

## 📋 Frontend Architecture Overview

FastTTS uses a modular JavaScript architecture with 8 specialized ES6+ modules that handle different aspects of the user interface. Each module is designed with clean separation of concerns, proper memory management, and comprehensive error handling.

---

## 🎵 Audio Player Module (`audio-player.js`)

### **Primary Responsibilities**
- Karaoke highlighting with 50ms precision
- Audio playback control and synchronization
- Word-level timing management
- Auto-scroll functionality during playback

### **Core Functions**

#### `startHighlighting()` - `audio-player.js:~120`
- **Purpose**: Initialize real-time karaoke highlighting system
- **Timing**: 50ms interval updates for smooth highlighting
- **Features**: Position-based highlighting, layout stability, auto-scroll integration
- **Performance**: Throttled mouse events, efficient DOM manipulation

#### `highlightCurrentWord(currentTime)` - `audio-player.js:~180`
- **Purpose**: Update highlighting based on audio playback position
- **Parameters**: `currentTime: number` - Current audio playback time in seconds
- **Logic**: Binary search through word timing data for performance
- **Visual**: Golden yellow highlighting with smooth transitions

#### `setupAudioEventListeners(audioElement)` - `audio-player.js:37`
- **Purpose**: Centralized audio event management with proper cleanup
- **Events**: play, pause, ended, seeking, seeked
- **Memory**: Prevents event listener duplication and memory leaks
- **Pattern**: Store references for cleanup, remove legacy handlers

#### `cleanupAudioEventListeners(audioElement)` - `audio-player.js:24`
- **Purpose**: Remove all audio event listeners to prevent memory leaks
- **Called**: When loading new sessions, page unload, error recovery
- **Safety**: Null checks, graceful handling of missing elements

#### `enableAutoScroll()` / `disableAutoScroll()` - `audio-player.js:~300`
- **Purpose**: Intelligent content scrolling during playback
- **Logic**: Scroll to highlighted words, respect manual scrolling
- **UX**: Disable on manual scroll, re-enable after timeout
- **Performance**: RequestAnimationFrame for smooth scrolling

### **State Management**
```javascript
// Global state variables
let currentAudio = null;           // Current audio element
let wordData = [];                 // Word timing information
let isHighlighting = false;        // Highlighting active status
let highlightInterval = null;      // Timing interval reference
let isAutoScrolling = false;       // Auto-scroll state
let audioEventListeners = {};      // Event listener references
```

### **Key Patterns**
- **Event Cleanup**: Systematic removal of event listeners
- **Memory Management**: Clear intervals and timeouts
- **Performance Optimization**: Binary search for word lookup
- **Error Recovery**: Graceful handling of missing audio elements

---

## 🎭 Karaoke Interactions Module (`karaoke-interactions.js`)

### **Primary Responsibilities**
- Word container click and hover event handling
- Google Translate popup management
- Vocabulary lookup integration
- Context-aware interaction responses

### **Core Classes**

#### `KaraokeInteractionManager` - `karaoke-interactions.js:4`
- **Purpose**: Centralized management of word interaction events
- **Pattern**: Class-based architecture with lifecycle management
- **Features**: Event delegation, cleanup system, context menu prevention

#### `TranslationPopupManager` - `karaoke-interactions.js:~200`
- **Purpose**: Google Translate popup display and positioning
- **Features**: Dynamic positioning, click-outside closing, responsive design
- **Integration**: Coordinates with vocabulary system for "Define" button

### **Core Functions**

#### `initializeWordInteractions()` - `karaoke-interactions.js:12`
- **Purpose**: Set up event listeners for all word containers
- **Pattern**: Cleanup existing listeners before adding new ones
- **Scope**: Called after each TTS generation or session load
- **Memory**: Prevents event listener accumulation

#### `handleLeftClick(wordId, wordIndex, wordText, container)` - `karaoke-interactions.js:~80`
- **Purpose**: Process left-click on word containers
- **Logic**: Check vocabulary database → play audio segment OR show vocabulary info
- **Integration**: Calls backend `/word-interaction` endpoint
- **Response**: Updates vocabulary sidebar or triggers audio playback

#### `handleRightClick(wordId, wordIndex, wordText, container)` - `karaoke-interactions.js:~120`
- **Purpose**: Process right-click on word containers
- **Logic**: Check vocabulary database → show Google Translate popup OR vocabulary info
- **Features**: Context menu suppression, popup positioning
- **Fallback**: Google Translate for unknown words

#### `showTranslationPopup(wordText, translation, coordinates, wordId)` - `karaoke-interactions.js:~250`
- **Purpose**: Display Google Translate popup with positioning
- **Features**: Smart positioning (avoid screen edges), responsive sizing
- **Actions**: "Define" button for AI definition generation
- **Cleanup**: Auto-close on outside clicks, escape key

#### `showVocabularyInfo(vocabularyData, wordId)` - `karaoke-interactions.js:~350`
- **Purpose**: Display vocabulary information in right sidebar
- **Integration**: Calls `/vocabulary-display` endpoint for HTML generation
- **Updates**: Right sidebar content with complete vocabulary cards
- **Features**: Out-of-band content replacement, loading states

### **Event Handling Patterns**
```javascript
// Event listener cleanup pattern
addWordEventListeners(container) {
    const leftClickHandler = (event) => {
        event.preventDefault();
        this.handleLeftClick(wordId, wordIndex, wordText, container);
    };
    
    // Store reference for cleanup
    this.eventListeners.set(wordId + '_click', leftClickHandler);
    container.addEventListener('click', leftClickHandler);
}

// Cleanup pattern
cleanup() {
    this.eventListeners.forEach((listener, key) => {
        const [wordId, eventType] = key.split('_');
        const element = document.getElementById(wordId);
        if (element) {
            element.removeEventListener(eventType, listener);
        }
    });
    this.eventListeners.clear();
}
```

---

## 💾 Session Manager Module (`session-manager.js`)

### **Primary Responsibilities**
- Session creation, loading, and deletion
- Session metadata management (favorites, custom names)
- Local storage synchronization
- Sidebar scroll position preservation

### **Core Functions**

#### `setCurrentSession(sessionId)` - `session-manager.js:28`
- **Purpose**: Set active session with localStorage persistence
- **Parameters**: `sessionId: string` - Session identifier or null
- **Storage**: Synchronized with localStorage for page refresh persistence
- **Integration**: Used by session list, loading, and navigation

#### `getCurrentSession()` - `session-manager.js:38`
- **Purpose**: Get current session ID with lazy loading from localStorage
- **Returns**: `string|null` - Active session identifier
- **Fallback**: Loads from localStorage if memory variable is null

#### `createNewSession()` - `session-manager.js:45`
- **Purpose**: Clear current session and prepare for new content
- **Confirmation**: User confirmation dialog before clearing
- **Actions**: Clear text displays, audio container, reset session state
- **UX**: Immediate feedback, focus management

#### `saveCurrentSession()` - `session-manager.js:~80`
- **Purpose**: Persist current session with audio and timing data
- **Data**: Text, word timing, audio base64, metadata
- **Endpoint**: POST `/save-session` with JSON payload
- **Features**: Loading indicators, error handling, success feedback

#### `renameSession(sessionId, currentName)` - `session-manager.js:~150`
- **Purpose**: Interactive session renaming with inline editing
- **UI**: Prompt dialog with current name pre-filled
- **Validation**: Length limits, empty name handling
- **Updates**: Real-time session list updates via HTMX

#### `deleteSessionConfirm(sessionId)` - `session-manager.js:~200`
- **Purpose**: Session deletion with confirmation and cleanup
- **Safety**: Confirmation dialog, irreversible action warning
- **Integration**: Triggers backend DELETE endpoint with auto-selection
- **UX**: Smooth transition to next session

### **Scroll Position Management**

#### `storeSidebarScrollPosition()` - `session-manager.js:7`
- **Purpose**: Preserve sidebar scroll position during updates
- **Timing**: Called before HTMX requests that update session list
- **Storage**: Memory variable for immediate restoration

#### `restoreSidebarScrollPosition()` - `session-manager.js:16`
- **Purpose**: Restore scroll position after sidebar updates
- **Timing**: RequestAnimationFrame for DOM readiness
- **UX**: Maintains user's scroll position during filtering/updates

### **Session Data Structure**
```javascript
// Session save payload
{
    text: "你好世界",
    wordData: [
        {
            word: "你",
            startTime: 0.1,
            endTime: 0.5,
            hasVocabulary: false,
            wordId: "word_0"
        }
    ],
    audioData: "data:audio/mp3;base64,..."
}
```

---

## ⚙️ Settings Manager Module (`settings-manager.js`)

### **Primary Responsibilities**
- TTS settings management (voice, speed, volume, engine)
- Settings modal interface control
- Credential management for TTS engines
- Real-time settings validation and preview

### **Core Functions**

#### `openSettingsPopup()` - `settings-manager.js:~50`
- **Purpose**: Display settings modal with current configuration
- **Loading**: Populate current settings from localStorage and server
- **Tabs**: Voice/Speech settings, Advanced API configuration
- **Features**: Modal overlay, keyboard shortcuts, responsive design

#### `closeSettingsPopup()` - `settings-manager.js:~100`
- **Purpose**: Close settings modal with cleanup
- **Actions**: Save pending changes, clear temporary states
- **Cleanup**: Remove event listeners, reset form states

#### `changeVoice(voiceId)` - `settings-manager.js:~150`
- **Purpose**: Update TTS voice selection with immediate persistence
- **Parameters**: `voiceId: string` - Voice identifier (e.g., "zh-CN-XiaoxiaoNeural")
- **Storage**: localStorage for persistence across sessions
- **Integration**: Updates next TTS generation request

#### `changeSpeed(speedValue)` - `settings-manager.js:~180`
- **Purpose**: Update speech speed with real-time UI feedback
- **Parameters**: `speedValue: number` - Speed multiplier (0.5-2.0)
- **UI**: Slider with formatted display ("1.2× Faster")
- **Validation**: Range constraints, visual feedback

#### `changeTTSEngine(engineName)` - `settings-manager.js:~220`
- **Purpose**: Switch between TTS engines with compatibility checks
- **Parameters**: `engineName: string` - Engine identifier ('edge' or 'hailuo')
- **Logic**: Check configuration status, update voice options
- **UI**: Dynamic voice list updates, status indicators

#### `saveMinimaxCredentials()` - `settings-manager.js:~300`
- **Purpose**: Save and validate MiniMax TTS credentials
- **Data**: API key, group ID, model, chunk size, custom voice ID
- **Validation**: Real-time API testing, error feedback
- **Security**: Masked API key display, secure storage

#### `validateMinimaxCredentials()` - `settings-manager.js:~400`
- **Purpose**: Real-time credential validation with status updates
- **Features**: Debounced validation, loading states, detailed error messages
- **Integration**: Backend `/validate-credentials` endpoint
- **UX**: Immediate feedback, color-coded status indicators

### **Settings State Management**
```javascript
// Settings object structure
const settingsManager = {
    getCurrentVoice: () => localStorage.getItem('selectedVoice') || DEFAULT_VOICE,
    getCurrentSpeed: () => parseFloat(localStorage.getItem('speechSpeed')) || 1.0,
    getCurrentVolume: () => parseFloat(localStorage.getItem('audioVolume')) || 1.0,
    getCurrentEngine: () => localStorage.getItem('ttsEngine') || 'edge'
};
```

---

## 🎨 Theme Manager Module (`theme-manager.js`)

### **Primary Responsibilities**
- Accessibility theme switching (default, dark, high-contrast)
- Font size adjustment for readability
- Theme persistence across sessions
- CSS custom property management

### **Core Functions**

#### `changeColorScheme(scheme)` - `theme-manager.js:~20`
- **Purpose**: Switch between accessibility themes
- **Schemes**: 'default', 'dark-mode', 'high-contrast'
- **Implementation**: CSS class toggling on document body
- **Persistence**: localStorage for cross-session consistency

#### `adjustFontSize(size)` - `theme-manager.js:~60`
- **Purpose**: Dynamic font size adjustment for accessibility
- **Sizes**: 1 (small), 2 (medium), 3 (large), 4 (extra-large)
- **Scope**: Affects main text display area
- **Visual**: Button state updates, immediate text size changes

#### `initializeTheme()` - `theme-manager.js:~100`
- **Purpose**: Load saved theme preferences on page load
- **Timing**: Called on DOMContentLoaded
- **Fallback**: Default theme if no preference stored
- **UI**: Update button states to match current theme

### **Theme CSS Architecture**
```css
/* CSS custom properties for theme switching */
:root {
    --color-text-primary: #1f2937;
    --color-bg-primary: #ffffff;
    --color-accent: #3b82f6;
}

.high-contrast {
    --color-text-primary: #ffffff;
    --color-bg-primary: #000000;
    --color-accent: #ffff00;
}

.dark-mode {
    --color-text-primary: #f3f4f6;
    --color-bg-primary: #1f2937;
    --color-accent: #60a5fa;
}
```

### **Font Size Classes**
```css
.font-size-small { font-size: 14px; }
.font-size-medium { font-size: 16px; }
.font-size-large { font-size: 18px; }
.font-size-xlarge { font-size: 20px; }
```

---

## 🎛️ UI Manager Module (`ui-manager.js`)

### **Primary Responsibilities**
- Sidebar visibility control (left/right panels)
- Auto-hide behavior for input area and controls
- Mobile responsive menu management
- Layout state persistence

### **Core Functions**

#### `toggleLeftSidebar()` - `ui-manager.js:~30`
- **Purpose**: Toggle session management sidebar visibility
- **Animation**: CSS transitions for smooth panel movement
- **Persistence**: Save state to localStorage
- **Responsive**: Different behavior on mobile devices

#### `toggleRightSidebar()` - `ui-manager.js:~60`
- **Purpose**: Toggle vocabulary sidebar visibility
- **Layout**: Adjust main content area to fill available space
- **State**: Independent of left sidebar state
- **Integration**: Coordinate with vocabulary display system

#### `toggleMobileMenu()` - `ui-manager.js:~90`
- **Purpose**: Mobile hamburger menu for session navigation
- **Responsive**: Only active on mobile breakpoints
- **Overlay**: Modal-style overlay for mobile navigation
- **Accessibility**: Focus management, keyboard navigation

#### `initializeAutoHide()` - `ui-manager.js:~150`
- **Purpose**: Set up auto-hide behavior for UI elements
- **Elements**: Input area, accessibility controls, mini audio player
- **Triggers**: Mouse movement, keyboard activity, interaction timeout
- **UX**: Clean reading experience with on-demand controls

#### `setupResizeHandler()` - `ui-manager.js:~200`
- **Purpose**: Handle window resize events for responsive layout
- **Throttling**: 60fps limit for performance
- **Logic**: Adjust sidebar states based on screen size
- **Cleanup**: Proper event listener management

### **Auto-Hide Behavior**
```javascript
// Auto-hide pattern
let hideTimer = null;
const HIDE_DELAY = 3000; // 3 seconds

function startHideTimer() {
    clearTimeout(hideTimer);
    hideTimer = setTimeout(() => {
        hideControls();
    }, HIDE_DELAY);
}

function showControls() {
    clearTimeout(hideTimer);
    // Show UI elements
    startHideTimer();
}
```

---

## 📚 Vocabulary Status Manager Module (`vocab-status-manager.js`)

### **Primary Responsibilities**
- Real-time vocabulary status updates across sessions
- Database synchronization state management
- Word status tracking (known/unknown)
- Visual indicators for vocabulary coverage

### **Core Functions**

#### `updateWordVocabularyStatus(wordId, hasVocabulary)` - `vocab-status-manager.js:~20`
- **Purpose**: Update individual word vocabulary status with visual feedback
- **Parameters**: `wordId: string`, `hasVocabulary: boolean`
- **Visual**: Blue background for known words, default for unknown
- **Performance**: Batch updates for multiple words

#### `refreshAllWordStatuses()` - `vocab-status-manager.js:~50`
- **Purpose**: Sync vocabulary status across all visible words
- **Timing**: Called after session load, vocabulary updates
- **Source**: Backend vocabulary database query
- **UI**: Loading states during refresh, error handling

#### `markWordAsLearned(wordId, vocabularyData)` - `vocab-status-manager.js:~100`
- **Purpose**: Update word status after AI definition generation
- **Integration**: Called after successful `/define-word` responses
- **Updates**: Visual status, internal tracking, session metadata
- **Propagation**: Update all instances across current session

### **Status Tracking Data**
```javascript
// Word status structure
{
    wordId: "word_3",
    wordText: "世界",
    hasVocabulary: true,
    lastUpdated: "2025-06-25T14:30:22Z",
    source: "ai_generated" | "database" | "manual"
}
```

---

## 🔄 Vocabulary Refresh Module (`vocabulary-refresh.js`)

### **Primary Responsibilities**
- Vocabulary database refresh operations
- Progress tracking for refresh processes
- Statistics display and management
- Background refresh coordination

### **Core Functions**

#### `refreshVocabularyState()` - `vocabulary-refresh.js:~20`
- **Purpose**: Trigger complete vocabulary refresh across all sessions
- **Process**: Background processing with progress updates
- **UI**: Progress bar, status messages, completion statistics
- **Integration**: SSE for real-time progress updates

#### `updateVocabularyStats()` - `vocabulary-refresh.js:~80`
- **Purpose**: Update vocabulary statistics in right sidebar
- **Data**: Word count, last modified time, refresh status
- **Source**: Backend `/vocab-stats` endpoint
- **Display**: Compact info capsules with icons

#### `handleRefreshProgress(progressData)` - `vocabulary-refresh.js:~120`
- **Purpose**: Process Server-Sent Events from refresh operation
- **Events**: progress_update, completed, error
- **UI**: Real-time progress bar updates, status messages
- **Completion**: Success/error handling, statistics display

---

## 🎯 Module Integration Patterns

### **HTMX Integration**
```javascript
// HTMX event handling
document.addEventListener('htmx:afterRequest', function(event) {
    // Re-initialize after HTMX updates
    if (window.karaokeInteractionManager) {
        window.karaokeInteractionManager.initializeWordInteractions();
    }
});

// Out-of-band update handling
document.addEventListener('htmx:oobAfterSwap', function(event) {
    // Update affected modules
    restoreSidebarScrollPosition();
    updateVocabularyStats();
});
```

### **Error Handling Pattern**
```javascript
// Consistent error handling
function handleAsyncOperation(operation) {
    try {
        operation();
    } catch (error) {
        console.error(`Operation failed: ${error.message}`);
        // User feedback
        showErrorMessage(error.message);
        // Recovery
        resetToSafeState();
    }
}
```

### **Memory Management Pattern**
```javascript
// Cleanup pattern for all modules
class ModuleManager {
    constructor() {
        this.eventListeners = new Map();
        this.timers = new Set();
    }
    
    cleanup() {
        // Remove event listeners
        this.eventListeners.forEach((listener, element) => {
            element.removeEventListener('event', listener);
        });
        
        // Clear timers
        this.timers.forEach(timer => clearTimeout(timer));
        
        // Reset state
        this.reset();
    }
}
```

### **State Synchronization Pattern**
```javascript
// Cross-module state updates
window.addEventListener('sessionChanged', function(event) {
    const sessionId = event.detail.sessionId;
    
    // Update all affected modules
    sessionManager.setCurrentSession(sessionId);
    vocabStatusManager.refreshAllWordStatuses();
    uiManager.updateActiveSession(sessionId);
});
```

---

## 📊 Performance Characteristics

### **Event Management**
- **Event Delegation**: Efficient handling of dynamic word containers
- **Cleanup Systems**: Prevent memory leaks with systematic listener removal
- **Throttling**: 60fps limits for resize and scroll events
- **Debouncing**: 300ms delays for search and validation inputs

### **DOM Manipulation**
- **Batch Updates**: Group DOM changes for performance
- **RequestAnimationFrame**: Smooth animations and scrolling
- **Minimal Reflows**: Efficient CSS class toggles
- **Virtual State**: Track state in JavaScript, sync to DOM

### **Memory Management**
- **Weak References**: Use Map/Set for automatic garbage collection
- **Cleanup Lifecycle**: Systematic cleanup on navigation
- **State Reset**: Clear temporary data on session changes
- **Timer Management**: Clear all timeouts and intervals

### **Responsive Design**
- **Breakpoint Management**: JavaScript-driven responsive behavior
- **Touch Support**: Mobile-optimized interaction patterns
- **Accessibility**: Full keyboard navigation, screen reader support
- **Progressive Enhancement**: Core functionality without JavaScript

---

## 🔧 Development Guidelines

### **Module Creation Pattern**
```javascript
// Standard module structure
(function() {
    'use strict';
    
    // Private variables
    let moduleState = {};
    const eventListeners = new Map();
    
    // Private functions
    function privateHelper() {
        // Implementation
    }
    
    // Public API
    window.ModuleName = {
        init: function() {
            // Initialization
        },
        
        cleanup: function() {
            // Cleanup
        },
        
        publicMethod: function() {
            // Public functionality
        }
    };
    
    // Auto-initialize on DOM ready
    document.addEventListener('DOMContentLoaded', function() {
        window.ModuleName.init();
    });
})();
```

### **Error Recovery**
- **Graceful Degradation**: Core functionality works without JavaScript
- **Safe Defaults**: Fallback values for all settings
- **Error Boundaries**: Isolate module failures
- **User Feedback**: Clear error messages and recovery options

### **Testing Considerations**
- **Pure Functions**: Separate logic from DOM manipulation
- **State Isolation**: Independent module states
- **Mock Endpoints**: Test without backend dependencies
- **Edge Cases**: Handle missing elements, network failures

---

*This reference provides comprehensive documentation of FastTTS frontend architecture for AI coding assistants. All modules follow consistent patterns for event handling, memory management, and user experience optimization.*