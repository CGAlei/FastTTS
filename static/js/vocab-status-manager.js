// Vocabulary Status Manager
// Handles smart status display based on current state

class VocabStatusManager {
    constructor() {
        this.statusElement = null;
        this.currentState = 'default';
        this.databaseInfo = null;
        this.lastRefreshStats = null;
        
        this.initializeElements();
        this.loadDatabaseInfo();
    }
    
    initializeElements() {
        this.statusElement = document.getElementById('vocab-status-bar');
        this.dbWordCountElement = document.getElementById('db-word-count');
        this.dbModifiedTimeElement = document.getElementById('db-modified-time');
        this.dbStatusIconElement = document.getElementById('db-status-icon');
        this.statusCapsuleElement = document.querySelector('.status-capsule');
        this.instructionElement = document.getElementById('vocabulary-instruction');
    }
    
    async loadDatabaseInfo() {
        try {
            const response = await fetch('/vocab-stats');
            const stats = await response.json();
            
            this.databaseInfo = stats.database || {};
            this.lastRefreshStats = stats.last_refresh || {};
            
            // Update capsules on load
            this.updateCapsules();
            
        } catch (error) {
            console.error('Error loading database info:', error);
            this.updateCapsules({
                wordCount: '!',
                modifiedTime: 'Error',
                statusIcon: '⚠️',
                statusClass: 'refresh-needed'
            });
        }
    }
    
    updateCapsules(overrides = {}) {
        const dbInfo = this.databaseInfo;
        const refreshInfo = this.lastRefreshStats;
        
        // Update word count
        const wordCount = overrides.wordCount || dbInfo.total_words || 0;
        if (this.dbWordCountElement) {
            this.dbWordCountElement.textContent = wordCount;
        }
        
        // Update modified time - compact format
        let modifiedTime = overrides.modifiedTime;
        if (!modifiedTime && dbInfo.last_modified) {
            modifiedTime = this.getCompactTimeAgo(new Date(dbInfo.last_modified));
        }
        if (this.dbModifiedTimeElement) {
            this.dbModifiedTimeElement.textContent = modifiedTime || '--';
        }
        
        // Update status
        let statusIcon = overrides.statusIcon;
        let statusClass = overrides.statusClass;
        
        if (!statusIcon) {
            if (refreshInfo.last_refresh) {
                statusIcon = '✓';
                statusClass = 'current';
            } else {
                statusIcon = '⚡';
                statusClass = 'refresh-needed';
            }
        }
        
        if (this.dbStatusIconElement) {
            this.dbStatusIconElement.textContent = statusIcon || '--';
        }
        
        if (this.statusCapsuleElement) {
            // Remove old status classes
            this.statusCapsuleElement.classList.remove('current', 'refresh-needed');
            // Add new status class
            if (statusClass) {
                this.statusCapsuleElement.classList.add(statusClass);
            }
        }
    }
    
    setState(state, data = {}) {
        this.currentState = state;
        
        switch (state) {
            case 'default':
                this.showDefaultState();
                break;
                
            case 'word-definition':
                this.showWordDefinitionState(data);
                break;
                
            case 'refreshing':
                this.showRefreshingState(data);
                break;
                
            case 'refresh-complete':
                this.showRefreshCompleteState(data);
                break;
                
            case 'error':
                this.showErrorState(data.message || 'An error occurred');
                break;
                
            default:
                this.showDefaultState();
        }
    }
    
    showDefaultState() {
        // Update capsules with current database info
        this.updateCapsules();
        
        // Show instruction message
        if (this.instructionElement) {
            this.instructionElement.style.display = 'block';
        }
    }
    
    showWordDefinitionState(data) {
        // Keep capsules updated
        this.updateCapsules();
        
        // Hide instruction message when showing word definition
        if (this.instructionElement) {
            this.instructionElement.style.display = 'none';
        }
    }
    
    showRefreshingState(data) {
        // Update capsules to show refreshing status
        this.updateCapsules({
            statusIcon: '🔄',
            statusClass: 'refresh-needed'
        });
        
        // Hide instruction message during refresh
        if (this.instructionElement) {
            this.instructionElement.style.display = 'none';
        }
    }
    
    showRefreshCompleteState(data) {
        const stats = data.stats || {};
        
        // Update capsules with fresh data
        this.updateCapsules({
            wordCount: stats.vocabulary_count || this.databaseInfo.total_words || 0,
            modifiedTime: 'NOW',
            statusIcon: '✅',
            statusClass: 'current'
        });
        
        // Auto-return to default state after 3 seconds
        setTimeout(() => {
            if (this.currentState === 'refresh-complete') {
                this.loadDatabaseInfo(); // Reload fresh data
            }
        }, 3000);
    }
    
    showErrorState(message) {
        // Update capsules to show error state
        this.updateCapsules({
            statusIcon: '⚠️',
            statusClass: 'refresh-needed'
        });
        
        // Show instruction message with error note
        if (this.instructionElement) {
            this.instructionElement.style.display = 'block';
            this.instructionElement.innerHTML = `Error: ${message}. Click refresh button to try again.`;
            this.instructionElement.className = 'text-center text-red-500 py-8 px-4';
        }
    }
    
    // Helper methods
    extractDatabaseName(path) {
        if (!path) return 'Unknown';
        return path.split('/').pop() || path;
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
    
    formatDate(date) {
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    }
    
    getTimeAgo(date) {
        const now = new Date();
        const diff = now - date;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);
        
        if (minutes < 1) return 'just now';
        if (minutes < 60) return `${minutes}m ago`;
        if (hours < 24) return `${hours}h ago`;
        return `${days}d ago`;
    }
    
    getCompactTimeAgo(date) {
        const now = new Date();
        const diff = now - date;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);
        
        if (minutes < 1) return 'NOW';
        if (minutes < 60) return `${minutes}m`;
        if (hours < 24) return `${hours}h`;
        if (days < 7) return `${days}d`;
        return `${Math.floor(days / 7)}w`;
    }
    
    // Public API methods
    updateDatabaseInfo(newInfo) {
        this.databaseInfo = newInfo;
        this.updateCapsules();
    }
    
    updateRefreshStats(newStats) {
        this.lastRefreshStats = newStats;
        this.updateCapsules();
    }
    
    notifyWordShown(word) {
        this.setState('word-definition', { word });
    }
    
    notifyRefreshStarted() {
        this.setState('refreshing', { progress: 0, message: 'Initializing refresh...' });
    }
    
    notifyRefreshProgress(progress, message) {
        this.setState('refreshing', { progress, message });
    }
    
    notifyRefreshComplete(stats) {
        this.setState('refresh-complete', { stats });
    }
    
    notifyRefreshError(error) {
        this.setState('error', { message: error });
    }
    
    reset() {
        this.setState('default');
        // Reset instruction message styling
        if (this.instructionElement) {
            this.instructionElement.className = 'text-center text-gray-500 py-8 px-4';
            this.instructionElement.innerHTML = '点击文本中的汉字以查看词汇解释和相关信息。';
        }
    }
}

// Global instance
let vocabStatusManager;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    vocabStatusManager = new VocabStatusManager();
    
    // Make globally accessible
    window.vocabStatusManager = vocabStatusManager;
});

// Export for use in other modules
window.VocabStatusManager = VocabStatusManager;