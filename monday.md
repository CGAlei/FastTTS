# Right Sidebar - Vocabulary Dictionary System

## Overview
The right sidebar in FastTTS is a comprehensive vocabulary management system that displays Chinese words with AI-generated definitions, translations, and an integrated **5-star rating system**. It features a tabbed interface for different views and real-time synchronization across the application.

## Key Components

### 1. Header Section (`vocabulary.py:16-55`)
- **Title**: "词典" (Dictionary) with emoji icon
- **Info Capsules**: 
  - 📚 Database word count (live count)
  - 📅 Last modified time
  - 🔄 Refresh status indicator
- **Refresh Button**: Manual vocabulary state synchronization

### 2. Tabbed Interface (`vocabulary.py:57-114`)
Two main tabs with HTMX-powered content loading:

#### **Tab 1: 词汇信息 (Word Information)**
- Shows detailed vocabulary for currently selected words
- Displays AI-generated definitions with translations
- **NEW**: Integrated 5-star rating system for each word
- Real-time updates when words are clicked in the main content

#### **Tab 2: 词汇列表 (Word List)**  
- Searchable database of all vocabulary words
- Pagination with 20 words per page
- **NEW**: Rating display in word list items
- Debounced search with 500ms delay for performance

## ⭐ Rating System Features

### Interactive Rating Component (`main.py:1309-1324`)
```python
# 5-star rating slider in word information display
Input(
    type="range",
    min="0", max="5", step="1",
    value=str(vocab_data.get('rating', 0)),
    cls="star-rating",
    style=f"--val: {vocab_data.get('rating', 0)}",
    oninput="this.style.setProperty('--val', this.value); updateWordRating(this.value)",
    **{"data-word": vocab_data.get('word', '')},
    id="word-rating-input"
)
```

### Rating Display in Word List (`main.py:1673-1676`)
```python
# Read-only star display for word list items
Div("", cls="star-display", **{"data-rating": str(rating or 0)})
```

### JavaScript Rating Controller (`static/js/word-rating.js`)
- **`updateWordRating(rating)`**: Updates rating in database via POST request
- **`refreshWordListRatings()`**: Syncs ratings across tabs without switching
- **`showRatingUpdateFeedback(message)`**: Shows success notification
- **`onTabSwitch(tabName)`**: Handles cross-tab rating synchronization

### Backend Rating Endpoint (`main.py:1742+`)
- **Route**: `POST /update-word-rating`
- **Validation**: Rating must be 0-5, word must be valid Chinese
- **Database**: Updates SQLite vocabulary table with rating column
- **Response**: JSON success/error feedback

## CSS Styling (`static/css/components.css`)

### Star Rating Input (Lines 2322-2396)
- Custom CSS slider styled as 5 stars
- Dynamic `--val` CSS variable for visual updates
- Hover effects and responsive design
- Cross-browser compatibility (WebKit + Mozilla)

### Star Display (Lines 2397-2418)
- Read-only star ratings using data attributes
- Unicode star characters (★ and ☆)
- Color coding by rating level
- Responsive to theme changes

## Database Integration
- **Column**: `rating` INTEGER in vocabulary table
- **Range**: 0-5 stars (0 = unrated)
- **Default**: 0 for new words
- **Updates**: Real-time via AJAX calls

## Cross-Tab Synchronization
1. User rates word in "Word Information" tab
2. Rating saves to database immediately
3. Visual feedback shows success notification
4. "Word List" tab refreshes silently in background
5. Rating display updates without user switching tabs

## Performance Optimizations
- **Debounced Search**: 500ms delay prevents excessive API calls
- **Lazy Tab Loading**: Content loads only when tab is accessed
- **Background Refresh**: Rating updates don't block UI
- **Optimized Queries**: Database indexes for fast word lookups
- **HTMX Integration**: Minimal JavaScript for maximum responsiveness

## User Experience Flow
1. User clicks Chinese word in main karaoke area
2. Right sidebar shows word definition in "Word Information" tab
3. User can rate word 1-5 stars using interactive slider
4. Rating saves instantly with green success notification
5. User can switch to "Word List" tab to see all rated words
6. Search and pagination work seamlessly with rating display
7. All ratings persist across sessions and app restarts

The rating system is fully operational and provides both interactive rating input and visual display across all vocabulary interfaces!