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
    const toggle = document.getElementById('left-toggle');
    
    leftSidebarCollapsed = !leftSidebarCollapsed;
    
    if (leftSidebarCollapsed) {
        sidebar.classList.add('collapsed');
        toggle.classList.add('collapsed');
        toggle.innerHTML = '⟩';
        toggle.title = 'Expand Sessions Panel';
        toggle.setAttribute('aria-label', 'Expand sessions panel');
    } else {
        sidebar.classList.remove('collapsed');
        toggle.classList.remove('collapsed');
        toggle.innerHTML = '⟨';
        toggle.title = 'Collapse Sessions Panel';
        toggle.setAttribute('aria-label', 'Collapse sessions panel');
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
    const toggle = document.getElementById('right-toggle');
    
    rightSidebarCollapsed = !rightSidebarCollapsed;
    
    if (rightSidebarCollapsed) {
        sidebar.classList.add('collapsed');
        toggle.classList.add('collapsed');
        toggle.innerHTML = '⟩';
        toggle.title = 'Expand Dictionary Panel';
        toggle.setAttribute('aria-label', 'Expand dictionary panel');
    } else {
        sidebar.classList.remove('collapsed');
        toggle.classList.remove('collapsed');
        toggle.innerHTML = '⟨';
        toggle.title = 'Collapse Dictionary Panel';
        toggle.setAttribute('aria-label', 'Collapse dictionary panel');
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
    
    // Remove all collapse classes
    container.classList.remove('left-collapsed', 'right-collapsed', 'both-collapsed');
    controls.classList.remove('left-collapsed', 'right-collapsed', 'both-collapsed');
    
    // Add appropriate class based on state
    if (leftSidebarCollapsed && rightSidebarCollapsed) {
        container.classList.add('both-collapsed');
        controls.classList.add('both-collapsed');
    } else if (leftSidebarCollapsed) {
        container.classList.add('left-collapsed');
        controls.classList.add('left-collapsed');
    } else if (rightSidebarCollapsed) {
        container.classList.add('right-collapsed');
        controls.classList.add('right-collapsed');
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

// Mobile menu functionality (separate from desktop collapse)
function toggleMobileMenu() {
    const sidebar = document.getElementById('left-sidebar');
    sidebar.classList.toggle('open');
    
    // On mobile, we don't want the collapsed state to interfere
    if (window.innerWidth <= 768) {
        sidebar.classList.remove('collapsed');
    }
    
    // Close menu when clicking outside
    if (sidebar.classList.contains('open')) {
        // Add click listener on next frame to avoid immediate triggering
        requestAnimationFrame(() => {
            document.addEventListener('click', closeMobileMenuOnOutsideClick);
        });
    } else {
        document.removeEventListener('click', closeMobileMenuOnOutsideClick);
    }
}

function closeMobileMenuOnOutsideClick(event) {
    const sidebar = document.getElementById('left-sidebar');
    const menuToggle = document.getElementById('mobile-menu-toggle');
    
    if (!sidebar.contains(event.target) && !menuToggle.contains(event.target)) {
        sidebar.classList.remove('open');
        document.removeEventListener('click', closeMobileMenuOnOutsideClick);
    }
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

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeSidebarStates();
    initializeMouseProximityBehavior();
    initializeTheme();
});

