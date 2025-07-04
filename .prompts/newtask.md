# Session Renaming Implementation Plan for AI Coding Assistant

## Overview
Implement optional session renaming functionality for a FastHTML application using inline editing. Sessions are currently auto-named using the first 60 characters of content. Add the ability to rename sessions through double-click inline editing without disrupting the existing fast-save workflow.

## Current Architecture Context
- **Framework**: FastHTML with HTMX for reactive updates
- **Session Storage**: JSON files with metadata in `session_metadata.json`
- **Session Display**: Left sidebar showing session list with favorites and delete buttons
- **Existing Save Flow**: Direct save with auto-generated names from content preview
- **Mobile Support**: Responsive design with mobile menu toggle

## Core Requirements

### 1. Session Title Display Logic
- **Primary**: Display `custom_name` if it exists in session metadata
- **Fallback**: Display first 60 characters of session content if `custom_name` is null
- **Visual Distinction**: Add subtle styling to indicate custom-named vs auto-named sessions
- **Truncation**: Ensure long custom names don't break layout (max width with ellipsis)

### 2. Inline Editing Behavior
- **Trigger**: Double-click on session title text to enter edit mode
- **Edit State**: Replace title text with input field pre-filled with current name
- **Input Styling**: Match existing form input styling, proper focus indication
- **Save Actions**: Enter key or blur event saves the new name
- **Cancel Action**: Escape key cancels editing and reverts to original name
- **Validation**: Prevent empty names, trim whitespace, limit length to reasonable characters

### 3. Backend Integration
- **New Endpoint**: `POST /rename-session/{session_id}` accepting form data with new name
- **Metadata Update**: Modify existing `update_session_metadata()` function to handle custom_name
- **JSON Persistence**: Update `session_metadata.json` file atomically
- **Response Format**: Return updated session HTML fragment for HTMX replacement
- **Error Handling**: Validate session exists, handle file write errors gracefully

### 4. Frontend JavaScript Requirements
- **Event Delegation**: Handle double-click events on dynamically generated session items
- **Edit Mode Toggle**: Show/hide input field, manage focus states
- **Keyboard Handling**: Enter to save, Escape to cancel, proper tab navigation
- **Input Field Management**: Auto-select text on edit, handle blur events
- **HTMX Integration**: Trigger POST request on save with proper form data

### 5. HTMX Integration Pattern
- **Target Strategy**: Update individual session item using `hx-target="#session-item-{session_id}"`
- **Swap Strategy**: Replace session item content with `hx-swap="outerHTML"`
- **Include Pattern**: Include input field value in request using `hx-include`
- **Indicator**: Optional loading state during rename operation
- **Fallback**: Handle network errors with user feedback

### 6. Session List Rendering Updates
- **Template Modification**: Update `render_session_list()` function in main.py
- **Conditional Logic**: Check for `custom_name` in session metadata before falling back to content preview
- **CSS Classes**: Add classes for styling custom vs auto-generated names
- **Accessibility**: Proper ARIA labels for editable session titles
- **Data Attributes**: Include session ID and current name for JavaScript access

### 7. Mobile Responsiveness
- **Touch Support**: Ensure double-tap works on mobile devices
- **Input Sizing**: Proper input field sizing on small screens
- **Virtual Keyboard**: Handle virtual keyboard appearance/disappearance
- **Touch Targets**: Maintain adequate touch target sizes for session items

### 8. Integration with Existing Features
- **Search Functionality**: Ensure custom names are searchable in session filter
- **Favorites System**: Preserve favorite status during rename operations
- **Session Loading**: Maintain session loading behavior when custom names are used
- **Delete Operations**: No changes needed to existing delete functionality

### 9. Error Handling and Edge Cases
- **Concurrent Edits**: Handle case where session is renamed while in edit mode
- **Special Characters**: Properly escape and sanitize custom names
- **Long Names**: Graceful handling of very long custom names
- **Duplicate Names**: Allow duplicate names (no uniqueness constraint needed)
- **Session Deletion**: Clean up any active edit states if session is deleted

### 10. Testing Scenarios
- **Double-click to rename**: Verify edit mode activation works correctly
- **Save with Enter**: Confirm Enter key saves and exits edit mode
- **Cancel with Escape**: Verify Escape key cancels without saving
- **Click outside to save**: Ensure blur event saves changes
- **Empty name handling**: Prevent saving empty or whitespace-only names
- **Session list updates**: Confirm HTMX properly updates session display
- **Mobile interaction**: Test double-tap behavior on touch devices
- **Concurrent operations**: Test renaming during session loading/saving

### 11. Backward Compatibility
- **Existing Sessions**: All existing sessions work unchanged with auto-generated names
- **Save Workflow**: No changes to current fast-save behavior
- **API Compatibility**: Existing endpoints remain unchanged
- **File Format**: Session metadata JSON remains compatible with current structure

## Success Criteria
- Sessions can be renamed through double-click inline editing
- Current save workflow remains completely unchanged
- Custom names display properly and persist across sessions
- Mobile devices support rename functionality
- No conflicts with existing input panel or modal systems
- Graceful error handling and user feedback
- Maintains existing performance characteristics

This implementation provides optional customization without disrupting the core user experience of fast session saving and management.