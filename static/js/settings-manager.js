// Settings Manager
// Handles settings popup, voice selection, and preferences

// Centralized default values
const DEFAULT_VOLUME = 1.3;
const DEFAULT_SPEED = 1.0;
const DEFAULT_VOICE = 'zh-CN-XiaoxiaoNeural';
const DEFAULT_ENGINE = 'edge';

class SettingsManager {
    constructor() {
        this.currentVoice = localStorage.getItem('selectedVoice') || DEFAULT_VOICE;
        this.currentSpeed = parseFloat(localStorage.getItem('selectedSpeed')) || DEFAULT_SPEED;
        this.currentVolume = parseFloat(localStorage.getItem('selectedVolume')) || DEFAULT_VOLUME;
        this.currentEngine = localStorage.getItem('selectedEngine') || DEFAULT_ENGINE;
        this.modal = null;
        this.voiceSelector = null;
        this.speedSlider = null;
        this.speedDisplay = null;
        this.volumeSlider = null;
        this.volumeDisplay = null;
        this.engineSelector = null;
        this.minimaxApiKey = null;
        this.minimaxGroupId = null;
        this.minimaxModel = null;
        this.minimaxCustomVoice = null;
        this.minimaxChunkSize = null;
        this.minimaxStatus = null;
        this.isInitialized = false;
        this.availableEngines = {};
        this.credentialsStatus = {};
    }

    // Initialize settings manager
    async initialize() {
        if (this.isInitialized) return;
        
        this.modal = document.getElementById('settings-modal');
        this.voiceSelector = document.getElementById('voice-selector');
        this.speedSlider = document.getElementById('speed-slider');
        this.speedDisplay = document.getElementById('speed-display');
        this.volumeSlider = document.getElementById('volume-slider');
        this.volumeDisplay = document.getElementById('volume-display');
        this.engineSelector = document.getElementById('engine-selector');
        this.minimaxApiKey = document.getElementById('minimax-api-key');
        this.minimaxGroupId = document.getElementById('minimax-group-id');
        this.minimaxModel = document.getElementById('minimax-model');
        this.minimaxCustomVoice = document.getElementById('minimax-custom-voice');
        this.minimaxChunkSize = document.getElementById('minimax-chunk-size');
        this.minimaxStatus = document.getElementById('minimax-status');
        
        // Load available engines info and credentials status
        await this.loadEnginesInfo();
        await this.loadCredentialsStatus();
        
        if (this.engineSelector) {
            this.engineSelector.value = this.currentEngine;
        }
        
        if (this.voiceSelector) {
            this.voiceSelector.value = this.currentVoice;
        }
        
        if (this.speedSlider) {
            this.speedSlider.value = this.currentSpeed;
            this.updateSpeedDisplay(this.currentSpeed);
        }
        
        if (this.volumeSlider) {
            this.volumeSlider.value = this.currentVolume;
            this.updateVolumeDisplay(this.currentVolume);
        }
        
        // Update voices based on current engine
        this.updateVoicesForEngine(this.currentEngine);
        
        this.isInitialized = true;
    }

    // Open settings popup
    openSettingsPopup() {
        this.initialize();
        if (this.modal) {
            // Ensure modal is on top of everything
            this.modal.style.zIndex = '1100';
            this.modal.style.display = 'flex';
            this.modal.style.alignItems = 'center';
            this.modal.style.justifyContent = 'center';
            this.modal.style.padding = '16px';
            this.modal.classList.remove('hidden');
            this.syncSettingsWithUI();
            
            // Initialize tab state and validate credentials
            setTimeout(() => {
                initializeSettingsTabs();
                this.validateMinimaxCredentials();
            }, 50);
            
            // Scroll to top of modal content when opened
            const modalContent = this.modal.querySelector('.modal-content');
            if (modalContent) {
                modalContent.scrollTop = 0;
            }
            
            // Prevent body scrolling when modal is open
            document.body.style.overflow = 'hidden';
        }
    }

    // Close settings popup
    closeSettingsPopup(event) {
        if (!this.modal) return;
        
        // Only close if clicking the close button (X) - don't close by clicking outside
        if (event && !event.target.classList.contains('close-btn')) {
            // Not clicking close button, don't close
            return;
        }
        
        this.modal.classList.add('hidden');
        this.modal.style.display = 'none';
        
        // Restore body scrolling when modal is closed
        document.body.style.overflow = '';
    }

    // Load engines information from backend
    async loadEnginesInfo() {
        try {
            const response = await fetch('/tts-engines-info');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            
            if (data.success) {
                this.availableEngines = data.engines;
            }
        } catch (error) {
            // Silently handle engine info loading errors
        }
    }

    // Load credentials status from backend
    async loadCredentialsStatus() {
        try {
            const response = await fetch('/credentials-status');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            
            if (data.success) {
                this.credentialsStatus = data.engines;
                this.updateCredentialsUI();
            }
        } catch (error) {
            // Silently handle credentials status loading errors
        }
    }

    // Sync settings popup with current UI state
    syncSettingsWithUI() {
        // Sync engine selector
        if (this.engineSelector) {
            this.engineSelector.value = this.currentEngine;
        }
        
        // Sync voice selector
        if (this.voiceSelector) {
            this.voiceSelector.value = this.currentVoice;
        }
        
        // Sync speed slider
        if (this.speedSlider) {
            this.speedSlider.value = this.currentSpeed;
            this.updateSpeedDisplay(this.currentSpeed);
        }
    }

    // Change TTS engine selection
    changeTTSEngine(engine) {
        this.currentEngine = engine;
        localStorage.setItem('selectedEngine', engine);
        
        // Update available voices for this engine
        this.updateVoicesForEngine(engine);
        
        // Show notification
        this.showNotification(`TTS Engine changed to: ${this.getEngineName(engine)}`);
    }

    // Update voice options based on selected engine
    updateVoicesForEngine(engine) {
        if (!this.voiceSelector || !this.availableEngines[engine]) {
            return;
        }
        
        const voices = this.availableEngines[engine].voices || [];
        const defaultVoice = this.availableEngines[engine].default_voice;
        
        // Clear existing options
        this.voiceSelector.innerHTML = '';
        
        let voiceSelected = false;
        
        // Add new options
        voices.forEach(voice => {
            const option = document.createElement('option');
            option.value = voice.id;
            option.textContent = voice.name;
            
            // Prioritize saved voice, then current voice, then default
            if (!voiceSelected && (voice.id === this.currentVoice || 
                                   (this.currentVoice && voice.id.includes(this.currentVoice)) ||
                                   voice.id === defaultVoice)) {
                option.selected = true;
                this.currentVoice = voice.id;
                localStorage.setItem('selectedVoice', voice.id);
                voiceSelected = true;
            }
            
            this.voiceSelector.appendChild(option);
        });
        
        // If no voice was selected, use the first available
        if (!voiceSelected && voices.length > 0) {
            this.voiceSelector.selectedIndex = 0;
            this.currentVoice = voices[0].id;
            localStorage.setItem('selectedVoice', voices[0].id);
        }
        
    }

    // Change voice selection
    changeVoice(voice) {
        this.currentVoice = voice;
        localStorage.setItem('selectedVoice', voice);
        
        // Show notification
        this.showNotification(`Voice changed to: ${this.getVoiceName(voice)}`);
    }

    // Change speed selection
    changeSpeed(speed) {
        const speedValue = parseFloat(speed);
        this.currentSpeed = speedValue;
        localStorage.setItem('selectedSpeed', speedValue.toString());
        
        // Update display
        this.updateSpeedDisplay(speedValue);
        
        // Show notification
        this.showNotification(`Speed changed to: ${speedValue}×`);
    }

    // Update speed display
    updateSpeedDisplay(speed) {
        if (this.speedDisplay) {
            if (speed === 1.0) {
                this.speedDisplay.textContent = '1.0× Normal';
            } else {
                this.speedDisplay.textContent = `${speed}×`;
            }
        }
    }

    // Change volume setting
    changeVolume(volume) {
        this.currentVolume = parseFloat(volume);
        localStorage.setItem('selectedVolume', this.currentVolume.toString());
        this.updateVolumeDisplay(this.currentVolume);
        
        // Show notification
        this.showNotification(`Volume changed to: ${Math.round(this.currentVolume * 100)}%`);
    }

    // Update volume display
    updateVolumeDisplay(volume) {
        const volumeDisplay = document.getElementById('volume-display');
        if (volumeDisplay) {
            const percentage = Math.round(parseFloat(volume) * 100);
            volumeDisplay.textContent = `${percentage}%`;
        }
    }

    // Get current volume setting
    getCurrentVolume() {
        return this.currentVolume || DEFAULT_VOLUME;
    }

    // Get friendly engine name
    getEngineName(engine) {
        const engineNames = {
            'edge': 'Microsoft Edge TTS',
            'hailuo': 'MiniMax Hailuo TTS',
            'minimax': 'MiniMax Hailuo TTS'
        };
        return engineNames[engine] || engine;
    }

    // Get friendly voice name
    getVoiceName(voice) {
        // Try to find voice name from loaded engines info
        for (const engineKey in this.availableEngines) {
            const engine = this.availableEngines[engineKey];
            const voiceObj = engine.voices?.find(v => v.id === voice);
            if (voiceObj) {
                return voiceObj.name;
            }
        }
        
        // Fallback to hardcoded names
        const voiceNames = {
            'zh-CN-XiaoxiaoNeural': 'Microsoft Xiaoxiao (Female)',
            'zh-CN-XiaoyiNeural': 'Microsoft Xiaoyi (Female)',
            'zh-CN-YunjianNeural': 'Microsoft Yunjian (Male)',
            'zh-CN-YunxiNeural': 'Microsoft Yunxi (Male)',
            'zh-CN-YunxiaNeural': 'Microsoft Yunxia (Female)',
            'zh-CN-YunyangNeural': 'Microsoft Yunyang (Male)',
            'zh-CN-liaoning-XiaobeiNeural': 'Microsoft Xiaobei (Female - Northeastern)',
            'zh-CN-shaanxi-XiaoniNeural': 'Microsoft Xiaoni (Female - Shaanxi)'
        };
        return voiceNames[voice] || voice;
    }

    // Show notification with enhanced progress support
    showNotification(message, type = 'info', duration = 3000, persistent = false) {
        // Create temporary notification
        const notification = document.createElement('div');
        notification.textContent = message;
        
        let bgColor = 'bg-blue-500';
        let icon = '💙';
        if (type === 'success') {
            bgColor = 'bg-green-500';
            icon = '🟢';
        } else if (type === 'error') {
            bgColor = 'bg-red-500';
            icon = '🔴';
        } else if (type === 'warning') {
            bgColor = 'bg-yellow-500';
            icon = '⚠️';
        } else if (type === 'progress') {
            bgColor = 'bg-blue-500';
            icon = '🔵';
        }
        
        // Enhanced styling for better visibility
        notification.className = `fixed top-4 right-4 ${bgColor} text-white px-4 py-3 rounded-md shadow-lg z-[1000] transition-all duration-300 max-w-xs`;
        notification.innerHTML = `${icon} ${message}`;
        
        // Add data attribute for progress notifications
        if (type === 'progress') {
            notification.setAttribute('data-progress', 'true');
        }
        
        document.body.appendChild(notification);
        
        // Handle persistent notifications (for progress)
        if (!persistent) {
            setTimeout(() => {
                notification.style.opacity = '0';
                notification.style.transform = 'translateX(100%)';
                setTimeout(() => {
                    if (document.body.contains(notification)) {
                        document.body.removeChild(notification);
                    }
                }, 300);
            }, duration);
        }
        
        return notification; // Return reference for progress updates
    }
    
    // Show chunk progress notification
    showChunkProgress(current, total, message = '') {
        // Remove any existing progress notifications
        const existingProgress = document.querySelectorAll('[data-progress="true"]');
        existingProgress.forEach(notification => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        });
        
        const progressMessage = message || `Processing chunk ${current}/${total}`;
        const percentage = Math.round((current / total) * 100);
        const fullMessage = `${progressMessage} (${percentage}%)`;
        
        return this.showNotification(fullMessage, 'progress', 5000, true);
    }
    
    // Clear all progress notifications
    clearProgressNotifications() {
        const progressNotifications = document.querySelectorAll('[data-progress="true"]');
        progressNotifications.forEach(notification => {
            if (document.body.contains(notification)) {
                notification.style.opacity = '0';
                notification.style.transform = 'translateX(100%)';
                setTimeout(() => {
                    if (document.body.contains(notification)) {
                        document.body.removeChild(notification);
                    }
                }, 300);
            }
        });
    }

    // Get current engine for TTS generation
    getCurrentEngine() {
        return this.currentEngine;
    }

    // Get current voice for TTS generation
    getCurrentVoice() {
        return this.currentVoice;
    }

    // Get current speed for TTS generation
    getCurrentSpeed() {
        return this.currentSpeed.toString();
    }

    // Update credentials UI elements
    updateCredentialsUI() {
        if (!this.credentialsStatus.hailuo) return;
        
        const hailuoStatus = this.credentialsStatus.hailuo;
        
        // Update status display
        if (this.minimaxStatus) {
            if (hailuoStatus.configured) {
                this.minimaxStatus.innerHTML = '<span class="text-green-600 font-medium">✅ Configured</span>';
            } else {
                this.minimaxStatus.innerHTML = '<span class="text-gray-500">❌ Not configured</span>';
            }
        }
        
        // Don't pre-fill credentials for security
        if (this.minimaxApiKey) {
            this.minimaxApiKey.value = '';
            this.minimaxApiKey.placeholder = hailuoStatus.configured ? 
                'API Key is configured' : 'Enter your MiniMax API Key';
        }
        
        if (this.minimaxGroupId) {
            this.minimaxGroupId.value = '';
            this.minimaxGroupId.placeholder = hailuoStatus.configured ? 
                'Group ID is configured' : 'Enter your MiniMax Group ID';
        }
        
        // Update model and custom voice (these can be pre-filled)
        if (this.minimaxModel && this.credentialsStatus.hailuo) {
            const currentModel = this.credentialsStatus.hailuo.model || 'speech-02-turbo';
            this.minimaxModel.value = currentModel;
        }
        
        if (this.minimaxCustomVoice && this.credentialsStatus.hailuo) {
            const customVoice = this.credentialsStatus.hailuo.custom_voice_id || '';
            this.minimaxCustomVoice.value = customVoice;
            if (customVoice) {
                this.minimaxCustomVoice.placeholder = 'Custom voice configured';
            }
        }
        
        // Update chunk size setting
        if (this.minimaxChunkSize && this.credentialsStatus.hailuo) {
            const chunkSize = this.credentialsStatus.hailuo.chunk_size || 120;
            this.minimaxChunkSize.value = chunkSize;
            updateChunkSizeDisplay(chunkSize);  // Update display
        }
        
        // Update save button state based on configuration status
        this.validateMinimaxCredentials();
    }

    // Validate MiniMax credentials (real-time)
    async validateMinimaxCredentials() {
        if (!this.minimaxApiKey || !this.minimaxGroupId) return;
        
        const apiKey = this.minimaxApiKey.value.trim();
        const groupId = this.minimaxGroupId.value.trim();
        const customVoice = this.minimaxCustomVoice ? this.minimaxCustomVoice.value.trim() : '';
        
        // Basic client-side validation
        let isValid = true;
        let errorMessage = '';
        
        // Check if API key is valid (either actual key or dots indicating saved key)
        if (apiKey && apiKey.length < 10 && !apiKey.startsWith('••••••••••')) {
            isValid = false;
            errorMessage = 'API Key appears too short';
        }
        
        if (groupId && groupId.length < 5) {
            isValid = false;
            errorMessage = 'Group ID appears too short';
        }
        
        // Validate custom voice ID format if provided
        if (customVoice && !this._validateVoiceIdFormat(customVoice)) {
            isValid = false;
            errorMessage = 'Custom Voice ID format appears invalid';
        }
        
        // Update visual feedback
        const saveBtn = document.getElementById('save-credentials-btn');
        if (saveBtn) {
            // Check if credentials are already configured
            const isAlreadyConfigured = this.credentialsStatus?.hailuo?.configured || false;
            // Enable if we have valid API key (either dots or actual key) and group ID, OR if already configured
            const hasValidApiKey = apiKey && (apiKey.startsWith('••••••••••') || apiKey.length >= 10);
            if ((hasValidApiKey && groupId && isValid) || isAlreadyConfigured) {
                saveBtn.disabled = false;
                saveBtn.classList.remove('opacity-50');
            } else {
                saveBtn.disabled = true;
                saveBtn.classList.add('opacity-50');
            }
        }
        
        // Update status if there's an error
        if (!isValid && errorMessage && this.minimaxStatus) {
            this.minimaxStatus.innerHTML = `<span class="text-red-500 text-sm">${errorMessage}</span>`;
        }
    }

    // Validate voice ID format (client-side)
    _validateVoiceIdFormat(voiceId) {
        if (!voiceId) return true; // Empty is valid
        
        // Check length and characters
        if (voiceId.length < 3 || voiceId.length > 100) return false;
        
        // Allow alphanumeric, hyphens, underscores
        const pattern = /^[a-zA-Z0-9_-]+$/;
        return pattern.test(voiceId);
    }

    // Save MiniMax credentials
    async saveMinimaxCredentials() {
        if (!this.minimaxApiKey || !this.minimaxGroupId) return;
        
        const apiKey = this.minimaxApiKey.value.trim();
        const groupId = this.minimaxGroupId.value.trim();
        const customVoice = this.minimaxCustomVoice ? this.minimaxCustomVoice.value.trim() : '';
        const model = this.minimaxModel ? this.minimaxModel.value : 'speech-02-turbo';
        
        if (!apiKey || !groupId) {
            this.showNotification('Please enter both API Key and Group ID', 'error');
            return;
        }
        
        try {
            // Show loading state
            const saveBtn = document.getElementById('save-credentials-btn');
            const originalText = saveBtn.textContent;
            saveBtn.textContent = 'Saving...';
            saveBtn.disabled = true;
            
            const response = await fetch('/save-credentials', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    engine: 'hailuo',
                    credentials: {
                        api_key: apiKey,
                        group_id: groupId,
                        custom_voice_id: customVoice,
                        model: model,
                        chunk_size: parseInt(this.minimaxChunkSize ? this.minimaxChunkSize.value : 120)
                    }
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                let message = 'Settings saved successfully!';
                if (customVoice) {
                    message += ` Custom voice configured: ${customVoice.substring(0, 20)}...`;
                }
                this.showNotification(message, 'success');
                
                // Reload credentials status and engine info
                await this.loadCredentialsStatus();
                await this.loadEnginesInfo();
                
                // Clear credentials for security, but keep model and custom voice
                this.minimaxApiKey.value = '';
                this.minimaxGroupId.value = '';
                
                // Update voices for current engine if Hailuo is selected
                if (this.currentEngine === 'hailuo') {
                    this.updateVoicesForEngine('hailuo');
                }
            } else {
                this.showNotification(`Error: ${data.error}`, 'error');
            }
            
            // Restore button
            saveBtn.textContent = originalText;
            saveBtn.disabled = false;
            
        } catch (error) {
            console.error('Error saving settings:', error);
            this.showNotification('Failed to save settings', 'error');
        }
    }

    // Clear MiniMax credentials
    async clearMinimaxCredentials() {
        if (!confirm('Are you sure you want to clear MiniMax credentials?')) {
            return;
        }
        
        try {
            const response = await fetch('/save-credentials', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    engine: 'hailuo',
                    credentials: {
                        api_key: '',
                        group_id: '',
                        chunk_size: 120
                    }
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Credentials cleared successfully', 'success');
                // Reload status
                await this.loadCredentialsStatus();
                // Clear form
                if (this.minimaxApiKey) this.minimaxApiKey.value = '';
                if (this.minimaxGroupId) this.minimaxGroupId.value = '';
                if (this.minimaxCustomVoice) this.minimaxCustomVoice.value = '';
                if (this.minimaxModel) this.minimaxModel.value = 'speech-02-turbo';
            } else {
                this.showNotification(`Error: ${data.error}`, 'error');
            }
            
        } catch (error) {
            console.error('Error clearing credentials:', error);
            this.showNotification('Failed to clear credentials', 'error');
        }
    }
}

// Global instance
window.settingsManager = new SettingsManager();

// ========================================
// Tab Switching Functionality
// ========================================

function switchSettingsTab(tabName) {
    // Remove active class from all tabs and content
    document.querySelectorAll('.settings-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
        content.style.display = 'none';
    });
    
    // Add active class to clicked tab
    const activeTab = document.querySelector(`[data-tab="${tabName}"]`);
    if (activeTab) {
        activeTab.classList.add('active');
    }
    
    // Show corresponding content
    const activeContent = document.querySelector(`[data-tab-content="${tabName}"]`);
    if (activeContent) {
        activeContent.style.display = 'block';
        activeContent.classList.add('active');
    }
    
    // Store active tab in localStorage for persistence
    localStorage.setItem('activeSettingsTab', tabName);
    
    // Trigger validation if switching to API tab
    if (tabName === 'api') {
        // Slight delay to allow DOM to settle
        setTimeout(() => {
            if (window.settingsManager) {
                window.settingsManager.validateMinimaxCredentials();
            }
        }, 100);
    }
}

// Initialize tab state when settings modal opens
function initializeSettingsTabs() {
    // Get saved tab preference or default to 'voice'
    const activeTab = localStorage.getItem('activeSettingsTab') || 'voice';
    switchSettingsTab(activeTab);
}

// Keyboard navigation for tabs
function handleTabKeyboard(event) {
    if (!document.getElementById('settings-modal').classList.contains('hidden')) {
        const tabs = Array.from(document.querySelectorAll('.settings-tab'));
        const currentTab = document.querySelector('.settings-tab.active');
        const currentIndex = tabs.indexOf(currentTab);
        
        let nextIndex = -1;
        
        // Left arrow or up arrow = previous tab
        if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') {
            event.preventDefault();
            nextIndex = currentIndex > 0 ? currentIndex - 1 : tabs.length - 1;
        }
        // Right arrow or down arrow = next tab  
        else if (event.key === 'ArrowRight' || event.key === 'ArrowDown') {
            event.preventDefault();
            nextIndex = currentIndex < tabs.length - 1 ? currentIndex + 1 : 0;
        }
        // Number keys for direct tab access
        else if (event.key >= '1' && event.key <= '9') {
            const tabIndex = parseInt(event.key) - 1;
            if (tabIndex < tabs.length) {
                event.preventDefault();
                nextIndex = tabIndex;
            }
        }
        
        if (nextIndex !== -1 && tabs[nextIndex]) {
            const tabName = tabs[nextIndex].getAttribute('data-tab');
            switchSettingsTab(tabName);
            tabs[nextIndex].focus();
        }
    }
}

// Global functions for HTML onclick handlers
function openSettingsPopup() {
    window.settingsManager.openSettingsPopup();
}

// Make sure switchSettingsTab is globally available
window.switchSettingsTab = switchSettingsTab;

function closeSettingsPopup(event) {
    window.settingsManager.closeSettingsPopup(event);
}

function changeVoice(voice) {
    window.settingsManager.changeVoice(voice);
}

function changeTTSEngine(engine) {
    window.settingsManager.changeTTSEngine(engine);
}

function changeSpeed(speed) {
    window.settingsManager.changeSpeed(speed);
}

function validateMinimaxCredentials() {
    window.settingsManager.validateMinimaxCredentials();
}

function saveMinimaxCredentials() {
    window.settingsManager.saveMinimaxCredentials();
}

function clearMinimaxCredentials() {
    window.settingsManager.clearMinimaxCredentials();
}

// Global functions for chunk size management
function updateChunkSizeDisplay(chunkSize) {
    const display = document.getElementById('chunk-size-display');
    const estimate = document.getElementById('chunk-estimate');
    
    if (display) {
        const estimatedChars = Math.round(chunkSize * 1.7); // 1.7 chars per word average
        display.textContent = `${chunkSize} words (~${estimatedChars} chars)`;
    }
    
    if (estimate) {
        // Estimate chunks based on typical text length (500 words)
        const typicalTextWords = 500;
        const estimatedChunks = Math.ceil(typicalTextWords / chunkSize);
        estimate.textContent = estimatedChunks;
        
        // Color coding based on API usage risk
        if (estimatedChunks <= 5) {
            estimate.className = 'font-medium text-green-600';
        } else if (estimatedChunks <= 15) {
            estimate.className = 'font-medium text-orange-600';
        } else {
            estimate.className = 'font-medium text-red-600';
        }
    }
}

// Global functions for volume management
function updateVolumeDisplay(volume) {
    window.settingsManager.updateVolumeDisplay(volume);
    window.settingsManager.changeVolume(volume);
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.settingsManager.initialize();
    
    // Initialize chunk size display
    const chunkSlider = document.getElementById('minimax-chunk-size');
    if (chunkSlider) {
        updateChunkSizeDisplay(chunkSlider.value);
    }
});

// Handle ESC key to close settings and tab navigation
document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
        window.settingsManager.closeSettingsPopup();
    } else {
        // Handle tab navigation when settings modal is open
        handleTabKeyboard(event);
    }
});