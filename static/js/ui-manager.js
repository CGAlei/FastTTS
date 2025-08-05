// Sidebar state management
let leftSidebarCollapsed = false;
let rightSidebarCollapsed = false;

// Scroll behavior variables
let isScrolling = false;
let scrollTimeout = null;

// Auto-hide configuration
const AUTO_HIDE_CONFIG = {
    topTriggerDistance: 120,      // Distance from top to show controls
    bottomTriggerDistance: 150,   // Distance from bottom to show input
    bottomHideDistance: 200,      // Distance from bottom to hide input
    scrollHideThreshold: 100,     // Scroll position to trigger hide
    bottomScrollOffset: 200,      // Offset from bottom for scroll behavior
    hideDelay: 200               // Delay before hiding after scroll stops
};

// Initialize sidebar states from localStorage
function initializeSidebarStates() {
    try {
        const savedLeftState = localStorage.getItem('leftSidebarCollapsed');
        const savedRightState = localStorage.getItem('rightSidebarCollapsed');
        
        if (savedLeftState === 'true') {
            toggleLeftSidebar(false); // Don't save to localStorage again
        }
        if (savedRightState === 'true') {
            toggleRightSidebar(false); // Don't save to localStorage again
        }
    } catch (error) {
        console.warn('Could not access localStorage for sidebar states:', error);
    }
}

// Sidebar toggle functions
function toggleLeftSidebar(saveState = true) {
    const container = document.querySelector('.app-container');
    const sidebar = document.getElementById('left-sidebar');
    
    if (!sidebar) {
        console.warn('Left sidebar not found!');
        return;
    }
    
    leftSidebarCollapsed = !leftSidebarCollapsed;
    console.log('Left sidebar collapsed state:', leftSidebarCollapsed);
    
    if (leftSidebarCollapsed) {
        sidebar.classList.add('collapsed');
    } else {
        sidebar.classList.remove('collapsed');
    }
    
    updateContainerGrid();
    
    if (saveState) {
        try {
            localStorage.setItem('leftSidebarCollapsed', leftSidebarCollapsed);
        } catch (error) {
            console.warn('Could not save left sidebar state to localStorage:', error);
        }
    }
}

function toggleRightSidebar(saveState = true) {
    const container = document.querySelector('.app-container');
    const sidebar = document.getElementById('right-sidebar');
    
    if (!sidebar) {
        console.warn('Right sidebar not found!');
        return;
    }
    
    rightSidebarCollapsed = !rightSidebarCollapsed;
    console.log('Right sidebar collapsed state:', rightSidebarCollapsed);
    
    if (rightSidebarCollapsed) {
        sidebar.classList.add('collapsed');
    } else {
        sidebar.classList.remove('collapsed');
    }
    
    updateContainerGrid();
    
    if (saveState) {
        try {
            localStorage.setItem('rightSidebarCollapsed', rightSidebarCollapsed);
        } catch (error) {
            console.warn('Could not save right sidebar state to localStorage:', error);
        }
    }
}

function toggleBothSidebars(saveState = true) {
    // Check current state - if either is visible, hide both
    // If both are hidden, show both
    const shouldShowBoth = leftSidebarCollapsed && rightSidebarCollapsed;
    
    if (shouldShowBoth) {
        // Show both sidebars
        if (leftSidebarCollapsed) toggleLeftSidebar(saveState);
        if (rightSidebarCollapsed) toggleRightSidebar(saveState);
    } else {
        // Hide both sidebars
        if (!leftSidebarCollapsed) toggleLeftSidebar(saveState);
        if (!rightSidebarCollapsed) toggleRightSidebar(saveState);
    }
}

function updateContainerGrid() {
    const container = document.querySelector('.app-container');
    const controls = document.querySelector('.accessibility-controls');
    
    if (!container) {
        console.warn('App container not found!');
        return;
    }
    
    // Remove all collapse classes
    container.classList.remove('left-collapsed', 'right-collapsed', 'both-collapsed');
    if (controls) {
        controls.classList.remove('left-collapsed', 'right-collapsed', 'both-collapsed');
    }
    
    // Add appropriate class based on state
    if (leftSidebarCollapsed && rightSidebarCollapsed) {
        container.classList.add('both-collapsed');
        if (controls) controls.classList.add('both-collapsed');
        console.log('Applied both-collapsed class');
    } else if (leftSidebarCollapsed) {
        container.classList.add('left-collapsed');
        if (controls) controls.classList.add('left-collapsed');
        console.log('Applied left-collapsed class');
    } else if (rightSidebarCollapsed) {
        container.classList.add('right-collapsed');
        if (controls) controls.classList.add('right-collapsed');
        console.log('Applied right-collapsed class');
    } else {
        console.log('No collapse classes applied - both sidebars visible');
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Don't trigger shortcuts when user is typing in inputs
    if (event.target.tagName === 'INPUT' || 
        event.target.tagName === 'TEXTAREA' || 
        event.target.contentEditable === 'true' ||
        event.target.isContentEditable) {
        return;
    }
    
    // Ctrl+1 for left sidebar
    if (event.ctrlKey && event.key === '1') {
        event.preventDefault();
        toggleLeftSidebar();
    }
    // Ctrl+2 for right sidebar
    if (event.ctrlKey && event.key === '2') {
        event.preventDefault();
        toggleRightSidebar();
    }
    
    // New hotkeys without modifiers
    if (!event.ctrlKey && !event.altKey && !event.metaKey) {
        switch(event.key.toLowerCase()) {
            case 'a':
                event.preventDefault();
                toggleLeftSidebar();
                break;
            case 's':
                event.preventDefault();
                toggleBothSidebars();
                break;
            case 'd':
                event.preventDefault();
                toggleRightSidebar();
                break;
        }
    }
});

// Mouse proximity-based auto-hide behavior (no scroll triggers)
function initializeMouseProximityBehavior() {
    const controls = document.querySelector('.accessibility-controls');
    const inputArea = document.querySelector('.input-area');
    const mainContent = document.querySelector('.main-content');
    
    // Ensure required elements exist
    if (!inputArea || !mainContent || !controls) {
        return;
    }
    
    // Set up scroll tracking for isScrolling flag only (no auto-hide triggers)
    if (mainContent) {
        mainContent.addEventListener('scroll', function() {
            isScrolling = true;
            
            // Clear existing timeout
            if (scrollTimeout) {
                clearTimeout(scrollTimeout);
            }
            
            // Reset scrolling flag after scroll stops (for other features that need it)
            scrollTimeout = setTimeout(() => {
                isScrolling = false;
            }, AUTO_HIDE_CONFIG.hideDelay);
        });
    }
    
    // Optimized mouse movement detection with throttling (ONLY mouse proximity triggers)
    let mouseTimeout;
    let rafId;
    
    document.addEventListener('mousemove', function(e) {
        if (mouseTimeout) return;
        
        // Use requestAnimationFrame for better performance
        if (rafId) {
            cancelAnimationFrame(rafId);
        }
        
        rafId = requestAnimationFrame(() => {
            // Show top controls when mouse near top
            if (e.clientY < AUTO_HIDE_CONFIG.topTriggerDistance) {
                controls.classList.remove('auto-hide');
            }
            
            // Show/hide input panel based on mouse position near bottom
            if (e.clientY > window.innerHeight - AUTO_HIDE_CONFIG.bottomTriggerDistance) {
                inputArea.classList.remove('auto-hide');
            } else if (e.clientY < window.innerHeight - AUTO_HIDE_CONFIG.bottomHideDistance) {
                // Hide input panel when mouse is away from bottom area
                // But only if user is not actively interacting with it
                const activeElement = document.activeElement;
                const isInputFocused = activeElement && 
                    (activeElement.id === 'custom-text' || inputArea.contains(activeElement));
                
                if (!isInputFocused && !isScrolling) {
                    inputArea.classList.add('auto-hide');
                }
            }
            
            mouseTimeout = setTimeout(() => {
                mouseTimeout = null;
            }, 16); // Throttle to ~60fps
        });
    });
    
    // Accessibility: Show input panel on focus and keep visible during interaction
    const textarea = document.getElementById('custom-text');
    const inputButtons = inputArea.querySelectorAll('button');
    
    if (textarea) {
        // Show panel when textarea receives focus
        textarea.addEventListener('focus', function() {
            inputArea.classList.remove('auto-hide');
        });
        
        // Keep panel visible while typing
        textarea.addEventListener('input', function() {
            inputArea.classList.remove('auto-hide');
        });
    }
    
    // Show panel when any button in the input area receives focus
    inputButtons.forEach(button => {
        button.addEventListener('focus', function() {
            inputArea.classList.remove('auto-hide');
        });
    });
    
    // Show panel when clicking anywhere in the input area
    inputArea.addEventListener('click', function() {
        inputArea.classList.remove('auto-hide');
    });
}


function adjustFontSize(value) {
    const textDisplay = document.getElementById('text-display');
    if (textDisplay) {
        // Remove all font size classes
        textDisplay.classList.remove('font-size-small', 'font-size-medium', 'font-size-large', 'font-size-xlarge');
        
        // Map slider values to font size classes
        const sizeMap = {
            '1': 'font-size-small',
            '2': 'font-size-medium',
            '3': 'font-size-large',
            '4': 'font-size-xlarge'
        };
        
        const sizeClass = sizeMap[value] || 'font-size-medium';
        textDisplay.classList.add(sizeClass);
        
        // Update button active states
        document.querySelectorAll('.font-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        const buttonMap = {
            '1': 'font-small',
            '2': 'font-medium',
            '3': 'font-large',
            '4': 'font-xlarge'
        };
        
        const activeBtn = document.getElementById(buttonMap[value]);
        if (activeBtn) {
            activeBtn.classList.add('active');
        }
        
    }
}

// ========================================
//   Folder Management System
// ========================================

// Folder expand/collapse functionality
function toggleFolder(folderName) {
    const folderContent = document.querySelector(`[data-folder="${folderName}"].folder-content`);
    const toggleBtn = document.querySelector(`[data-folder="${folderName}"] .folder-toggle-btn`);
    const folderHeader = document.querySelector(`[data-folder="${folderName}"].folder-header`);
    
    if (!folderContent || !toggleBtn) {
        console.warn(`Folder elements not found for: ${folderName}`);
        return;
    }
    
    // Use CSS class-based state detection instead of style.display
    const isExpanded = folderContent.classList.contains('expanded');
    const newExpandedState = !isExpanded;
    
    // Update UI using only CSS classes (no inline styles)
    if (newExpandedState) {
        folderContent.classList.remove('collapsed');
        folderContent.classList.add('expanded');
        toggleBtn.innerHTML = '▼';
        if (folderHeader) folderHeader.classList.add('active');
    } else {
        folderContent.classList.remove('expanded');
        folderContent.classList.add('collapsed');
        toggleBtn.innerHTML = '▶';
        if (folderHeader) folderHeader.classList.remove('active');
    }
    
    // Save state to server
    saveFolderExpandedState(folderName, newExpandedState);
}

// Save folder expanded state to server
function saveFolderExpandedState(folderName, expanded) {
    fetch('/api/folder/toggle', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            folder_name: folderName,
            expanded: expanded
        })
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            console.error('Failed to save folder state:', data.error);
        }
    })
    .catch(error => {
        console.error('Error saving folder state:', error);
    });
}


// Move session to folder functionality
function moveSessionToFolder(sessionId, targetFolder) {
    fetch('/api/session/move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: sessionId,
            target_folder: targetFolder
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            refreshSessionList();
            showNotification(`Session moved to "${targetFolder}"!`, 'success');
        } else {
            alert(`Failed to move session: ${data.error}`);
        }
    })
    .catch(error => {
        console.error('Error moving session:', error);
        alert('Error moving session. Please try again.');
    });
}

// Refresh session list
function refreshSessionList() {
    // Use HTMX to refresh the sessions list
    const sessionsList = document.getElementById('sessions-list');
    if (sessionsList) {
        htmx.trigger(sessionsList, 'htmx:load');
    }
}

// Show notification (simple implementation)
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 6px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        animation: slideInRight 0.3s ease-out;
    `;
    
    // Set background color based on type
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        info: '#3b82f6',
        warning: '#f59e0b'
    };
    notification.style.backgroundColor = colors[type] || colors.info;
    
    notification.textContent = message;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.3s ease-in';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Initialize folder functionality
function initializeFolderSystem() {
    
    // Initialize folder headers click handlers
    document.addEventListener('click', function(e) {
        const folderHeader = e.target.closest('.folder-header');
        if (folderHeader && !e.target.closest('.folder-toggle-btn')) {
            const folderName = folderHeader.getAttribute('data-folder');
            if (folderName) {
                toggleFolder(folderName);
            }
        }
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeSidebarStates();
    initializeMouseProximityBehavior();
    initializeTheme();
    initializeFolderSystem();
});

