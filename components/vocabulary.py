"""
Right sidebar component for vocabulary display.
"""

from fasthtml.common import *


def render_right_sidebar():
    """
    Renders the right sidebar with vocabulary information and tabs.
    
    Returns:
        Div: Right sidebar container
    """
    return Div(
        # LAYER 1: Compact Header with Info Capsules
        Div(
            H2("词典 ", cls="text-lg font-semibold flex-shrink-0"),
            # Info Capsules Container
            Div(
                # Database Capsule
                Span(
                    "📚 ",
                    Span("0", id="db-word-count", cls="font-medium"),
                    cls="info-capsule db-capsule",
                    title="Database word count"
                ),
                # Modified Capsule  
                Span(
                    "📅 ",
                    Span("--", id="db-modified-time", cls="font-medium"),
                    cls="info-capsule modified-capsule",
                    title="Last modified time"
                ),
                # Status Capsule
                Span(
                    "🔄 ",
                    Span("--", id="db-status-icon", cls="font-medium"),
                    cls="info-capsule status-capsule",
                    title="Refresh status"
                ),
                cls="info-capsules-container flex gap-2",
                id="info-capsules"
            ),
            Button(
                "🔄",
                cls="refresh-vocab-btn flex-shrink-0",
                id="refresh-vocab-btn",
                title="Refresh vocabulary state",
                onclick="refreshVocabularyState()",
                **{"aria-label": "Refresh vocabulary database synchronization"}
            ),
            cls="vocab-header-compact flex items-center justify-between gap-3 py-4 pr-4 pl-8 border-b",
            id="vocab-header-permanent"
        ),
        
        # LAYER 2: HTMX Tabs
        Div(
            # Tab Navigation
            Div(
                id="vocab-tabs", 
                hx_target="#vocab-tab-contents", 
                role="tablist",
                **{
                    "hx-on:htmx-after-on-load": """
                        let currentTab = document.querySelector('[aria-selected=true]');
                        currentTab.setAttribute('aria-selected', 'false');
                        currentTab.classList.remove('vocab-tab-selected');
                        let newTab = event.target;
                        newTab.setAttribute('aria-selected', 'true');
                        newTab.classList.add('vocab-tab-selected');
                        
                        // Notify rating system of tab switch
                        if (typeof window.onTabSwitch === 'function') {
                            const tabName = newTab.id === 'tab-word-list-btn' ? 'word-list' : 'word-info';
                            window.onTabSwitch(tabName);
                        }
                    """
                },
                cls="vocab-tabs-nav flex border-b"
            )(
                Button(
                    "词汇信息", 
                    role="tab", 
                    **{"aria-controls": "vocab-tab-contents", "aria-selected": "true"}, 
                    hx_get="/tab-word-info", 
                    hx_swap="innerHTML",
                    cls="vocab-tab vocab-tab-selected",
                    id="tab-word-info-btn"
                ),
                Button(
                    "词汇列表", 
                    role="tab", 
                    **{"aria-controls": "vocab-tab-contents", "aria-selected": "false"}, 
                    hx_get="/tab-word-list", 
                    hx_swap="innerHTML",
                    cls="vocab-tab",
                    id="tab-word-list-btn"
                )
            ),
            
            # Tab Content Container
            Div(
                id="vocab-tab-contents", 
                role="tabpanel", 
                hx_get="/tab-word-info", 
                hx_trigger="load",
                hx_swap="innerHTML",
                cls="vocab-tab-content",
                style="height: calc(100vh - 48px); overflow-y: auto;"
            ),
            
            cls="vocab-tabs-container flex flex-col flex-1"
        ),
        
        cls="right-sidebar h-full flex flex-col",
        id="right-sidebar"
    )