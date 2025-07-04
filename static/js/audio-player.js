let currentAudio = null;
let highlightTimeouts = [];
let wordData = [];
let isHighlighting = false;
let highlightInterval = null;
let miniAudioPlayer = null;

// Performance optimization: Cache DOM elements to avoid repeated querySelectorAll
let cachedWordElements = [];
let cachedCharElements = [];
let lastActiveWordElement = null;
let lastActiveCharElement = null;

// Auto-scroll state management
let isAutoScrolling = false;
let manualScrollTimeout = null;
let autoScrollDisabled = false;
let lastScrollTime = 0;

// Store references to event listeners for cleanup
let audioEventListeners = {
    play: null,
    pause: null,
    ended: null,
    seeking: null,
    seeked: null
};

// Performance optimization: Cache DOM elements for efficient highlighting
function cacheHighlightElements() {
    // Cache word elements
    cachedWordElements = Array.from(document.querySelectorAll('.word-part'));
    
    // Cache character elements  
    cachedCharElements = Array.from(document.querySelectorAll('.char-part'));
    
    console.log(`Cached ${cachedWordElements.length} word elements and ${cachedCharElements.length} char elements`);
}

// Reset all word elements to gray efficiently using cached elements
function resetWordsToGrayOptimized() {
    if (cachedWordElements.length === 0) {
        cacheHighlightElements();
    }
    
    // Reset the previously active element if it exists
    if (lastActiveWordElement) {
        lastActiveWordElement.classList.remove('bg-yellow-400');
        lastActiveWordElement.classList.add('bg-gray-200');
        lastActiveWordElement = null;
    }
    
    // Only reset all if we need to start fresh
    cachedWordElements.forEach(el => {
        el.classList.remove('bg-yellow-400');
        el.classList.add('bg-gray-200');
    });
}

// Reset all character elements to gray efficiently using cached elements
function resetCharsToGrayOptimized() {
    if (cachedCharElements.length === 0) {
        cacheHighlightElements();
    }
    
    // Reset the previously active element if it exists
    if (lastActiveCharElement) {
        lastActiveCharElement.classList.remove('bg-yellow-400');
        lastActiveCharElement.classList.add('bg-gray-200');
        lastActiveCharElement = null;
    }
    
    // Only reset all if we need to start fresh
    cachedCharElements.forEach(el => {
        el.classList.remove('bg-yellow-400');
        el.classList.add('bg-gray-200');
    });
}

// Centralized function to clean up audio event listeners
function cleanupAudioEventListeners(audioElement) {
    if (!audioElement || !audioEventListeners) return;
    
    // Remove all stored event listeners
    Object.keys(audioEventListeners).forEach(eventType => {
        if (audioEventListeners[eventType]) {
            audioElement.removeEventListener(eventType, audioEventListeners[eventType]);
            audioEventListeners[eventType] = null;
        }
    });
}

// Centralized function to set up audio event listeners (prevents duplication)
function setupAudioEventListeners(audioElement) {
    if (!audioElement) return;
    
    // Clean up any existing listeners first
    cleanupAudioEventListeners(audioElement);
    
    // Clear legacy event handlers
    audioElement.onplay = null;
    audioElement.onpause = null;
    audioElement.onended = null;
    
    // Create and store event listeners for proper cleanup
    audioEventListeners.play = function() {
        startHighlighting();
    };
    
    audioEventListeners.pause = function() {
        stopHighlighting();
    };
    
    audioEventListeners.ended = function() {
        stopHighlighting();
    };
    
    audioEventListeners.seeking = function() {
        stopHighlighting();
    };
    
    audioEventListeners.seeked = function() {
        if (!audioElement.paused) {
            startHighlighting();
        }
    };
    
    // Add all event listeners
    audioElement.addEventListener('play', audioEventListeners.play);
    audioElement.addEventListener('pause', audioEventListeners.pause);
    audioElement.addEventListener('ended', audioEventListeners.ended);
    audioElement.addEventListener('seeking', audioEventListeners.seeking);
    audioElement.addEventListener('seeked', audioEventListeners.seeked);
    
}

// Mini Audio Player Functions
let miniAudioUpdateInterval = null;

function toggleMiniAudio() {
    if (!currentAudio) return;
    
    if (currentAudio.paused) {
        currentAudio.play();
    } else {
        currentAudio.pause();
    }
}

function updateMiniAudioDisplay() {
    if (!currentAudio) return;
    
    const playBtn = document.getElementById('mini-play-btn');
    const timeDisplay = document.getElementById('mini-time-display');
    const progressBar = document.getElementById('mini-progress-bar');
    
    // Error handling for missing DOM elements
    if (!playBtn || !timeDisplay || !progressBar) {
        return;
    }
    
    // Update play/pause button
    playBtn.textContent = currentAudio.paused ? '▶' : '⏸';
    
    // Update time display
    const currentMinutes = Math.floor(currentAudio.currentTime / 60);
    const currentSeconds = Math.floor(currentAudio.currentTime % 60);
    timeDisplay.textContent = `${currentMinutes}:${currentSeconds.toString().padStart(2, '0')}`;
    
    // Update progress bar
    if (currentAudio.duration) {
        const progress = (currentAudio.currentTime / currentAudio.duration) * 100;
        progressBar.style.width = progress + '%';
    }
}

function seekMiniAudio(event) {
    if (!currentAudio || !currentAudio.duration) return;
    
    const container = event.currentTarget;
    const rect = container.getBoundingClientRect();
    const clickX = event.clientX - rect.left;
    const percentage = clickX / rect.width;
    const newTime = percentage * currentAudio.duration;
    
    currentAudio.currentTime = newTime;
}


function showMiniAudioPlayer() {
    const miniPlayer = document.getElementById('mini-audio-player');
    if (miniPlayer) {
        miniPlayer.classList.add('visible');
        
        // Start updating display
        if (miniAudioUpdateInterval) {
            clearInterval(miniAudioUpdateInterval);
        }
        
        miniAudioUpdateInterval = setInterval(updateMiniAudioDisplay, 100);
    }
}

function hideMiniAudioPlayer() {
    const miniPlayer = document.getElementById('mini-audio-player');
    if (miniPlayer) {
        miniPlayer.classList.remove('visible');
        
        // Improved memory management: stop updating display and cleanup
        if (miniAudioUpdateInterval) {
            clearInterval(miniAudioUpdateInterval);
            miniAudioUpdateInterval = null;
        }
        
        // Clear any remaining highlighting when hiding player
        stopHighlighting();
    }
}

function resetWordsToGray() {
    resetWordsToGrayOptimized();
}

function resetAudio() {
    try {
        if (currentAudio) {
            currentAudio.pause();
            currentAudio.currentTime = 0;
        }
        stopHighlighting();
        const textEl = document.getElementById('text-display');
        if (textEl) {
            // Reset to original text content
            const originalText = textEl.getAttribute('data-original-text') || textEl.textContent;
            textEl.innerHTML = '';
            textEl.textContent = originalText;
        }
        
        // Clear cached elements to force refresh on next load
        cachedWordElements = [];
        cachedCharElements = [];
        lastActiveWordElement = null;
        lastActiveCharElement = null;
    } catch (error) {
        console.error('Error resetting audio:', error);
    }
}

function stopHighlighting() {
    isHighlighting = false;
    if (highlightInterval) {
        clearInterval(highlightInterval);
        highlightInterval = null;
    }
    // Improved memory management: clear all timeouts and reset array
    highlightTimeouts.forEach(timeout => {
        if (timeout) clearTimeout(timeout);
    });
    highlightTimeouts.length = 0; // More efficient than [] assignment
}

function prepareWordSeparationWithMergedPunctuation(wordData, pinyinData = []) {
    
    const textEl = document.getElementById('text-display');
    if (!textEl) {
        return;
    }
    
    if (!wordData || !wordData.length) {
        return;
    }
    
    const originalText = textEl.textContent;
    
    // Filter out asterisk entries and garbled characters
    const validWords = wordData.filter(item => {
        if (!item.word || item.word === '*' || item.word.trim() === '') {
            return false;
        }
        const chineseRegex = /[\u4e00-\u9fff]/;
        if (!chineseRegex.test(item.word)) {
            return false;
        }
        return true;
    });
    
    if (validWords.length === 0) {
        setupCharacterHighlighting(originalText, wordData);
        return;
    }
    
    // Enhanced word processing with punctuation merging
    let htmlText = '';
    let textIndex = 0;
    
    // Define punctuation that should be merged with words
    const punctuationToMerge = /[，。、；：！？,.;:!?]/;
    
    validWords.forEach((item, i) => {
        const word = item.word.trim();
        const wordIndex = originalText.indexOf(word, textIndex);
        
        if (wordIndex >= 0) {
            // Handle text before the word (spaces, line breaks, non-mergeable punctuation)
            const beforeText = originalText.slice(textIndex, wordIndex);
            for (let j = 0; j < beforeText.length; j++) {
                const char = beforeText[j];
                if (char === '\n') {
                    htmlText += '<div class="line-break"></div>';
                } else if (char.trim() === '' || char === ' ') {
                    htmlText += char; // Keep spaces as-is
                } else if (!punctuationToMerge.test(char)) {
                    // Only create containers for punctuation that shouldn't be merged
                    htmlText += `<span class="punctuation-part">`;
                    htmlText += `<div class="punctuation-container">`;
                    htmlText += `<div class="punctuation-spacer">&nbsp;</div>`;
                    htmlText += `<div class="punctuation-char">${char}</div>`;
                    htmlText += `</div>`;
                    htmlText += `</span>`;
                }
                // Skip mergeable punctuation - it should have been merged with previous word
            }
            
            // Look ahead for following punctuation to merge
            let wordEndIndex = wordIndex + word.length;
            let followingPunctuation = '';
            
            // Check for punctuation immediately following the word
            while (wordEndIndex < originalText.length && 
                   punctuationToMerge.test(originalText[wordEndIndex])) {
                followingPunctuation += originalText[wordEndIndex];
                wordEndIndex++;
            }
            
            // Add the word with pinyin structure + merged punctuation + enhanced metadata
            const wordId = `word-${i}`;
            const wordStart = item.startTime || 0;
            const wordEnd = item.endTime || 0;
            const isInDB = item.isInDB || false;
            const vocabClass = isInDB ? 'vocab-word' : '';
            htmlText += `<span id="${wordId}" class="word-part ${vocabClass}" 
                         data-word-index="${i}" 
                         data-word-text="${word}" 
                         data-start-time="${wordStart}" 
                         data-end-time="${wordEnd}"
                         data-is-in-db="${isInDB}">`;
            
            // Process each character in the word
            let wordPinyin = '';
            let wordChars = '';
            
            // Add the main word characters with pinyin
            for (let j = 0; j < word.length; j++) {
                const char = word[j];
                // Find pinyin for this character
                const charPosition = wordIndex + j;
                const pinyin = (pinyinData[charPosition] && pinyinData[charPosition].pinyin) || '';
                
                if (j > 0 && pinyin) {
                    wordPinyin += ' ';
                }
                wordPinyin += pinyin;
                wordChars += char;
            }
            
            // Add merged punctuation to the word (no pinyin for punctuation)
            if (followingPunctuation) {
                wordChars += followingPunctuation;
            }
            
            // Create a single container for the entire word + punctuation
            htmlText += `<div class="char-container">`;
            htmlText += `<div class="pinyin-text">${wordPinyin}</div>`;
            htmlText += `<div class="chinese-char">${wordChars}</div>`;
            htmlText += `</div>`;
            
            htmlText += `</span>`;
            
            // Update text index to skip the merged punctuation
            textIndex = wordEndIndex;
        }
    });
    
    // Handle any remaining text at the end
    const remainingText = originalText.slice(textIndex);
    for (let j = 0; j < remainingText.length; j++) {
        const char = remainingText[j];
        if (char === '\n') {
            htmlText += '<div class="line-break"></div>';
        } else if (char.trim() === '' || char === ' ') {
            htmlText += char; // Keep spaces as-is
        } else if (!punctuationToMerge.test(char)) {
            // Only create containers for non-mergeable punctuation
            htmlText += `<span class="punctuation-part">`;
            htmlText += `<div class="punctuation-container">`;
            htmlText += `<div class="punctuation-spacer">&nbsp;</div>`;
            htmlText += `<div class="punctuation-char">${char}</div>`;
            htmlText += `</div>`;
            htmlText += `</span>`;
        }
        // Skip mergeable punctuation if it somehow wasn't caught above
    }
    
    textEl.innerHTML = htmlText;
    
    // Store valid words globally for later highlighting
    window.currentValidWords = validWords;
    
    
    // Initialize karaoke interactions for the new word containers
    if (window.karaokeInteractionManager) {
        // Use requestAnimationFrame for next rendering cycle
        requestAnimationFrame(() => {
            window.karaokeInteractionManager.initializeWordInteractions();
        });
    }
}

function startHighlighting() {
    
    if (!window.currentValidWords) {
        return;
    }
    
    const validWords = window.currentValidWords;
    
    // Start position-based highlighting
    isHighlighting = true;
    highlightInterval = setInterval(() => {
        if (!currentAudio || currentAudio.paused || !isHighlighting) {
            return;
        }
        
        const currentTime = currentAudio.currentTime * 1000; // Convert to milliseconds
        updateHighlightingAtPosition(currentTime, validWords);
    }, 50); // Update every 50ms for smooth highlighting
    
}

function updateHighlightingAtPosition(currentTimeMs, validWords) {
    // Find the current word based on audio position
    let currentWordIndex = -1;
    for (let i = 0; i < validWords.length; i++) {
        if (currentTimeMs >= validWords[i].timestamp) {
            currentWordIndex = i;
        } else {
            break;
        }
    }
    
    // Efficiently reset previous highlighting
    if (lastActiveWordElement) {
        lastActiveWordElement.classList.remove('bg-yellow-400');
        lastActiveWordElement.classList.add('bg-gray-200');
        lastActiveWordElement = null;
    }
    
    // Highlight current word if found
    if (currentWordIndex >= 0) {
        const wordEl = document.getElementById('word-' + currentWordIndex);
        if (wordEl) {
            wordEl.classList.remove('bg-gray-200');
            // Apply default yellow highlighting
            wordEl.classList.add('bg-yellow-400');
            
            // Track the active element for efficient cleanup
            lastActiveWordElement = wordEl;
            
            // Auto-scroll to keep highlighted word visible
            autoScrollToWord(wordEl);
        }
    }
}

// Auto-scroll functions for karaoke highlighting
function isWordInViewport(wordElement) {
    if (!wordElement) return true;
    
    const mainContent = document.querySelector('.main-content');
    if (!mainContent) return true;
    
    const wordRect = wordElement.getBoundingClientRect();
    const containerRect = mainContent.getBoundingClientRect();
    
    // Account for accessibility controls height (when visible)
    const controls = document.querySelector('.accessibility-controls');
    const controlsHeight = controls && !controls.classList.contains('auto-hide') 
        ? controls.offsetHeight : 0;
    
    // Account for input panel height (when visible)
    const inputArea = document.querySelector('.input-area');
    const inputHeight = inputArea && !inputArea.classList.contains('auto-hide') 
        ? inputArea.offsetHeight : 0;
    
    // Calculate effective viewing area
    const viewportTop = containerRect.top + controlsHeight;
    const viewportBottom = containerRect.bottom - inputHeight;
    const viewportHeight = viewportBottom - viewportTop;
    
    // Check if word is in the middle 60% of the effective viewport
    const bufferZone = viewportHeight * 0.2; // 20% buffer on top and bottom
    const wordCenter = wordRect.top + (wordRect.height / 2);
    
    return wordCenter >= (viewportTop + bufferZone) && 
           wordCenter <= (viewportBottom - bufferZone);
}

function autoScrollToWord(wordElement) {
    // Skip if auto-scroll is disabled due to manual scrolling
    if (autoScrollDisabled || isAutoScrolling) return;
    
    // Skip if word is already in comfortable viewing area
    if (isWordInViewport(wordElement)) return;
    
    const mainContent = document.querySelector('.main-content');
    if (!mainContent) return;
    
    // Set auto-scrolling flag to prevent conflicts
    isAutoScrolling = true;
    
    // Calculate target scroll position to center the word
    const wordRect = wordElement.getBoundingClientRect();
    const containerRect = mainContent.getBoundingClientRect();
    
    // Account for UI elements
    const controls = document.querySelector('.accessibility-controls');
    const controlsHeight = controls && !controls.classList.contains('auto-hide') 
        ? controls.offsetHeight : 0;
    
    const inputArea = document.querySelector('.input-area');
    const inputHeight = inputArea && !inputArea.classList.contains('auto-hide') 
        ? inputArea.offsetHeight : 0;
    
    // Calculate effective viewport center
    const effectiveViewportHeight = containerRect.height - controlsHeight - inputHeight;
    const targetCenter = controlsHeight + (effectiveViewportHeight / 2);
    
    // Calculate scroll offset needed
    const wordCenter = wordRect.top + (wordRect.height / 2);
    const scrollOffset = wordCenter - containerRect.top - targetCenter;
    const targetScrollTop = mainContent.scrollTop + scrollOffset;
    
    // Smooth scroll to target position
    mainContent.scrollTo({
        top: Math.max(0, targetScrollTop),
        behavior: 'smooth'
    });
    
    // Reset auto-scrolling flag after animation completes
    setTimeout(() => {
        isAutoScrolling = false;
    }, 500); // Account for smooth scroll animation time
}


function setupManualScrollDetection() {
    const mainContent = document.querySelector('.main-content');
    if (!mainContent) return;
    
    // Detect manual scrolling during karaoke
    mainContent.addEventListener('scroll', function(event) {
        const currentTime = Date.now();
        
        // If this scroll event is happening during auto-scroll, ignore
        if (isAutoScrolling) return;
        
        // If user manually scrolls during karaoke, disable auto-scroll temporarily
        if (isHighlighting) {
            autoScrollDisabled = true;
            lastScrollTime = currentTime;
            
            // Clear any existing timeout
            if (manualScrollTimeout) {
                clearTimeout(manualScrollTimeout);
            }
            
            // Re-enable auto-scroll after 2 seconds of no manual scrolling
            manualScrollTimeout = setTimeout(() => {
                autoScrollDisabled = false;
            }, 2000);
        }
    }, { passive: true });
}

function setupCharacterHighlighting(text, wordData) {
    const textEl = document.getElementById('text-display');
    let htmlText = '';
    
    // Create array of Chinese characters only
    const chineseChars = [];
    let charSpanIndex = 0;
    
    // Split text into characters and wrap Chinese characters in spans
    for (let i = 0; i < text.length; i++) {
        const char = text[i];
        const isChineseChar = /[\u4e00-\u9fff]/.test(char);
        
        if (isChineseChar) {
            htmlText += `<span id="char-${charSpanIndex}" class="char-part bg-gray-200 rounded px-1 mx-1">${char}</span>`;
            chineseChars.push({char: char, index: charSpanIndex});
            charSpanIndex++;
        } else {
            htmlText += char; // Keep punctuation and spaces as-is
        }
    }
    
    textEl.innerHTML = htmlText;
    
    // Use timestamps to highlight characters progressively
    const validTimestamps = wordData.filter(item => item.timestamp && item.timestamp > 0);
    
    validTimestamps.forEach((item, i) => {
        const timeout = setTimeout(() => {
            // Efficiently remove previous highlighting
            if (lastActiveCharElement) {
                lastActiveCharElement.classList.remove('bg-yellow-400');
                lastActiveCharElement.classList.add('bg-gray-200');
                lastActiveCharElement = null;
            }
            
            // Calculate which character to highlight based on progression
            const charIndex = Math.floor((i / validTimestamps.length) * chineseChars.length);
            const actualCharIndex = Math.min(charIndex, chineseChars.length - 1);
            
            const charEl = document.getElementById('char-' + actualCharIndex);
            if (charEl) {
                charEl.classList.remove('bg-gray-200');
                charEl.classList.add('bg-yellow-400');
                
                // Track the active element for efficient cleanup
                lastActiveCharElement = charEl;
            }
        }, item.timestamp);
        highlightTimeouts.push(timeout);
    });
    
}

// HTMX event listener for TTS generation
document.addEventListener('htmx:afterRequest', function(evt) {
    
    if ((evt.detail.xhr.responseURL.includes('/generate-') && evt.detail.xhr.responseURL.includes('tts')) || 
        evt.detail.xhr.responseURL.includes('/load-session/')) {
        
        // Wait for DOM updates using requestAnimationFrame
        requestAnimationFrame(() => {
            const audioElement = document.querySelector('#audio-player');
            const dataElement = document.querySelector('#word-data');
            const textElement = document.getElementById('text-display');
            
            
            if (audioElement && dataElement && textElement) {
                currentAudio = audioElement;
                
                // Show mini audio player
                showMiniAudioPlayer();
                
                try {
                    const rawData = dataElement.getAttribute('data-words');
                    
                    const wordData = JSON.parse(rawData);
                    
                    // Store word data globally and audio reference
                    window.currentWordData = wordData;
                    currentAudio = audioElement;
                    
                    // Cache DOM elements for efficient highlighting performance
                    cacheHighlightElements();
                    
                    // Store audio data for session saving
                    const audioSrc = audioElement.querySelector('source').src;
                    if (audioSrc.startsWith('data:audio/mp3;base64,')) {
                        window.currentAudioData = audioSrc.split(',')[1];
                    }
                    
                    // Get pinyin data
                    const pinyinElement = document.querySelector('#pinyin-data');
                    let pinyinData = [];
                    if (pinyinElement) {
                        try {
                            const rawPinyinData = pinyinElement.getAttribute('data-pinyin');
                            pinyinData = JSON.parse(rawPinyinData);
                        } catch (e) {
                            // Silently handle pinyin parse errors
                        }
                    }
                    
                    // IMMEDIATELY prepare word separation with pinyin after TTS generation
                    prepareWordSeparationWithMergedPunctuation(wordData, pinyinData);
                    
                    // Set up audio event listeners
                    setupAudioEventListeners(audioElement);
                    
                    // Initialize manual scroll detection for auto-scroll functionality
                    setupManualScrollDetection();
                    
                } catch (e) {
                    // Silently handle JSON parse errors
                }
            }
        });
    }
});