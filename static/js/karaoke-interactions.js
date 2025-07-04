// Karaoke Word Container Interaction Manager
// Handles left-click, right-click, and hover events for word containers

class KaraokeInteractionManager {
    constructor() {
        this.eventListeners = new Map();
        this.isInitialized = false;
        this.preventContextMenu = true;
    }

    // Initialize event listeners for all word containers
    initializeWordInteractions() {
        if (this.isInitialized) {
            this.cleanup();
        }

        const wordContainers = document.querySelectorAll('.word-part');

        wordContainers.forEach((container, index) => {
            this.addWordEventListeners(container);
        });

        this.isInitialized = true;
    }

    // Add event listeners to a specific word container
    addWordEventListeners(container) {
        if (!container || !container.id) {
            return;
        }

        const wordId = container.id;
        const wordIndex = container.dataset.wordIndex;
        const wordText = container.dataset.wordText;

        // Left click handler
        const leftClickHandler = (event) => {
            event.preventDefault();
            this.handleLeftClick(wordId, wordIndex, wordText, container);
        };

        // Right click handler
        const rightClickHandler = (event) => {
            event.preventDefault();
            if (this.preventContextMenu) {
                event.stopPropagation();
            }
            this.handleRightClick(wordId, wordIndex, wordText, container);
        };

        // Mouse enter handler
        const mouseEnterHandler = (event) => {
            this.handleMouseEnter(wordId, wordIndex, wordText, container);
        };

        // Mouse leave handler
        const mouseLeaveHandler = (event) => {
            this.handleMouseLeave(wordId, wordIndex, wordText, container);
        };

        // Add event listeners
        container.addEventListener('click', leftClickHandler);
        container.addEventListener('contextmenu', rightClickHandler);
        container.addEventListener('mouseenter', mouseEnterHandler);
        container.addEventListener('mouseleave', mouseLeaveHandler);

        // Store references for cleanup
        this.eventListeners.set(wordId, {
            element: container,
            click: leftClickHandler,
            contextmenu: rightClickHandler,
            mouseenter: mouseEnterHandler,
            mouseleave: mouseLeaveHandler
        });
    }

    // Handle left click on word container
    handleLeftClick(wordId, wordIndex, wordText, container) {
        
        // Add visual feedback
        container.classList.add('mouse-left-click');
        setTimeout(() => {
            container.classList.remove('mouse-left-click');
        }, 150);

        // Call Python backend API
        this.sendWordInteractionToPython('left-click', {
            wordId,
            wordIndex,
            wordText,
            startTime: container.dataset.startTime,
            endTime: container.dataset.endTime
        });
    }

    // Handle right click on word container
    handleRightClick(wordId, wordIndex, wordText, container) {
        
        // Add visual feedback
        container.classList.add('mouse-right-click');
        setTimeout(() => {
            container.classList.remove('mouse-right-click');
        }, 150);

        // Call Python backend API
        this.sendWordInteractionToPython('right-click', {
            wordId,
            wordIndex,
            wordText,
            startTime: container.dataset.startTime,
            endTime: container.dataset.endTime
        });
    }

    // Handle mouse enter
    handleMouseEnter(wordId, wordIndex, wordText, container) {
        // Enhanced hover effect is handled by CSS
        // This can be used for additional JavaScript-based interactions
        this.sendWordInteractionToPython('hover-enter', {
            wordId,
            wordIndex,
            wordText
        });
    }

    // Handle mouse leave
    handleMouseLeave(wordId, wordIndex, wordText, container) {
        // Clean up any temporary states
        container.classList.remove('mouse-left-click', 'mouse-right-click');
    }

    // Send interaction data to Python backend
    async sendWordInteractionToPython(action, data) {
        try {
            const response = await fetch('/word-interaction', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    action,
                    data,
                    timestamp: Date.now()
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            // Handle any response from Python
            if (result.action) {
                this.handlePythonResponse(result);
            }

        } catch (error) {
            // Silently handle interaction errors
        }
    }

    // Handle responses from Python backend
    handlePythonResponse(response) {
        switch (response.action) {
            case 'highlight-word':
                this.highlightWord(response.wordId);
                break;
            case 'play-word-audio':
                this.playWordAudio(response.wordId, response.startTime, response.endTime);
                break;
            case 'show-word-info':
                this.showWordInfo(response.wordData);
                break;
            case 'show-vocabulary-info':
                this.showVocabularyInfo(response.vocabularyData);
                break;
            case 'show-translation-popup':
                this.showTranslationPopup(response.wordId, response.wordText, response.translation);
                break;
            default:
                // Handle unknown response actions silently
        }
    }

    // Utility functions for Python-triggered actions
    highlightWord(wordId) {
        // Only highlight with yellow when audio is playing
        if (!window.currentAudio || window.currentAudio.paused) {
            return;
        }
        
        const container = document.getElementById(wordId);
        if (container) {
            container.classList.add('bg-yellow-400');
            setTimeout(() => {
                container.classList.remove('bg-yellow-400');
            }, 1000);
        }
    }

    playWordAudio(wordId, startTime, endTime) {
        if (window.currentAudio && startTime && endTime) {
            window.currentAudio.currentTime = parseFloat(startTime) / 1000;
            window.currentAudio.play();
            
            // Stop at end time
            setTimeout(() => {
                if (window.currentAudio) {
                    window.currentAudio.pause();
                }
            }, (parseFloat(endTime) - parseFloat(startTime)));
        }
    }

    showWordInfo(wordData) {
        // This could show a tooltip or modal with word information
    }

    async showVocabularyInfo(vocabularyData) {
        
        try {
            // Auto-switch to Word Info tab only if not already active
            const wordInfoTab = document.getElementById('tab-word-info-btn');
            if (wordInfoTab && !wordInfoTab.classList.contains('active')) {
                // Trigger the tab switch
                wordInfoTab.click();
                // Wait a moment for the tab content to load
                await new Promise(resolve => setTimeout(resolve, 100));
            }

            // Call backend to get formatted HTML for vocabulary display
            const response = await fetch('/vocabulary-display', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    vocabularyData: vocabularyData
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const htmlContent = await response.text();
            
            // Update only the vocabulary content area, preserve header and status
            const vocabularyContent = document.getElementById('vocabulary-content');
            if (vocabularyContent) {
                vocabularyContent.innerHTML = htmlContent;
                
                // Notify status manager that word definition is being shown
                if (window.vocabStatusManager && vocabularyData.word) {
                    window.vocabStatusManager.notifyWordShown(vocabularyData.word);
                }
            }

        } catch (error) {
            // Silently handle vocabulary display errors
        }
    }

    showTranslationPopup(wordId, wordText, translation) {
        
        // Remove any existing popups
        this.removeTranslationPopup();
        
        // Get the word container to position popup near it
        const wordContainer = document.getElementById(wordId);
        if (!wordContainer) {
            return;
        }
        
        // Calculate popup position
        const rect = wordContainer.getBoundingClientRect();
        const popupX = rect.left + (rect.width / 2);
        const popupY = rect.bottom + 10;
        
        // Create popup element
        const popup = document.createElement('div');
        popup.id = 'translation-popup';
        popup.className = 'translation-popup';
        popup.innerHTML = `
            <div class="popup-content">
                <div class="popup-header">
                    <span class="chinese-word">${wordText}</span>
                    <button class="popup-close" onclick="window.karaokeInteractionManager.removeTranslationPopup()">×</button>
                </div>
                <div class="popup-body">
                    <div class="translation-text">${translation}</div>
                    <button class="define-btn" onclick="window.karaokeInteractionManager.defineWord('${wordText}')">Define</button>
                </div>
            </div>
        `;
        
        // Position the popup
        popup.style.position = 'fixed';
        popup.style.left = popupX + 'px';
        popup.style.top = popupY + 'px';
        popup.style.zIndex = '1000';
        
        // Add to document
        document.body.appendChild(popup);
        
        // Auto-hide after 8 seconds
        setTimeout(() => {
            this.removeTranslationPopup();
        }, 8000);
    }

    removeTranslationPopup() {
        const existingPopup = document.getElementById('translation-popup');
        if (existingPopup) {
            existingPopup.remove();
        }
    }

    async defineWord(wordText) {
        // AI-powered word definition generation
        try {
            // Find the word container to get wordId
            const wordContainers = document.querySelectorAll('.word-part');
            let wordId = null;
            
            for (const container of wordContainers) {
                if (container.dataset.wordText === wordText) {
                    wordId = container.id;
                    break;
                }
            }
            
            if (!wordId) {
                console.error(`Could not find word container for: ${wordText}`);
                this.showDefineError('Word container not found');
                return;
            }
            
            // Update DEFINE button to show loading state
            this.updateDefineButton('loading');
            
            // Call the backend /define-word endpoint
            const currentSession = getCurrentSession(); // Get current session ID
            
            const response = await fetch('/define-word', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    word: wordText,
                    wordId: wordId,
                    currentSessionId: currentSession
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Definition generated successfully
                this.updateDefineButton('success');
                
                // Update the word container styling to show it's now in database
                this.updateWordContainerAfterDefine(wordId);
                
                // Show vocabulary information in right sidebar
                if (result.vocabularyData) {
                    await this.showVocabularyInfo(result.vocabularyData);
                }
                
                // Remove the popup after a short delay
                setTimeout(() => {
                    this.removeTranslationPopup();
                }, 2000);
                
            } else {
                // Definition generation failed
                console.error('Definition generation failed:', result.error);
                this.updateDefineButton('error');
                this.showDefineError(result.error || 'Definition generation failed');
            }
            
        } catch (error) {
            console.error('Error defining word:', error);
            this.updateDefineButton('error');
            this.showDefineError('Network error or service unavailable');
        }
    }
    
    updateDefineButton(state) {
        const defineBtn = document.querySelector('.define-btn');
        if (!defineBtn) return;
        
        switch (state) {
            case 'loading':
                defineBtn.innerHTML = '⏳ Defining...';
                defineBtn.disabled = true;
                defineBtn.style.opacity = '0.7';
                break;
                
            case 'success':
                defineBtn.innerHTML = '✅ Defined!';
                defineBtn.disabled = true;
                defineBtn.style.backgroundColor = '#10b981';
                defineBtn.style.color = 'white';
                break;
                
            case 'error':
                defineBtn.innerHTML = '❌ Failed';
                defineBtn.disabled = false;
                defineBtn.style.backgroundColor = '#ef4444';
                defineBtn.style.color = 'white';
                break;
                
            default:
                defineBtn.innerHTML = 'Define';
                defineBtn.disabled = false;
                defineBtn.style.opacity = '1';
                defineBtn.style.backgroundColor = '';
                defineBtn.style.color = '';
        }
    }
    
    updateWordContainerAfterDefine(wordId) {
        const wordContainer = document.getElementById(wordId);
        if (wordContainer) {
            // Add vocabulary word styling
            wordContainer.classList.add('vocab-word');
            
            // Update visual styling to match other vocabulary words
            wordContainer.style.backgroundColor = 'rgba(173, 216, 230, 0.8)';
            wordContainer.style.border = '1px solid #7dd3fc';
        }
    }
    
    showDefineError(errorMessage) {
        // Show error message in the popup
        const popup = document.getElementById('translation-popup');
        if (popup) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'define-error';
            errorDiv.style.cssText = 'color: #ef4444; font-size: 12px; margin-top: 8px; padding: 4px;';
            errorDiv.textContent = errorMessage;
            
            const popupBody = popup.querySelector('.popup-body');
            if (popupBody) {
                // Remove any existing error messages
                const existingError = popupBody.querySelector('.define-error');
                if (existingError) {
                    existingError.remove();
                }
                popupBody.appendChild(errorDiv);
            }
        }
    }

    // Clean up all event listeners
    cleanup() {
        
        this.eventListeners.forEach((listeners, wordId) => {
            const element = listeners.element;
            if (element) {
                element.removeEventListener('click', listeners.click);
                element.removeEventListener('contextmenu', listeners.contextmenu);
                element.removeEventListener('mouseenter', listeners.mouseenter);
                element.removeEventListener('mouseleave', listeners.mouseleave);
            }
        });

        this.eventListeners.clear();
        this.isInitialized = false;
    }

    // Toggle context menu prevention
    setPreventContextMenu(prevent) {
        this.preventContextMenu = prevent;
    }
}

// Global instance
window.karaokeInteractionManager = new KaraokeInteractionManager();

// Initialize interactions when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Karaoke interaction manager ready
});

// Auto-initialize interactions when new content is loaded
const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        if (mutation.type === 'childList') {
            const addedNodes = Array.from(mutation.addedNodes);
            const hasWordContainers = addedNodes.some(node => 
                node.nodeType === Node.ELEMENT_NODE && 
                (node.classList?.contains('word-part') || 
                 node.querySelector?.('.word-part'))
            );
            
            if (hasWordContainers) {
                // Use requestAnimationFrame for proper DOM sync
                requestAnimationFrame(() => {
                    window.karaokeInteractionManager.initializeWordInteractions();
                });
            }
        }
    });
});

// Start observing changes in the text display area
const textDisplay = document.getElementById('text-display');
if (textDisplay) {
    observer.observe(textDisplay, {
        childList: true,
        subtree: true
    });
}

// Global function for word list clicks - uses existing system
function wordListClick(chineseWord) {
    if (window.karaokeInteractionManager) {
        window.karaokeInteractionManager.sendWordInteractionToPython('left-click', {
            wordText: chineseWord
        });
    }
}