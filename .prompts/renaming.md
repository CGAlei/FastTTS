# AI Code Engine Instructions: Session Rename Functionality Implementation

## Objective
Implement inline editing functionality for session titles in the left sidebar of a FastHTML/HTMX application, allowing users to click and edit custom names that persist to the `custom_name` field in session metadata JSON.

## Current State Analysis
- Sessions display truncated text content as titles: `session['text'][:60] + '...'`
- Session metadata stored in `session_metadata.json` with structure:
  ```json
  "session_id": {
    "is_favorite": boolean,
    "custom_name": null,
    "created_at": "timestamp",
    "modified_at": "timestamp"
  }
  ```
- Session rendering handled by `render_session_list()` function
- Metadata management via `get_session_metadata()` and `update_session_metadata()`

## Required Changes

### 1. Frontend UI Modifications

**File: `main.py` - `render_session_list()` function**

**Task**: Replace static title display with dual-mode editable interface

**Implementation Details**:
- Create helper function `get_display_title(session)` that returns `custom_name` if exists, otherwise fallback to truncated text
- Replace current title div with two-state container:
  - **Display State**: Show title text + edit button (pencil icon)
  - **Edit State**: Show input field + save/cancel buttons
- Use CSS classes to toggle visibility: `.hidden` class management
- Add unique IDs for each session's edit components using session ID

**Expected HTML Structure**:
```html
<div class="session-title-container">
  <div id="title-container-{session_id}" class="session-title-display">
    <span class="session-title-text">{display_title}</span>
    <button class="edit-title-btn" onclick="editSessionTitle('{session_id}')">✏️</button>
  </div>
  <div id="title-edit-{session_id}" class="session-title-edit hidden">
    <input type="text" id="title-input-{session_id}" value="{current_title}" maxlength="100">
    <button class="save-title-btn" hx-post="/update-session-name/{session_id}">✓</button>
    <button class="cancel-title-btn" onclick="cancelEditTitle('{session_id}')">✗</button>
  </div>
</div>
```

### 2. Backend API Endpoint

**File: `main.py`**

**Task**: Create new FastHTML route to handle session name updates

**Route**: `@rt("/update-session-name/{session_id}", methods=["POST"])`

**Implementation Logic**:
1. Extract `session_id` from URL parameter
2. Parse form data to get new title from input field
3. Validate input (max 100 characters, sanitize)
4. Call `update_session_metadata(session_id, custom_name=new_name)`
5. Retrieve updated session data
6. Return updated HTML fragment for title container
7. Include HTMX out-of-band swap to hide edit mode

**Error Handling**:
- Session not found: Return error message
- Invalid input: Truncate/sanitize and proceed
- Database errors: Log and return user-friendly error

**Response Format**: HTML fragment that replaces the title container and resets edit form

### 3. JavaScript Interaction Functions

**Files**: Add to existing JS files or inline script

**Required Functions**:

**`editSessionTitle(sessionId)`**:
- Hide display container (`#title-container-{sessionId}`)
- Show edit container (`#title-edit-{sessionId}`)
- Focus input field and select existing text
- Prevent event bubbling to session click handler

**`cancelEditTitle(sessionId)`**:
- Hide edit container
- Show display container
- Reset input value to original text
- No server interaction required

**Global Event Handlers**:
- **Enter Key**: Trigger save button click
- **Escape Key**: Trigger cancel action
- **Click Outside**: Optional - auto-cancel edit mode

### 4. CSS Styling Requirements

**Files**: Add to existing CSS files

**Key Styles Needed**:
- `.session-title-container`: Relative positioning for dual-mode layout
- `.edit-title-btn`: Hidden by default, show on session hover with smooth opacity transition
- `.session-title-input`: Styled input field matching app theme
- `.save-title-btn`, `.cancel-title-btn`: Small action buttons
- `.hidden`: Display none utility class
- Responsive considerations for mobile devices

**Visual Behavior**:
- Edit button appears on hover with fade-in animation
- Smooth transition between display and edit modes
- Input field should match existing form styling
- Maintain session item height consistency during mode changes

### 5. Data Flow Integration

**HTMX Integration**:
- Use `hx-post` for save action with `hx-include` to capture input value
- Use `hx-target` and `hx-swap="outerHTML"` to replace title container
- Implement `hx-swap-oob` to simultaneously hide edit form
- Maintain existing session loading functionality without interference

**State Management**:
- Preserve current session highlighting during title edit
- Update session list state without full page reload
- Maintain filter and sort states during title updates
- Handle concurrent edit prevention (optional enhancement)

## Expected Outcomes

### User Experience
1. **Intuitive Editing**: Users hover over session title → edit button appears → click to edit
2. **Instant Feedback**: Save/cancel actions provide immediate visual response
3. **Keyboard Shortcuts**: Enter to save, Escape to cancel
4. **Persistent Names**: Custom names survive app restarts and persist across sessions
5. **Fallback Behavior**: When no custom name set, display original truncated text

### Technical Results
1. **Database Updates**: `session_metadata.json` properly updated with custom names
2. **HTMX Reactivity**: Smooth updates without page refresh
3. **State Consistency**: Edit mode states properly managed across multiple sessions
4. **Error Resilience**: Graceful handling of edge cases and server errors
5. **Performance**: Minimal overhead, efficient DOM updates

### Integration Points
- Seamlessly integrates with existing favorite toggle functionality
- Compatible with session filtering and search features
- Maintains session loading behavior when clicking on content area
- Preserves delete session functionality
- Works with mobile responsive design

## Success Criteria
- [ ] Edit button appears on session hover
- [ ] Clicking edit button switches to input mode
- [ ] Save functionality updates metadata and refreshes display
- [ ] Cancel functionality reverts changes without server call
- [ ] Custom names persist across application restarts
- [ ] No conflicts with existing session management features
- [ ] Responsive design maintained on all screen sizes
- [ ] Keyboard shortcuts work as expected
- [ ] Error states handled gracefully