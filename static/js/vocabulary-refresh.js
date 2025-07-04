// Vocabulary Refresh Manager
// Handles vocabulary database refresh functionality

class VocabularyRefreshManager {
    constructor() {
        this.isRefreshing = false;
        this.refreshButton = null;
        this.statusElement = null;
        this.eventSource = null;
        this.refreshSessionId = null;
        
        this.initializeElements();
        this.loadInitialStats();
    }
    
    initializeElements() {
        this.refreshButton = document.getElementById('refresh-vocab-btn');
        this.statusElement = document.getElementById('vocab-status');
        
        if (this.refreshButton) {
            this.refreshButton.addEventListener('click', () => this.startRefresh());
        }
    }
    
    async loadInitialStats() {
        try {
            const response = await fetch('/vocab-stats');
            const stats = await response.json();
            
            this.updateStatus(stats);
        } catch (error) {
            console.error('Error loading vocabulary stats:', error);
            this.updateStatusText('Failed to load vocabulary statistics');
        }
    }
    
    updateStatus(stats) {
        if (!this.statusElement) return;
        
        const dbStats = stats.database || {};
        const refreshStats = stats.last_refresh || {};
        const needsRefresh = stats.needs_refresh || false;
        
        let statusHtml = '';
        
        // Database information
        if (dbStats.exists) {
            statusHtml += `<div class="text-xs text-gray-600 mb-1">`;
            statusHtml += `📚 Database: ${dbStats.total_words || 0} words`;
            if (dbStats.file_size) {
                const sizeKB = Math.round(dbStats.file_size / 1024);
                statusHtml += ` (${sizeKB}KB)`;
            }
            statusHtml += `</div>`;
        } else {
            statusHtml += `<div class="text-xs text-red-500 mb-1">⚠️ Database not found</div>`;
        }
        
        // Last refresh information
        if (refreshStats.last_refresh) {
            const refreshDate = new Date(refreshStats.last_refresh);
            const timeAgo = this.getTimeAgo(refreshDate);
            
            statusHtml += `<div class="text-xs text-gray-500 mb-1">`;
            statusHtml += `🔄 Last refresh: ${timeAgo}`;
            if (refreshStats.sessions_processed) {
                statusHtml += ` (${refreshStats.sessions_processed} sessions)`;
            }
            statusHtml += `</div>`;
        } else {
            statusHtml += `<div class="text-xs text-orange-500 mb-1">⚡ Never refreshed</div>`;
        }
        
        // Refresh recommendation
        if (needsRefresh) {
            statusHtml += `<div class="text-xs text-blue-600 font-medium">💡 Refresh recommended</div>`;
        }
        
        this.statusElement.innerHTML = statusHtml;
    }
    
    updateStatusText(message, isError = false) {
        if (!this.statusElement) return;
        
        const className = isError ? 'text-red-500' : 'text-gray-600';
        this.statusElement.innerHTML = `<div class="text-xs ${className}">${message}</div>`;
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
    
    async startRefresh() {
        if (this.isRefreshing) {
            console.log('Refresh already in progress');
            return;
        }
        
        this.isRefreshing = true;
        this.refreshSessionId = `refresh_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        try {
            // Update UI state
            this.setRefreshingState(true);
            this.updateStatusText('🔄 Starting vocabulary refresh...');
            
            // Notify status manager about refresh start
            if (window.vocabStatusManager) {
                window.vocabStatusManager.notifyRefreshStarted();
            }
            
            // Start SSE connection for progress updates
            this.startProgressMonitoring();
            
            // Start refresh process
            const response = await fetch('/refresh-vocabulary', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                console.log('Vocabulary refresh completed successfully:', result);
                this.onRefreshCompleted(result);
            } else {
                throw new Error(result.error || 'Refresh failed');
            }
            
        } catch (error) {
            console.error('Vocabulary refresh error:', error);
            this.onRefreshError(error);
        }
    }
    
    startProgressMonitoring() {
        if (this.eventSource) {
            this.eventSource.close();
        }
        
        const url = `/refresh-vocabulary-progress/${this.refreshSessionId}`;
        this.eventSource = new EventSource(url);
        
        this.eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleProgressUpdate(data);
            } catch (error) {
                console.error('Error parsing SSE data:', error);
            }
        };
        
        this.eventSource.onerror = (error) => {
            console.error('SSE connection error:', error);
            this.eventSource.close();
        };
    }
    
    handleProgressUpdate(data) {
        switch (data.type) {
            case 'connected':
                console.log('Progress monitoring connected');
                break;
                
            case 'progress_update':
                this.updateStatusText(`🔄 ${data.message} (${data.progress}%)`);
                
                // Notify status manager about progress
                if (window.vocabStatusManager) {
                    window.vocabStatusManager.notifyRefreshProgress(data.progress, data.message);
                }
                break;
                
            case 'completed':
                this.onRefreshCompleted(data);
                this.eventSource.close();
                break;
                
            case 'error':
                this.onRefreshError(new Error(data.message));
                this.eventSource.close();
                break;
                
            default:
                console.log('Unknown progress update type:', data.type);
        }
    }
    
    onRefreshCompleted(result) {
        this.isRefreshing = false;
        this.setRefreshingState(false);
        
        const stats = result.stats || {};
        let message = '✅ Refresh completed';
        
        if (stats.sessions_processed) {
            message += ` • ${stats.sessions_processed} sessions`;
        }
        if (stats.words_updated) {
            message += ` • ${stats.words_updated} words updated`;
        }
        if (stats.duration_seconds) {
            message += ` • ${stats.duration_seconds.toFixed(1)}s`;
        }
        
        this.updateStatusText(message);
        
        // Reload stats after a short delay
        setTimeout(() => {
            this.loadInitialStats();
        }, 2000);
        
        // Show success notification
        this.showNotification('Vocabulary refresh completed successfully', 'success');
        
        // Notify status manager about completion
        if (window.vocabStatusManager) {
            window.vocabStatusManager.notifyRefreshComplete(stats);
        }
    }
    
    onRefreshError(error) {
        this.isRefreshing = false;
        this.setRefreshingState(false);
        
        const message = `❌ Refresh failed: ${error.message}`;
        this.updateStatusText(message, true);
        
        // Show error notification
        this.showNotification(`Vocabulary refresh failed: ${error.message}`, 'error');
        
        // Notify status manager about error
        if (window.vocabStatusManager) {
            window.vocabStatusManager.notifyRefreshError(error.message);
        }
        
        // Reload stats to get current state
        setTimeout(() => {
            this.loadInitialStats();
        }, 2000);
    }
    
    setRefreshingState(isRefreshing) {
        if (!this.refreshButton) return;
        
        if (isRefreshing) {
            this.refreshButton.disabled = true;
            this.refreshButton.innerHTML = '⏳';
            this.refreshButton.title = 'Refresh in progress...';
            this.refreshButton.classList.add('refreshing');
        } else {
            this.refreshButton.disabled = false;
            this.refreshButton.innerHTML = '🔄';
            this.refreshButton.title = 'Refresh vocabulary state';
            this.refreshButton.classList.remove('refreshing');
        }
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `vocab-refresh-notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
    
    cleanup() {
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
        }
        
        this.isRefreshing = false;
        this.refreshSessionId = null;
    }
}

// Global refresh manager instance
let vocabularyRefreshManager;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    vocabularyRefreshManager = new VocabularyRefreshManager();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (vocabularyRefreshManager) {
        vocabularyRefreshManager.cleanup();
    }
});

// Global function for button onclick
function refreshVocabularyState() {
    if (vocabularyRefreshManager) {
        vocabularyRefreshManager.startRefresh();
    }
}