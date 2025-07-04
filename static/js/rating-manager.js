/**
 * Rating Manager for FastTTS Star Rating System
 * Handles client-side rating interactions and HTMX integration
 */

class RatingManager {
    constructor() {
        this.isInitialized = false;
        this.pendingUpdates = new Map();
        this.updateTimeout = 500; // Debounce timeout for database updates
        this.init();
    }

    /**
     * Initialize the rating manager
     */
    init() {
        if (this.isInitialized) return;
        
        this.setupEventListeners();
        this.initializeExistingRatings();
        this.isInitialized = true;
        
        console.log('Rating Manager initialized successfully');
    }

    /**
     * Set up event listeners for rating interactions
     */
    setupEventListeners() {
        // Listen for new star rating elements added to DOM
        document.addEventListener('htmx:afterSettle', (event) => {
            this.initializeNewRatings(event.target);
        });

        // Listen for successful rating updates
        document.addEventListener('htmx:afterRequest', (event) => {
            if (event.detail.xhr && event.detail.xhr.status === 200) {
                const target = event.target;
                if (target && target.classList.contains('star-rating')) {
                    this.handleRatingUpdateSuccess(target);
                }
            }
        });

        // Listen for rating update errors
        document.addEventListener('htmx:responseError', (event) => {
            const target = event.target;
            if (target && target.classList.contains('star-rating')) {
                this.handleRatingUpdateError(target, event.detail);
            }
        });

    }

    /**
     * Initialize existing rating elements in the DOM
     */
    initializeExistingRatings() {
        // Only initialize interactive star ratings, not readonly ones
        const ratingElements = document.querySelectorAll('.star-rating:not(.star-rating-readonly):not([disabled])');
        ratingElements.forEach(element => {
            this.initializeRatingElement(element);
        });
    }

    /**
     * Initialize new rating elements added via HTMX
     */
    initializeNewRatings(container) {
        if (!container) return;
        
        // Only initialize interactive star ratings, not readonly ones
        const ratingElements = container.querySelectorAll('.star-rating:not(.star-rating-readonly):not([disabled])');
        ratingElements.forEach(element => {
            this.initializeRatingElement(element);
        });
    }

    /**
     * Initialize a single rating element
     */
    initializeRatingElement(element) {
        if (!element || element.dataset.initialized) return;
        
        // Skip readonly or disabled elements
        if (element.disabled || element.classList.contains('star-rating-readonly')) {
            return;
        }

        const chineseWord = element.dataset.chineseWord;
        if (!chineseWord) {
            console.warn('Star rating element missing chinese word data:', element);
            return;
        }

        // Add input event listener for real-time updates
        element.addEventListener('input', (event) => {
            this.handleRatingInput(event);
        });

        // Add keyboard support
        element.addEventListener('keydown', (event) => {
            this.handleRatingKeydown(event);
        });

        // Mark as initialized
        element.dataset.initialized = 'true';
    }

    /**
     * Handle rating input changes
     */
    handleRatingInput(event) {
        const element = event.target;
        const chineseWord = element.dataset.chineseWord;
        const newRating = parseFloat(element.value);

        if (!chineseWord || isNaN(newRating)) return;

        // Update visual display immediately
        this.updateRatingDisplay(chineseWord, newRating);
        
        
        // Debounce database updates to avoid too many requests
        this.debouncedUpdateRating(chineseWord, newRating);
        
        // Auto-route to word list tab after rating change in Word Info tab
        const isInWordInfo = element.closest('.vocab-card');
        if (isInWordInfo) {
            setTimeout(() => {
                // First, silently refresh word list data in background
                htmx.ajax('GET', '/tab-word-list', {
                    target: '#vocab-tab-contents .tab-pane:nth-child(2)',
                    swap: 'innerHTML'
                });
                
                // Then switch to word list tab to show updated rating (as user requested)
                const wordListTab = document.getElementById('tab-word-list-btn');
                if (wordListTab) {
                    wordListTab.click();
                }
            }, 300); // Slightly longer delay to ensure rating saves and refresh completes
        }
    }

    /**
     * Handle keyboard navigation for ratings
     */
    handleRatingKeydown(event) {
        const element = event.target;
        const currentValue = parseFloat(element.value);
        let newValue = currentValue;

        switch (event.key) {
            case 'ArrowLeft':
            case 'ArrowDown':
                newValue = Math.max(0.5, currentValue - 0.5);
                break;
            case 'ArrowRight':
            case 'ArrowUp':
                newValue = Math.min(5.0, currentValue + 0.5);
                break;
            case 'Home':
                newValue = 0.5;
                break;
            case 'End':
                newValue = 5.0;
                break;
            default:
                return; // Don't prevent default for other keys
        }

        if (newValue !== currentValue) {
            event.preventDefault();
            element.value = newValue;
            element.style.setProperty('--val', newValue);
            
            // Trigger input event for consistency
            element.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }

    /**
     * Update rating display elements
     */
    updateRatingDisplay(chineseWord, rating) {
        const sanitizedWord = chineseWord.replace(/\s/g, '-');
        
        // Convert rating to number if it's a string
        const numericRating = typeof rating === 'string' ? parseFloat(rating) : rating;
        
        // Validate rating is a valid number
        if (isNaN(numericRating)) {
            console.warn(`Invalid rating value for ${chineseWord}:`, rating);
            return;
        }
        
        // Update display value
        const displayElement = document.getElementById(`rating-display-${sanitizedWord}`);
        if (displayElement) {
            displayElement.textContent = numericRating.toFixed(1);
        }

        // Update compact display title
        const compactContainer = document.getElementById(`compact-star-rating-container-${sanitizedWord}`);
        if (compactContainer) {
            compactContainer.title = `Rating: ${numericRating.toFixed(1)}/5 stars`;
        }

        // Update aria-label for accessibility
        const ratingInput = document.getElementById(`rating-${sanitizedWord}`) || 
                           document.getElementById(`compact-rating-${sanitizedWord}`);
        if (ratingInput) {
            ratingInput.setAttribute('aria-label', `Rate word ${chineseWord}: ${numericRating.toFixed(1)} stars`);
        }
    }

    /**
     * Debounced rating update to prevent excessive API calls
     */
    debouncedUpdateRating(chineseWord, rating) {
        // Clear existing timeout for this word
        if (this.pendingUpdates.has(chineseWord)) {
            clearTimeout(this.pendingUpdates.get(chineseWord));
        }

        // Set new timeout
        const timeoutId = setTimeout(() => {
            this.updateRatingInDatabase(chineseWord, rating);
            this.pendingUpdates.delete(chineseWord);
        }, this.updateTimeout);

        this.pendingUpdates.set(chineseWord, timeoutId);
    }

    /**
     * Update rating in database via HTMX
     */
    updateRatingInDatabase(chineseWord, rating) {
        const encodedWord = encodeURIComponent(chineseWord);
        
        // Create form data
        const formData = new FormData();
        formData.append('value', rating.toString());

        // Send HTMX request
        htmx.ajax('POST', `/update-rating/${encodedWord}`, {
            values: { value: rating.toString() },
            swap: 'none'
        }).then(() => {
            console.log(`Rating updated successfully for "${chineseWord}": ${rating}`);
        }).catch((error) => {
            console.error(`Failed to update rating for "${chineseWord}":`, error);
            this.handleRatingUpdateError(null, { error });
        });
    }

    /**
     * Handle successful rating update
     */
    handleRatingUpdateSuccess(element) {
        if (!element) return;
        
        const chineseWord = element.dataset.chineseWord;
        if (chineseWord) {
            console.log(`Rating update confirmed for "${chineseWord}"`);
            
            // Add visual feedback (subtle flash)
            element.style.transition = 'all 0.2s ease';
            element.style.transform = 'scale(1.05)';
            
            setTimeout(() => {
                element.style.transform = 'scale(1)';
            }, 200);
        }
    }

    /**
     * Handle rating update errors
     */
    handleRatingUpdateError(element, detail) {
        const chineseWord = element?.dataset?.chineseWord || 'unknown word';
        console.error(`Failed to update rating for "${chineseWord}":`, detail);
        
        // Show user feedback (could be expanded to show toast notification)
        if (element) {
            element.style.transition = 'all 0.2s ease';
            element.style.filter = 'hue-rotate(300deg)'; // Red tint
            
            setTimeout(() => {
                element.style.filter = '';
            }, 1000);
        }
    }

    /**
     * Get current rating for a word
     */
    async getCurrentRating(chineseWord) {
        try {
            const encodedWord = encodeURIComponent(chineseWord);
            const response = await fetch(`/get-rating/${encodedWord}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            return data.success ? data.rating : null;
        } catch (error) {
            console.error(`Failed to get rating for "${chineseWord}":`, error);
            return null;
        }
    }

    /**
     * Set rating for a word programmatically
     */
    setRating(chineseWord, rating) {
        if (typeof rating !== 'number' || rating < 0.5 || rating > 5.0) {
            console.error('Invalid rating value:', rating);
            return false;
        }

        // Round to nearest 0.5
        const roundedRating = Math.round(rating * 2) / 2;
        
        // Find rating element
        const sanitizedWord = chineseWord.replace(/\s/g, '-');
        const ratingInput = document.getElementById(`rating-${sanitizedWord}`) || 
                           document.getElementById(`compact-rating-${sanitizedWord}`);
        
        if (ratingInput) {
            ratingInput.value = roundedRating;
            ratingInput.style.setProperty('--val', roundedRating);
            this.updateRatingDisplay(chineseWord, roundedRating);
            this.debouncedUpdateRating(chineseWord, roundedRating);
            return true;
        }
        
        console.warn(`Rating element not found for word: ${chineseWord}`);
        return false;
    }

    /**
     * Get all ratings from the current page
     */
    getAllPageRatings() {
        const ratings = {};
        const ratingElements = document.querySelectorAll('.star-rating[data-chinese-word]');
        
        ratingElements.forEach(element => {
            const chineseWord = element.dataset.chineseWord;
            const rating = parseFloat(element.value);
            
            if (chineseWord && !isNaN(rating)) {
                ratings[chineseWord] = rating;
            }
        });
        
        return ratings;
    }


    /**
     * Clear all pending updates (useful for cleanup)
     */
    clearPendingUpdates() {
        this.pendingUpdates.forEach(timeoutId => {
            clearTimeout(timeoutId);
        });
        this.pendingUpdates.clear();
    }

    /**
     * Destroy the rating manager
     */
    destroy() {
        this.clearPendingUpdates();
        this.isInitialized = false;
        console.log('Rating Manager destroyed');
    }
}

// Global functions for inline event handlers (backward compatibility)
window.updateRatingDisplay = function(chineseWord, rating) {
    if (window.ratingManager) {
        window.ratingManager.updateRatingDisplay(chineseWord, rating);
    }
};

window.updateCompactRatingDisplay = function(chineseWord, rating) {
    if (window.ratingManager) {
        window.ratingManager.updateRatingDisplay(chineseWord, rating);
    }
};

// Initialize global rating manager when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (!window.ratingManager) {
        window.ratingManager = new RatingManager();
    }
});

// Also initialize if script is loaded after DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        if (!window.ratingManager) {
            window.ratingManager = new RatingManager();
        }
    });
} else {
    if (!window.ratingManager) {
        window.ratingManager = new RatingManager();
    }
}