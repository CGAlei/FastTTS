// Session management functions
let currentSessionId = null;

// Scroll position preservation for left sidebar
let sidebarScrollPosition = 0;

function storeSidebarScrollPosition() {
    const sidebarContent = document.querySelector('.left-sidebar-content');
    if (sidebarContent) {
        sidebarScrollPosition = sidebarContent.scrollTop;
        // Debug logging to verify scroll position storage
        console.log('Scroll position stored:', sidebarScrollPosition);
    }
}

function restoreSidebarScrollPosition() {
    const sidebarContent = document.querySelector('.left-sidebar-content');
    if (sidebarContent && sidebarScrollPosition > 0) {
        // Use requestAnimationFrame to ensure DOM is ready
        requestAnimationFrame(() => {
            sidebarContent.scrollTop = sidebarScrollPosition;
            // Debug logging to verify scroll restoration
            console.log('Scroll position restored to:', sidebarScrollPosition);
        });
    }
}

function setCurrentSession(sessionId) {
    currentSessionId = sessionId;
    // Store in localStorage for persistence
    if (sessionId) {
        localStorage.setItem('currentSessionId', sessionId);
    } else {
        localStorage.removeItem('currentSessionId');
    }
}

function getCurrentSession() {
    if (!currentSessionId) {
        currentSessionId = localStorage.getItem('currentSessionId');
    }
    return currentSessionId;
}

function createNewSession() {
    if (confirm('Create a new session? This will clear the current text.')) {
        document.getElementById('custom-text').value = '';
        document.getElementById('text-display').textContent = '';
        const audioContainer = document.getElementById('audio-container');
        if (audioContainer) audioContainer.innerHTML = '';
        // Clear current session
        setCurrentSession(null);
    }
}

// Add current session to HTMX requests
document.addEventListener('DOMContentLoaded', function() {
    // Intercept HTMX requests to add current session ID
    document.body.addEventListener('htmx:configRequest', function(evt) {
        const currentSession = getCurrentSession();
        if (currentSession && evt.detail.path.includes('/filter-sessions')) {
            // Add current session to the request
            if (evt.detail.verb === 'POST') {
                if (!evt.detail.parameters) evt.detail.parameters = {};
                evt.detail.parameters.current_session = currentSession;
            } else {
                // Add to URL for GET requests
                const url = new URL(evt.detail.path, window.location.origin);
                url.searchParams.set('current_session', currentSession);
                evt.detail.path = url.pathname + url.search;
            }
        }
        
        // Store scroll position before any request that might update the sessions list
        if (evt.detail.path.includes('/load-session') || 
            evt.detail.path.includes('/filter-sessions') ||
            evt.detail.path.includes('/toggle-favorite')) {
            storeSidebarScrollPosition();
        }
    });
    
    // Restore scroll position after HTMX swaps that affect the sessions list
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        if (evt.detail.xhr && evt.detail.xhr.responseURL && 
            (evt.detail.xhr.responseURL.includes('/load-session') || 
             evt.detail.xhr.responseURL.includes('/filter-sessions') ||
             evt.detail.xhr.responseURL.includes('/toggle-favorite'))) {
            restoreSidebarScrollPosition();
        }
    });
});

function saveCurrentSession() {
    const text = document.getElementById('custom-text').value;
    if (!text.trim()) {
        alert('Please enter some text before saving.');
        return;
    }
    
    // Send request to save session
    fetch('/save-session', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            text: text,
            wordData: window.currentWordData || [],
            audioData: window.currentAudioData || null
        })
    }).then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            alert('Session saved successfully!');
            // Refresh session list
            location.reload();
        } else {
            alert(`Failed to save session: ${data.error || 'Unknown error'}`);
        }
    }).catch(error => {
        console.error('Error saving session:', error);
        alert(`Error saving session: ${error.message}`);
    });
}

function loadSession(sessionId, element) {
    // Store current scroll position before loading session
    storeSidebarScrollPosition();
    
    fetch(`/load-session/${sessionId}`)
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            document.getElementById('custom-text').value = data.text;
            document.getElementById('text-display').textContent = data.text;
            
            // Update active session styling
            document.querySelectorAll('.session-item').forEach(item => {
                item.classList.remove('active');
            });
            if (element) {
                element.classList.add('active');
            }
            
            // Store data globally
            window.currentWordData = data.wordData || [];
            window.currentAudioData = data.audioData;
            
            // If audio data exists, load it
            if (data.audioData) {
                const audioContainer = document.getElementById('audio-container');
                audioContainer.innerHTML = `<audio id="audio-player" style="display: none;"><source src="data:audio/mp3;base64,${data.audioData}" type="audio/mpeg"></audio>`;
                
                // Wait for audio element to be ready using next animation frame
                requestAnimationFrame(() => {
                    if (data.wordData && data.wordData.length > 0) {
                        const pinyinData = data.pinyinData || [];
                        prepareWordSeparationWithMergedPunctuation(data.wordData, pinyinData);
                        
                        // Set up audio event listeners for the loaded session
                        const audioElement = document.getElementById('audio-player');
                        if (audioElement) {
                            currentAudio = audioElement;
                            
                            // Show mini audio player
                            showMiniAudioPlayer();
                            
                            // Use centralized function to set up event listeners
                            setupAudioEventListeners(audioElement);
                        }
                    }
                });
            } else {
                // No audio data, but we might still have text to display with word separation
                if (data.wordData && data.wordData.length > 0) {
                    const pinyinData = data.pinyinData || [];
                    prepareWordSeparationWithMergedPunctuation(data.wordData, pinyinData);
                }
            }
        }
    }).catch(error => {
        alert(`Error loading session: ${error.message || 'Network error'}`);
    });
}

// ===========================
// Session Rename Functionality
// ===========================

let currentEditingSession = null;

// Initialize session rename event listeners
document.addEventListener('DOMContentLoaded', function() {
    initializeSessionRenameListeners();
});

function initializeSessionRenameListeners() {
    // Use event delegation for dynamically added session items
    document.addEventListener('click', handleSessionRenameClick);
    document.addEventListener('dblclick', handleSessionRenameDoubleClick);
    document.addEventListener('keydown', handleSessionRenameKeydown);
}

function handleSessionRenameClick(event) {
    // Handle edit button clicks
    if (event.target.classList.contains('edit-btn')) {
        event.stopPropagation(); // Prevent session loading
        const sessionId = event.target.dataset.sessionId;
        startSessionRename(sessionId);
    }
}

function handleSessionRenameDoubleClick(event) {
    // Handle double-click on session title
    if (event.target.classList.contains('session-title')) {
        console.log('Session title double-clicked!', event.target.dataset.sessionId);
        event.stopPropagation(); // Prevent session loading
        const sessionId = event.target.dataset.sessionId;
        if (sessionId) {
            startSessionRename(sessionId);
        }
    }
}

function handleSessionRenameKeydown(event) {
    if (!currentEditingSession) return;
    
    if (event.target.classList.contains('session-rename-input')) {
        if (event.key === 'Enter') {
            event.preventDefault();
            saveSessionRename();
        } else if (event.key === 'Escape') {
            event.preventDefault();
            cancelSessionRename();
        }
    }
}

function startSessionRename(sessionId) {
    
    // Prevent multiple simultaneous edits
    if (currentEditingSession && currentEditingSession !== sessionId) {
        cancelSessionRename();
    }
    
    // Find the session item by traversing up from the edit button
    const editButton = document.querySelector(`[data-session-id="${sessionId}"]`);
    const sessionItem = editButton ? editButton.closest('.session-item') : null;
    
    if (!sessionItem) {
        console.error('Session item not found:', sessionId);
        return;
    }
    
    const titleDiv = sessionItem.querySelector('.session-title');
    if (!titleDiv) {
        console.error('Session title not found');
        return;
    }
    
    const currentName = titleDiv.textContent.trim();
    
    // Create input element
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'session-rename-input';
    input.value = currentName;
    input.dataset.sessionId = sessionId;
    input.dataset.originalName = currentName;
    input.style.cssText = `
        width: 100%;
        padding: 4px 8px;
        border: 2px solid #d97706;
        border-radius: 4px;
        font-size: 14px;
        font-weight: 500;
        background: #fbbf24;
        color: #1a1a1a;
        outline: none;
        box-shadow: 0 0 0 3px rgba(251, 191, 36, 0.3);
        margin: 0;
    `;
    
    // Replace title with input
    titleDiv.style.display = 'none';
    titleDiv.parentElement.insertBefore(input, titleDiv);
    
    // Set edit state
    sessionItem.classList.add('editing');
    currentEditingSession = sessionId;
    
    // Focus and select text
    setTimeout(() => {
        input.focus();
        input.select();
    }, 50);
    
    // Prevent input from losing focus when clicked
    input.addEventListener('click', function(e) {
        e.stopPropagation();
    });
    
    // Handle blur event to save (with delay to allow clicking in input)
    input.addEventListener('blur', function(e) {
        setTimeout(() => {
            if (currentEditingSession === sessionId) {
                saveSessionRename();
            }
        }, 150);
    });
}

function saveSessionRename() {
    if (!currentEditingSession) return;
    
    const editButton = document.querySelector(`[data-session-id="${currentEditingSession}"]`);
    const sessionItem = editButton ? editButton.closest('.session-item') : null;
    if (!sessionItem) return;
    
    const input = sessionItem.querySelector('.session-rename-input');
    if (!input) return;
    
    const newName = input.value.trim();
    const originalName = input.dataset.originalName;
    
    // Validate name
    if (!newName) {
        alert('Session name cannot be empty');
        input.value = originalName;
        input.focus();
        return;
    }
    
    if (newName.length > 100) {
        alert('Session name too long (max 100 characters)');
        input.focus();
        return;
    }
    
    // If name unchanged, just cancel
    if (newName === originalName) {
        cancelSessionRename();
        return;
    }
    
    // Show loading state
    sessionItem.classList.add('renaming');
    input.disabled = true;
    
    // Send rename request
    const formData = new FormData();
    formData.append('new_name', newName);
    formData.append('current_session_id', getCurrentSession() || '');
    
    fetch(`/rename-session/${currentEditingSession}`, {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => Promise.reject(err));
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Update the session title text
            const titleDiv = sessionItem.querySelector('.session-title');
            const input = sessionItem.querySelector('.session-rename-input');
            
            if (titleDiv && input) {
                titleDiv.textContent = newName;
                input.remove();
                titleDiv.style.display = '';
                sessionItem.classList.remove('editing');
            }
            
            // Reset editing state
            currentEditingSession = null;
            
            // Show success feedback
            showRenameSuccess(newName);
        } else {
            throw new Error(data.error || 'Failed to rename session');
        }
    })
    .catch(error => {
        console.error('Error renaming session:', error);
        
        // Remove loading state
        sessionItem.classList.remove('renaming');
        input.disabled = false;
        
        // Show error message
        const errorMsg = error.error || error.message || 'Failed to rename session';
        alert(`Error: ${errorMsg}`);
        
        // Restore original name
        input.value = originalName;
        input.focus();
    });
}

function cancelSessionRename() {
    if (!currentEditingSession) return;
    
    const editButton = document.querySelector(`[data-session-id="${currentEditingSession}"]`);
    const sessionItem = editButton ? editButton.closest('.session-item') : null;
    if (!sessionItem) return;
    
    const input = sessionItem.querySelector('.session-rename-input');
    const titleDiv = sessionItem.querySelector('.session-title');
    
    if (input && titleDiv) {
        // Remove input and show title
        input.remove();
        titleDiv.style.display = '';
        
        // Remove edit state
        sessionItem.classList.remove('editing');
    }
    
    // Reset editing state
    currentEditingSession = null;
}

function showRenameSuccess(newName) {
    // Create temporary success indicator
    const indicator = document.createElement('div');
    indicator.textContent = `✓ Renamed to "${newName}"`;
    indicator.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #10b981;
        color: white;
        padding: 8px 16px;
        border-radius: 6px;
        font-size: 14px;
        z-index: 1000;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(indicator);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        indicator.style.animation = 'fadeOut 0.3s ease-in';
        setTimeout(() => indicator.remove(), 300);
    }, 3000);
}

// Global TTS Progress Notification System
let currentProgressIndicator = null;

function showTTSProgress(message, type = 'progress') {
    // Remove existing progress indicator
    if (currentProgressIndicator && document.body.contains(currentProgressIndicator)) {
        document.body.removeChild(currentProgressIndicator);
    }
    
    // Create new progress indicator
    const indicator = document.createElement('div');
    let bgColor = '#3b82f6'; // Blue for progress
    let icon = '🔵';
    
    if (type === 'success') {
        bgColor = '#10b981'; // Green
        icon = '🟢';
    } else if (type === 'error') {
        bgColor = '#ef4444'; // Red
        icon = '🔴';
    } else if (type === 'warning') {
        bgColor = '#f59e0b'; // Yellow
        icon = '⚠️';
    }
    
    indicator.innerHTML = `${icon} ${message}`;
    indicator.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${bgColor};
        color: white;
        padding: 8px 16px;
        border-radius: 6px;
        font-size: 14px;
        z-index: 1000;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        animation: slideIn 0.3s ease-out;
        max-width: 300px;
        word-wrap: break-word;
    `;
    
    document.body.appendChild(indicator);
    currentProgressIndicator = indicator;
    
    // Auto-remove after delay (longer for progress messages)
    if (type !== 'progress') {
        setTimeout(() => {
            if (document.body.contains(indicator)) {
                indicator.style.opacity = '0';
                setTimeout(() => {
                    if (document.body.contains(indicator)) {
                        document.body.removeChild(indicator);
                    }
                    if (currentProgressIndicator === indicator) {
                        currentProgressIndicator = null;
                    }
                }, 300);
            }
        }, type === 'success' ? 4000 : 6000);
    }
    
    return indicator;
}

function clearTTSProgress() {
    if (currentProgressIndicator && document.body.contains(currentProgressIndicator)) {
        currentProgressIndicator.style.opacity = '0';
        setTimeout(() => {
            if (document.body.contains(currentProgressIndicator)) {
                document.body.removeChild(currentProgressIndicator);
            }
            currentProgressIndicator = null;
        }, 300);
    }
}

// Global functions for TTS progress (accessible from anywhere)
window.showTTSProgress = showTTSProgress;
window.clearTTSProgress = clearTTSProgress;

// TTS Progress Integration with HTMX and SSE
let currentProgressSSE = null;
let progressSessionId = null;

document.addEventListener('DOMContentLoaded', function() {
    // Intercept HTMX requests for TTS generation
    document.body.addEventListener('htmx:configRequest', function(evt) {
        if (evt.detail.path.includes('/generate-custom-tts')) {
            // Get current engine and text
            const currentEngine = window.settingsManager ? window.settingsManager.getCurrentEngine() : 'edge';
            const textInput = document.getElementById('custom-text');
            const textLength = textInput ? textInput.value.length : 0;
            
            // Show progress notification based on engine and text length
            if (currentEngine === 'hailuo' || currentEngine === 'minimax') {
                // MiniMax engine - estimate chunks and show progress
                const chunkSize = 120; // words
                const estimatedWords = Math.ceil(textLength / 1.7); // ~1.7 chars per word
                const estimatedChunks = Math.ceil(estimatedWords / chunkSize);
                
                if (estimatedChunks > 1) {
                    const estimatedTime = estimatedChunks * 2; // 2 seconds per chunk + delays
                    showTTSProgress(`🔄 MiniMax: ${estimatedChunks} chunks, ~${estimatedTime}s (with rate limiting)`, 'progress');
                    
                    // Start checking for progress session after a short delay
                    setTimeout(() => {
                        checkForProgressSession();
                    }, 1000);
                } else {
                    showTTSProgress('🔄 MiniMax: Single chunk, generating audio...', 'progress');
                }
            } else {
                // Edge TTS - simpler progress
                if (textLength > 500) {
                    showTTSProgress('🔄 Edge TTS: Processing long text...', 'progress');
                } else {
                    showTTSProgress('🔄 Edge TTS: Generating audio...', 'progress');
                }
            }
        }
    });
    
    // Handle successful TTS completion
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        if (evt.detail.xhr && evt.detail.xhr.responseURL && evt.detail.xhr.responseURL.includes('/generate-custom-tts')) {
            clearTTSProgress();
            
            // Check if response contains audio (success indicator)
            const audioContainer = document.getElementById('audio-container');
            if (audioContainer && audioContainer.innerHTML.includes('audio-player')) {
                showTTSProgress('TTS generation completed successfully!', 'success');
            } else {
                showTTSProgress('TTS generation completed', 'success');
            }
        }
    });
    
    // Handle TTS errors
    document.body.addEventListener('htmx:responseError', function(evt) {
        if (evt.detail.xhr && evt.detail.xhr.responseURL && evt.detail.xhr.responseURL.includes('/generate-custom-tts')) {
            clearTTSProgress();
            showTTSProgress('TTS generation failed. Please try again.', 'error');
        }
    });
    
    // Handle network errors
    document.body.addEventListener('htmx:sendError', function(evt) {
        if (evt.detail.pathInfo.requestPath.includes('/generate-custom-tts')) {
            clearTTSProgress();
            showTTSProgress('Network error. Please check your connection.', 'error');
        }
    });
    
    // Handle timeout errors
    document.body.addEventListener('htmx:timeout', function(evt) {
        if (evt.detail.pathInfo.requestPath.includes('/generate-custom-tts')) {
            disconnectProgressSSE();
            clearTTSProgress();
            showTTSProgress('Request timed out. Large texts may take longer.', 'warning');
        }
    });
});

// SSE Progress Functions
function checkForProgressSession() {
    // Simple approach: check for active progress sessions periodically
    let checkAttempts = 0;
    const maxAttempts = 20; // Check for 20 seconds
    
    const checkInterval = setInterval(async () => {
        checkAttempts++;
        
        try {
            // Try to find an active progress session by polling recent sessions
            const response = await fetch('/api/progress-sessions');
            if (response.ok) {
                const data = await response.json();
                if (data.active_session) {
                    progressSessionId = data.active_session;
                    connectToProgressSSE(progressSessionId);
                    clearInterval(checkInterval);
                    return;
                }
            }
        } catch (error) {
            console.log('Progress session check failed:', error);
        }
        
        if (checkAttempts >= maxAttempts) {
            clearInterval(checkInterval);
            console.log('No progress session found after 20 seconds');
        }
    }, 1000);
}

function connectToProgressSSE(sessionId) {
    if (currentProgressSSE) {
        currentProgressSSE.close();
    }
    
    console.log('Connecting to progress SSE for session:', sessionId);
    
    currentProgressSSE = new EventSource(`/tts-progress/${sessionId}`);
    
    currentProgressSSE.onopen = function() {
        console.log('SSE connection opened for session:', sessionId);
    };
    
    currentProgressSSE.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            handleProgressUpdate(data);
        } catch (error) {
            console.error('Error parsing SSE message:', error);
        }
    };
    
    currentProgressSSE.onerror = function(error) {
        console.error('SSE connection error:', error);
        disconnectProgressSSE();
    };
}

function handleProgressUpdate(data) {
    switch (data.type) {
        case 'connected':
            console.log('SSE connected to session:', data.session_id);
            break;
            
        case 'progress_update':
            // Update the progress notification with real-time data
            if (data.status === 'processing') {
                const message = `🔄 Processing chunk ${data.current_chunk}/${data.total_chunks}... (${data.percentage}%)`;
                updateTTSProgress(message);
            } else if (data.status === 'combining') {
                updateTTSProgress('🔄 Combining audio chunks...');
            } else if (data.status === 'completed') {
                clearTTSProgress();
                showTTSProgress('TTS generation completed successfully!', 'success');
                disconnectProgressSSE();
            } else if (data.status === 'error') {
                clearTTSProgress();
                showTTSProgress(`TTS generation failed: ${data.error || 'Unknown error'}`, 'error');
                disconnectProgressSSE();
            }
            break;
            
        case 'session_ended':
            console.log('Session ended:', data.session_id);
            disconnectProgressSSE();
            break;
            
        case 'ping':
            // Keep-alive ping, no action needed
            break;
    }
}

function updateTTSProgress(message) {
    // Update existing progress notification instead of creating new one
    if (currentProgressIndicator && document.body.contains(currentProgressIndicator)) {
        currentProgressIndicator.innerHTML = `🔵 ${message}`;
    } else {
        showTTSProgress(message, 'progress');
    }
}

function disconnectProgressSSE() {
    if (currentProgressSSE) {
        currentProgressSSE.close();
        currentProgressSSE = null;
    }
    progressSessionId = null;
}