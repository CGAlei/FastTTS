"""
Left sidebar component for session management.
"""

from fasthtml.common import *


def render_left_sidebar(sessions, filter_params, current_session_id, sessions_content=None):
    """
    Renders the left sidebar with session list and filters.
    
    Args:
        sessions: List of session objects
        filter_params: Dictionary containing filter parameters
        current_session_id: Currently selected session ID
        sessions_content: Pre-rendered sessions content (optional)
        
    Returns:
        Div: Left sidebar container
    """
    return Div(
        # Fixed Header Section
        Div(
            # New Session Button
            Button(
                "➕ New Session",
                onclick="createNewSession()",
                cls="new-session-btn"
            ),
            
            # Filter Controls - Enhanced Compact Layout
            Div(
                Div(
                    # Search Input
                    Input(
                        type="text",
                        placeholder="Search...",
                        value=filter_params.get('search_text', ''),
                        cls="filter-search-input",
                        hx_post="/filter-sessions",
                        hx_target="#sessions-list",
                        hx_trigger="keyup changed delay:300ms",
                        hx_include="[name='favorites-filter'], [name='sort-filter']",
                        name="search"
                    ),
                    
                    # Favorites Filter Toggle (smaller icon button)
                    Button(
                        "⭐",
                        cls=f"filter-toggle-btn-compact {'active' if filter_params.get('show_favorites') else ''}",
                        hx_get="/filter-sessions",
                        hx_target="#sessions-list",
                        hx_include="[name='search'], [name='sort-filter']",
                        hx_vals=f'{{"favorites": "{not filter_params.get("show_favorites", False)}"}}',
                        name="favorites-filter",
                        title="Toggle favorites filter"
                    ),
                    
                    # Clear Filters Button (smaller icon button)
                    Button(
                        "🚫",
                        cls="clear-filters-btn-compact",
                        hx_get="/filter-sessions",
                        hx_target="#sessions-list",
                        title="Clear all filters"
                    ),
                    
                    cls="filter-controls-row"
                ),
                
                cls="filter-controls-compact"
            ),
            
            cls="left-sidebar-header"
        ),
        
        # Scrollable Content Section
        sessions_content if sessions_content else Div(id="sessions-list"),
        
        cls="left-sidebar",
        id="left-sidebar"
    )