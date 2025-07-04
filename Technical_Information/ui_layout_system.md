# FastTTS UI Layout System - Three-Panel Architecture

## 📐 Layout Overview

FastTTS implements a sophisticated three-panel layout system optimized for Chinese language learning. The interface consists of fixed-width sidebars with a dynamic center panel, providing dedicated spaces for session management, content interaction, and vocabulary learning.

## 🏗️ Three-Panel Architecture

### **Layout Structure**
```css
.app-container {
    display: grid;
    grid-template-columns: 300px 1fr 300px;
    height: 100vh;
    overflow: hidden;
}
```

### **Panel Dimensions**
- **Left Sidebar**: Fixed 300px width
- **Center Panel**: Dynamic width (calculated as `100vw - 600px` when both sidebars visible)
- **Right Sidebar**: Fixed 300px width
- **Total Minimum Width**: 900px for full three-panel display

## 🎛️ Left Sidebar - Session Management Panel

### **Primary Functions**
- Session list display and navigation
- Advanced filtering and search capabilities
- New session creation controls
- Favorites management system

### **Component Structure**
```html
<aside class="left-sidebar">
  <div class="left-sidebar-header">
    <!-- New Session Button -->
    <!-- Filter Controls -->
  </div>
  <div class="left-sidebar-content">
    <!-- Session List Items -->
  </div>
</aside>
```

### **Key Components**

#### **New Session Button**
- **Location**: `main.css:107-135`
- **Styling**: Blue gradient with hover effects and shadow transitions
- **Behavior**: Creates new learning session and focuses input area
- **Accessibility**: Full keyboard navigation and screen reader support

```css
.new-session-btn {
    width: 100%;
    padding: var(--space-3) var(--space-4);
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    border-radius: var(--space-2);
    transition: all var(--transition-base);
}
```

#### **Filter Controls**
- **Compact Row Design**: Search input + filter toggles + clear button in unified container
- **Real-time Search**: Debounced text matching across session content
- **Filter Buttons**: Favorites toggle with active state indicators
- **Clear Function**: One-click filter reset with visual feedback

```css
.filter-controls-row {
    display: flex;
    border-radius: 6px;
    overflow: hidden;
    border: 1px solid var(--color-border);
    height: 32px;
}
```

#### **Session Items**
- **Interactive Cards**: Hover effects with subtle transformations
- **Active State**: Golden highlighting for currently loaded session
- **Favorite Indicators**: Star-based system with color-coded states
- **Custom Naming**: Inline editing with save/cancel controls

```css
.session-item {
    padding: var(--space-3) var(--space-4);
    cursor: pointer;
    transition: all var(--transition-base);
    display: flex;
    align-items: center;
    gap: var(--space-3);
}

.session-item.active {
    background-color: rgba(251, 191, 36, 0.15);
    border-left: 4px solid #d97706;
    box-shadow: 0 2px 8px rgba(251, 191, 36, 0.2);
}
```

### **Responsive Behavior**
- **Tablet (1024px)**: Left sidebar remains visible, right sidebar collapses
- **Mobile (768px)**: Left sidebar becomes overlay with hamburger menu
- **Auto-hide Logic**: Sidebar collapses when insufficient screen space

## 🎪 Center Panel - Primary Content Area

### **Layout Components**
- **Karaoke Area**: Main text display with synchronized highlighting
- **Input Area**: Floating ChatGPT-style text input with controls
- **Accessibility Controls**: Top-mounted control bar with theme and settings
- **Audio Controls**: Integrated playback controls and progress indicators

### **Dynamic Positioning**
The center panel adjusts its dimensions based on sidebar states:

```css
.main-content {
    position: absolute;
    left: 300px;    /* Adjusts when left sidebar collapsed */
    right: 300px;   /* Adjusts when right sidebar collapsed */
    top: 0;
    bottom: 0;
}
```

### **Karaoke Area**
- **Location**: Core content display region
- **Padding**: Accommodates floating controls (top: 3.5rem, bottom: 120px)
- **Scrolling**: Smooth auto-scroll following audio playback
- **Text Layout**: Word containers with precise spacing for highlighting

```css
.karaoke-area {
    flex: 1;
    padding: 0.5rem;
    padding-top: 3.5rem;
    padding-bottom: 120px;
    background-color: white;
    min-height: calc(100vh - 120px);
}
```

### **Input Area - Floating Design**
- **Position**: Fixed at bottom center with responsive margins
- **Style**: ChatGPT-inspired floating card with shadow and border radius
- **Auto-hide**: Disappears when not in use, appears on hover/focus
- **Responsive**: Adjusts width based on available space

```css
.input-area {
    position: fixed;
    bottom: 1.5rem;
    left: 320px;
    right: 320px;
    max-width: 800px;
    border-radius: 12px;
    background-color: white;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
    z-index: 300;
}
```

### **Accessibility Controls**
- **Position**: Fixed top bar spanning center panel width
- **Contents**: Theme selector, settings button, sidebar toggles
- **Auto-hide**: Slides up when not needed, appears on interaction
- **Responsive**: Adjusts positioning when sidebars collapse

```css
.accessibility-controls {
    position: fixed;
    top: 0.5rem;
    left: 320px;
    right: 320px;
    background: #f8fafc;
    border-radius: 4px;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
```

## 📚 Right Sidebar - Vocabulary Learning Panel

### **Primary Functions**
- Vocabulary card display with definitions and examples
- AI-generated word explanations and usage context
- Dictionary integration with translation services
- Learning progress indicators and word status tracking

### **Component Structure**
```html
<aside class="right-sidebar">
  <div class="vocabulary-section">
    <!-- Vocabulary Cards -->
    <!-- Definition Display -->
    <!-- Learning Progress -->
  </div>
</aside>
```

### **Vocabulary Cards**
- **Card Design**: Material Design-inspired cards with subtle shadows
- **Content Layout**: Chinese word, pinyin, definition, examples
- **Interactive Elements**: Click to hear pronunciation, mark as learned
- **Status Indicators**: Visual badges for learning progress

### **Dynamic Content**
- **Real-time Updates**: Cards appear as words are encountered during session
- **AI Integration**: Definitions generated on-demand through LLM services
- **Persistence**: Card state saved across sessions for learning continuity

## 🎨 Visual Design System

### **Color Palette**
```css
:root {
    --color-text-primary: #1f2937;    /* Main text color */
    --color-text-secondary: #6b7280;  /* Secondary text */
    --color-text-tertiary: #9ca3af;   /* Muted text */
    --color-border: #e5e7eb;          /* Standard borders */
    --color-bg-subtle: #f8fafc;       /* Sidebar backgrounds */
    --color-bg-hover: #f1f5f9;        /* Hover states */
}
```

### **Spacing System**
Consistent 4px-based spacing scale:
```css
--space-1: 0.25rem;  /* 4px */
--space-2: 0.5rem;   /* 8px */
--space-3: 0.75rem;  /* 12px */
--space-4: 1rem;     /* 16px */
--space-6: 1.5rem;   /* 24px */
--space-8: 2rem;     /* 32px */
```

### **Typography Scale**
```css
--text-xs: 0.75rem;    /* 12px - Small labels */
--text-sm: 0.875rem;   /* 14px - Interface text */
--text-base: 1rem;     /* 16px - Body text */
--text-lg: 1.125rem;   /* 18px - Headings */
```

### **Transition Standards**
```css
--transition-fast: 0.15s ease;   /* Quick interactions */
--transition-base: 0.2s ease;    /* Standard animations */
--transition-slow: 0.3s ease;    /* Panel movements */
```

## 📱 Responsive Behavior

### **Desktop (>1024px)**
- **Full Three-Panel Layout**: All panels visible with standard dimensions
- **Optimal Learning Experience**: Maximum screen real estate utilization
- **Hover Effects**: Rich interactive feedback for mouse interactions

### **Tablet (768px - 1024px)**
- **Two-Panel Layout**: Left sidebar + center panel (right sidebar hidden)
- **Touch Optimization**: Larger touch targets and gesture support
- **Vocabulary Access**: Right panel accessible via overlay or modal

### **Mobile (<768px)**
- **Single Panel**: Center panel only with hamburger menu for navigation
- **Mobile-First Interactions**: Touch-optimized controls and spacing
- **Progressive Enhancement**: Core functionality preserved on small screens

### **Responsive Layout Classes**
```css
@media (max-width: 1024px) {
    .right-sidebar { display: none; }
    .main-content { right: 0px; }
}

@media (max-width: 768px) {
    .left-sidebar { left: -300px; }
    .main-content { left: 0; right: 0; }
}
```

## 🎛️ Interactive Controls

### **Sidebar Toggle Buttons**
- **Position**: Fixed at panel edges for easy access
- **Visual Design**: Minimal icons with hover state feedback
- **Keyboard Support**: Tab navigation and Enter/Space activation
- **State Persistence**: Toggle states remembered across sessions

### **Auto-Hide Functionality**
- **Input Area**: Hides when inactive, shows on hover or keyboard focus
- **Accessibility Bar**: Slides up when not needed, appears on mouse movement
- **Smart Detection**: Context-aware hiding based on user interaction patterns

### **Panel Resize Behavior**
- **Smooth Transitions**: 0.3s ease animations for panel movements
- **Content Reflow**: Text and components adapt to changing panel widths
- **Minimum Widths**: Prevents panels from becoming unusably narrow
- **Breakpoint Handling**: Graceful degradation at responsive breakpoints

## 🎯 Theme System Integration

### **Theme Architecture**
The UI layout system supports three comprehensive themes:

1. **Default Theme**: Light mode with subtle grays and blue accents
2. **Dark Theme**: Dark backgrounds with high contrast text
3. **High Contrast**: Maximum accessibility with bold color differences

### **Theme-Aware Components**
```css
.high-contrast .left-sidebar {
    background-color: #000000;
    border-color: #666666;
}

.high-contrast .session-item {
    background-color: #333333;
    color: #ffffff;
}
```

### **CSS Custom Properties**
Themes modify layout colors through CSS custom property overrides:
```css
.high-contrast {
    --color-text-primary: #ffffff;
    --color-bg-subtle: #1a1a1a;
    --color-border: #666666;
}
```

## 🔧 Performance Considerations

### **CSS Optimization**
- **Minimal Repaints**: Transform-based animations avoid layout thrashing
- **GPU Acceleration**: 3D transforms trigger hardware acceleration
- **Efficient Selectors**: Flat selector hierarchy for fast style computation

### **JavaScript Integration**
- **Event Delegation**: Efficient event handling for dynamic content
- **Throttled Resize**: 60fps-limited resize event handlers
- **Memory Management**: Proper cleanup of event listeners and timers

### **Loading Strategy**
- **Critical CSS**: Layout styles loaded immediately for fast initial render
- **Progressive Enhancement**: Non-essential styling loaded asynchronously
- **Viewport Optimization**: Only visible panel content fully rendered

## 🚀 Accessibility Features

### **WCAG 2.1 AA Compliance**
- **Color Contrast**: 4.5:1 minimum ratio for text elements
- **Keyboard Navigation**: Full keyboard access to all interface elements
- **Screen Reader Support**: Proper ARIA labels and semantic markup
- **Focus Management**: Logical tab order and visible focus indicators

### **Inclusive Design**
- **High Contrast Mode**: Enhanced visibility for vision impairments
- **Scalable Text**: Respects user font size preferences
- **Reduced Motion**: Honors prefers-reduced-motion media queries
- **Touch Accessibility**: 44px minimum touch target sizes

---

*This UI layout documentation provides comprehensive guidance for AI coding assistants working with FastTTS interface components, enabling informed decisions about layout modifications, responsive behavior, and accessibility improvements.*