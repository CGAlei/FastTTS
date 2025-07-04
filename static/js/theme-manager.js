// Initialize theme on page load
function initializeTheme() {
    let savedTheme = 'default';
    try {
        savedTheme = localStorage.getItem('themePreference') || 'default';
    } catch (error) {
        console.warn('Could not access localStorage for theme preference:', error);
    }
    changeColorScheme(savedTheme);
}

// Debug function to test theme switching (accessible from console)
window.testThemes = function() {
    setTimeout(() => {
        changeColorScheme('high-contrast');
    }, 1000);
    setTimeout(() => {
        changeColorScheme('dark-mode');
    }, 3000);
    setTimeout(() => {
        changeColorScheme('default');
    }, 5000);
};

function changeColorScheme(scheme) {
    
    // Get all elements that need theme changes
    const html = document.documentElement;
    const body = document.body;
    const appContainer = document.querySelector('.app-container');
    const mainContent = document.querySelector('.main-content');
    const karaokeArea = document.querySelector('.karaoke-area');
    const leftSidebar = document.querySelector('.left-sidebar');
    const rightSidebar = document.querySelector('.right-sidebar');
    const accessibilityControls = document.querySelector('.accessibility-controls');
    const inputArea = document.querySelector('.input-area');
    const textContainer = document.querySelector('#text-container');
    const themeBgSpacer = document.querySelector('.theme-bg-spacer');
    const contentWrapper = document.querySelector('#content-wrapper');
    
    
    if (karaokeArea) {
        const computedStyle = window.getComputedStyle(karaokeArea);
    }
    
    // Remove all theme classes from all elements
    const elementsToTheme = [html, body, appContainer, mainContent, karaokeArea, leftSidebar, rightSidebar, accessibilityControls, inputArea, textContainer, themeBgSpacer, contentWrapper].filter(el => el);
    
    elementsToTheme.forEach(element => {
        element.classList.remove('high-contrast', 'dark-mode');
    });
    
    // Define theme colors
    const themes = {
        'default': {
            bg: '#ffffff',
            sidebarBg: '#f8fafc',
            controlsBg: '#f8fafc'
        },
        'high-contrast': {
            bg: '#000000',
            sidebarBg: '#1a1a1a',
            controlsBg: '#1a1a1a'
        },
        'dark-mode': {
            bg: '#1a1a1a',
            sidebarBg: '#2d2d2d',
            controlsBg: '#2d2d2d'
        }
    };
    
    const currentTheme = themes[scheme] || themes['default'];
    
    // Apply theme classes and inline styles as fallback
    if (scheme !== 'default') {
        elementsToTheme.forEach(element => {
            element.classList.add(scheme);
        });
    }
    
    // Force inline styles for stubborn elements (fallback for !important conflicts)
    if (html) {
        html.style.backgroundColor = currentTheme.bg;
    }
    if (body) {
        body.style.backgroundColor = currentTheme.bg;
    }
    if (appContainer) {
        appContainer.style.backgroundColor = currentTheme.bg;
    }
    if (mainContent) {
        mainContent.style.backgroundColor = currentTheme.bg;
    }
    if (karaokeArea) {
        karaokeArea.style.backgroundColor = currentTheme.bg;
    }
    if (leftSidebar) {
        leftSidebar.style.backgroundColor = currentTheme.sidebarBg;
    }
    if (rightSidebar) {
        rightSidebar.style.backgroundColor = currentTheme.sidebarBg;
    }
    if (accessibilityControls) {
        accessibilityControls.style.backgroundColor = currentTheme.controlsBg;
    }
    if (inputArea) {
        inputArea.style.backgroundColor = currentTheme.sidebarBg;
    }
    if (textContainer) {
        textContainer.style.backgroundColor = currentTheme.bg;
    }
    if (themeBgSpacer) {
        themeBgSpacer.style.backgroundColor = currentTheme.bg;
    }
    if (contentWrapper) {
        contentWrapper.style.backgroundColor = currentTheme.bg;
    }
    
    // Update button active states
    document.querySelectorAll('.theme-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Map scheme names to button IDs
    const schemeToButtonId = {
        'default': 'theme-default',
        'high-contrast': 'theme-contrast',
        'dark-mode': 'theme-dark-mode'
    };
    
    const activeBtn = document.getElementById(schemeToButtonId[scheme] || 'theme-default');
    if (activeBtn) {
        activeBtn.classList.add('active');
    }
    
    if (karaokeArea) {
        const computedStyle = window.getComputedStyle(karaokeArea);
        console.log('  - Karaoke Area Classes:', karaokeArea.className);
    }
    
    // Save theme preference (with error handling)
    try {
        localStorage.setItem('themePreference', scheme);
    } catch (error) {
        console.warn('Could not save theme preference to localStorage:', error);
    }
    
}