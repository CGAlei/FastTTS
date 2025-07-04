/**
 * Word Rating System for FastTTS
 * Handles 5-star rating functionality with cross-tab updates
 */

/**
 * Update word rating in database and refresh displays
 */
function updateWordRating(rating) {
    console.log('updateWordRating called with rating:', rating);
    
    const wordElement = document.getElementById('word-rating-input');
    if (!wordElement) {
        console.error('Rating input element not found');
        return;
    }
    
    const word = wordElement.getAttribute('data-word');
    console.log('Word from data-word attribute:', word);
    
    if (!word) {
        console.error('Word data not found on rating element');
        return;
    }
    
    // Show loading state
    wordElement.style.opacity = '0.7';
    
    console.log('Sending rating update request:', { word, rating: parseInt(rating) });
    
    // Send rating update to server
    fetch('/update-word-rating', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            word: word,
            rating: parseInt(rating)
        })
    })
    .then(response => {
        console.log('Response status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Response data:', data);
        if (data.success) {
            console.log(`Rating updated successfully for "${word}": ${rating} stars`);
            
            // Restore visual state
            wordElement.style.opacity = '1';
            
            // Show brief success feedback
            showRatingUpdateFeedback(`Rating saved: ${rating} star${rating === 1 ? '' : 's'}!`);
            
            // Update Word List tab display silently (without switching tabs)
            refreshWordListRatings();
            
        } else {
            console.error('Failed to update rating:', data.error);
            wordElement.style.opacity = '1';
        }
    })
    .catch(error => {
        console.error('Error updating rating:', error);
        wordElement.style.opacity = '1';
    });
}

/**
 * Refresh the Word List tab's rating displays without switching tabs
 */
function refreshWordListRatings() {
    console.log('refreshWordListRatings called');
    
    // Try to load the Word List tab first if it doesn't exist
    const wordListTab = document.getElementById('tab-word-list-btn');
    if (!wordListTab) {
        console.log('Word List tab button not found');
        return;
    }
    
    // Check if Word List tab has been loaded at least once
    const wordListContainer = document.getElementById('word-list-container');
    if (!wordListContainer) {
        console.log('Word List container not found, need to load tab first');
        // Trigger tab load without switching to it
        fetch('/tab-word-list')
            .then(response => response.text())
            .then(html => {
                // This will trigger a tab load so next time we can refresh it
                console.log('Word List tab content preloaded for future refreshes');
            })
            .catch(error => {
                console.error('Error preloading Word List tab:', error);
            });
        return;
    }
    
    // Now refresh the existing content
    console.log('Word List container found, refreshing content');
    
    // Use defaults if search elements don't exist yet
    let searchQuery = '';
    let page = '1';
    
    const currentSearchInput = document.querySelector('.word-search-input');
    const currentPage = document.getElementById('current-page');
    
    if (currentSearchInput) {
        searchQuery = currentSearchInput.value || '';
    }
    if (currentPage) {
        page = currentPage.value || '1';
    }
    
    console.log('Refreshing word list with:', { page, searchQuery });
    
    // Fetch updated word list data
    fetch(`/search-words?page=${page}&search=${encodeURIComponent(searchQuery)}`)
        .then(response => {
            console.log('Word list refresh response status:', response.status);
            return response.text();
        })
        .then(html => {
            // Always update the container to ensure fresh data
            wordListContainer.innerHTML = html;
            console.log('Word List container updated with fresh data');
        })
        .catch(error => {
            console.error('Error refreshing word list ratings:', error);
        });
}

/**
 * Show brief feedback when rating is updated
 */
function showRatingUpdateFeedback(message) {
    // Remove any existing feedback
    const existingFeedback = document.getElementById('rating-feedback');
    if (existingFeedback) {
        existingFeedback.remove();
    }
    
    // Create feedback element
    const feedback = document.createElement('div');
    feedback.id = 'rating-feedback';
    feedback.textContent = message;
    feedback.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #10b981;
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 10000;
        font-size: 14px;
        font-weight: 500;
        transition: all 0.3s ease;
        opacity: 0;
        transform: translateY(-10px);
    `;
    
    document.body.appendChild(feedback);
    
    // Animate in
    setTimeout(() => {
        feedback.style.opacity = '1';
        feedback.style.transform = 'translateY(0)';
    }, 10);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        feedback.style.opacity = '0';
        feedback.style.transform = 'translateY(-10px)';
        setTimeout(() => {
            feedback.remove();
        }, 300);
    }, 3000);
}

/**
 * Initialize rating system when page loads
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Word rating system initialized');
});

/**
 * Handle tab switches to ensure rating displays are current
 */
function onTabSwitch(tabName) {
    if (tabName === 'word-list') {
        // Ensure Word List ratings are up to date when switching to it
        setTimeout(refreshWordListRatings, 100);
    }
}

// Export functions for global access
window.updateWordRating = updateWordRating;
window.refreshWordListRatings = refreshWordListRatings;
window.onTabSwitch = onTabSwitch;