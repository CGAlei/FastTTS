"""
Vocabulary management routes for FastTTS application.
Includes word interactions, AI definitions, search, and vocabulary display.
"""

from fasthtml.common import *
import logging
import json
import asyncio
from datetime import datetime
from starlette.responses import JSONResponse

# Import optimized database operations
from utils.db_helpers import (
    search_vocabulary_optimized,
    check_word_in_vocabulary_optimized,
    get_vocabulary_info_optimized,
    execute_query,
    initialize_database_indexes
)

# Import text helpers
from utils.text_helpers import (
    get_google_translate,
    insert_vocabulary_word,
    update_session_timestamp_for_word,
    update_all_sessions_with_word
)

logger = logging.getLogger(__name__)

def register_vocabulary_routes(rt, llm_manager=None, vocabulary_manager=None):
    """Register vocabulary routes with the FastHTML router"""
    
    # Initialize database indexes for better performance
    initialize_database_indexes()

    @rt("/word-interaction", methods=["POST"])
    async def word_interaction(request):
        """Handle word container interaction callbacks from frontend - OPTIMIZED"""
        try:
            data = await request.json()
            action = data.get('action')
            word = data.get('word', '').strip()
            
            if not word:
                return JSONResponse({"error": "No word provided"})
            
            # Handle different actions
            if action == 'translate':
                # Quick Google Translate popup
                translation = get_google_translate(word, 'es')
                
                return Div(
                    Div(
                        Div(
                            H3(f"🔤 {word}", cls="text-lg font-semibold mb-2"),
                            P(f"🌐 Translation: {translation}", cls="text-base mb-2"),
                            
                            # Quick actions
                            Div(
                                Button(
                                    "📖 Define with AI",
                                    cls="define-btn-popup bg-blue-500 text-white px-3 py-1 rounded mr-2",
                                    hx_post="/define-word",
                                    hx_vals=json.dumps({"word": word}),
                                    hx_target="#translate-popup",
                                    hx_swap="outerHTML"
                                ),
                                Button(
                                    "❌ Close",
                                    cls="close-btn bg-gray-500 text-white px-3 py-1 rounded",
                                    onclick="document.getElementById('translate-popup').remove()"
                                ),
                                cls="flex gap-2 mt-2"
                            ),
                            cls="translate-popup-content bg-white p-4 rounded-lg shadow-lg border max-w-md"
                        ),
                        cls="translate-popup-overlay fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50",
                        onclick="event.target === this && this.remove()",
                        id="translate-popup"
                    )
                )
                
            elif action == 'check_status':
                # Quick vocabulary status check using optimized function
                is_in_db = check_word_in_vocabulary_optimized(word)
                
                return JSONResponse({
                    "word": word,
                    "isInDB": is_in_db,
                    "status": "known" if is_in_db else "unknown"
                })
                
            else:
                return JSONResponse({"error": "Unknown action"})
                
        except Exception as e:
            logger.error(f"Error in word interaction: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)

    @rt("/define-word", methods=["POST"])
    async def define_word(request):
        """Generate AI-powered definition for unknown word and save to database - OPTIMIZED WITH ASYNC"""
        try:
            data = await request.json()
            word = data.get('word', '').strip()
            
            if not word:
                return JSONResponse({"error": "No word provided"})
            
            # Quick check if word already exists using optimized function
            if check_word_in_vocabulary_optimized(word):
                vocab_info = get_vocabulary_info_optimized(word)
                if vocab_info:
                    return Div(
                        H3(f"📖 {word} (Already in Database)", cls="text-lg font-semibold mb-2"),
                        P(f"🔤 Pinyin: {vocab_info.get('pinyin', 'N/A')}", cls="text-sm mb-1"),
                        P(f"🌐 Spanish: {vocab_info.get('spanish_meaning', 'N/A')}", cls="text-sm mb-1"),
                        P(f"🇨🇳 Chinese: {vocab_info.get('chinese_meaning', 'N/A')}", cls="text-sm mb-2"),
                        Button(
                            "✅ Close",
                            cls="close-btn bg-green-500 text-white px-3 py-1 rounded",
                            onclick="document.getElementById('translate-popup').remove()"
                        ),
                        cls="translate-popup-content bg-white p-4 rounded-lg shadow-lg border max-w-md",
                        id="translate-popup"
                    )
            
            # Show loading state immediately
            loading_response = Div(
                H3(f"🤖 Defining: {word}", cls="text-lg font-semibold mb-2"),
                P("⏳ AI is generating definition...", cls="text-sm mb-2"),
                Div(cls="animate-pulse bg-gray-200 h-4 rounded mb-2"),
                Div(cls="animate-pulse bg-gray-200 h-4 rounded mb-2 w-3/4"),
                cls="translate-popup-content bg-white p-4 rounded-lg shadow-lg border max-w-md",
                id="translate-popup"
            )
            
            # Start async AI definition generation (non-blocking)
            async def generate_and_save_definition():
                try:
                    if llm_manager:
                        # Call LLM asynchronously
                        definition_data = await llm_manager.get_word_definition(word)
                        
                        if definition_data and isinstance(definition_data, dict):
                            # Save to database
                            success = insert_vocabulary_word(definition_data)
                            
                            if success:
                                # Update session timestamps in background
                                asyncio.create_task(update_all_sessions_with_word(word))
                                return True
                                
                except Exception as e:
                    logger.error(f"Error generating definition for {word}: {e}")
                    return False
            
            # Start background task
            asyncio.create_task(generate_and_save_definition())
            
            # Return immediate loading response with polling
            return Div(
                loading_response,
                Script(f"""
                    // Poll for completion every 2 seconds, max 30 seconds
                    let pollCount = 0;
                    const maxPolls = 15;
                    
                    function pollDefinition() {{
                        if (pollCount >= maxPolls) {{
                            document.getElementById('translate-popup').innerHTML = `
                                <div class="translate-popup-content bg-white p-4 rounded-lg shadow-lg border max-w-md">
                                    <h3 class="text-lg font-semibold mb-2">⚠️ Definition Timeout</h3>
                                    <p class="text-sm mb-2">AI definition is taking longer than expected.</p>
                                    <button class="close-btn bg-gray-500 text-white px-3 py-1 rounded" 
                                            onclick="document.getElementById('translate-popup').remove()">Close</button>
                                </div>
                            `;
                            return;
                        }}
                        
                        fetch('/word-interaction', {{
                            method: 'POST',
                            headers: {{'Content-Type': 'application/json'}},
                            body: JSON.stringify({{'action': 'check_status', 'word': '{word}'}})
                        }})
                        .then(r => r.json())
                        .then(data => {{
                            if (data.isInDB) {{
                                // Word is now in database, refresh the popup
                                fetch('/define-word', {{
                                    method: 'POST',
                                    headers: {{'Content-Type': 'application/json'}},
                                    body: JSON.stringify({{'word': '{word}'}})
                                }})
                                .then(r => r.text())
                                .then(html => {{
                                    document.getElementById('translate-popup').outerHTML = html;
                                }});
                            }} else {{
                                pollCount++;
                                setTimeout(pollDefinition, 2000);
                            }}
                        }})
                        .catch(() => {{
                            pollCount++;
                            setTimeout(pollDefinition, 2000);
                        }});
                    }}
                    
                    setTimeout(pollDefinition, 2000);
                """)
            )
            
        except Exception as e:
            logger.error(f"Error defining word: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)

    @rt("/search-words")
    def search_words(request):
        """Search vocabulary database with pagination - OPTIMIZED"""
        try:
            # Get search parameters
            query_params = getattr(request, 'query_params', {})
            search_query = query_params.get('search', '').strip()
            page = int(query_params.get('page', '1'))
            per_page = 20  # Fixed page size for better performance
            
            # Use optimized search function
            results, total_count = search_vocabulary_optimized(search_query, page, per_page)
            
            if not results:
                return Div(
                    Div("No words found", cls="text-center text-gray-500 py-8"),
                    cls="word-list-container h-full flex flex-col"
                )
            
            # Generate word items efficiently
            word_items = []
            for result in results:
                chinese_word, pinyin, spanish, chinese_meaning, word_type, synonyms, antonyms, usage, updated = result
                
                word_items.append(
                    Div(
                        Div(
                            Strong(chinese_word, cls="text-lg"),
                            Span(f" [{pinyin}]", cls="text-sm text-gray-600 ml-2"),
                            cls="word-header mb-1"
                        ),
                        Div(
                            Span("🌐 ", cls="text-xs"),
                            Span(spanish or "No translation", cls="text-sm"),
                            cls="word-spanish mb-1"
                        ),
                        Div(
                            Span("🇨🇳 ", cls="text-xs"),
                            Span(chinese_meaning or "No definition", cls="text-sm"),
                            cls="word-chinese"
                        ) if chinese_meaning else None,
                        cls="word-item p-3 border-b hover:bg-gray-50 cursor-pointer",
                        onclick=f"showWordDetails('{chinese_word}')"
                    )
                )
            
            # Calculate pagination
            total_pages = (total_count + per_page - 1) // per_page
            
            # Generate pagination controls efficiently
            pagination_controls = []
            
            if page > 1:
                pagination_controls.append(
                    Button(
                        "←",
                        cls="pagination-btn",
                        hx_get=f"/search-words?page={page-1}&search={search_query}",
                        hx_target="#word-list-container",
                        hx_swap="innerHTML"
                    )
                )
            
            pagination_controls.append(
                Span(f"{page} of {total_pages}", cls="pagination-info")
            )
            
            if page < total_pages:
                pagination_controls.append(
                    Button(
                        "→",
                        cls="pagination-btn",
                        hx_get=f"/search-words?page={page+1}&search={search_query}",
                        hx_target="#word-list-container",
                        hx_swap="innerHTML"
                    )
                )
            
            # Return optimized content
            return Div(
                # Word list
                Div(
                    *word_items,
                    cls="word-list-content p-4 flex-1 overflow-y-auto"
                ),
                
                # Pagination
                Div(
                    *pagination_controls,
                    cls="word-pagination flex items-center justify-between p-4 border-t"
                ) if total_pages > 1 else None,
                
                cls="word-list-container h-full flex flex-col"
            )
            
        except Exception as e:
            logger.error(f"Error searching words: {e}")
            return Div(
                "Error loading vocabulary list",
                cls="text-center text-red-500 py-8"
            )

    @rt("/tab-word-info")
    def tab_word_info():
        """Tab content for word information display - OPTIMIZED"""
        return Div(
            id="vocabulary-content",
            cls="vocabulary-display-area",
            **{"hx-trigger": "load", "hx-get": "/vocabulary-display", "hx-target": "this", "hx-swap": "innerHTML"}
        )

    @rt("/tab-word-list")
    def tab_word_list():
        """Tab content for word list display with search and pagination - OPTIMIZED"""
        return Div(
            # Search Section - Optimized with debouncing
            Div(
                Input(
                    type="text",
                    placeholder="Search vocabulary...",
                    cls="w-full p-3 border rounded-lg",
                    hx_get="/search-words",
                    hx_target="#word-list-container",
                    hx_trigger="keyup changed delay:500ms",
                    hx_sync="this:abort",  # Cancel previous requests
                    name="search"
                ),
                cls="p-4 border-b"
            ),
            
            # Word List Container
            Div(
                id="word-list-container",
                cls="flex-1 overflow-hidden",
                **{"hx-trigger": "load", "hx-get": "/search-words", "hx-target": "this", "hx-swap": "innerHTML"}
            ),
            
            cls="h-full flex flex-col",
            id="word-list-tab"
        )

    @rt("/vocabulary-display", methods=["POST"])
    def vocabulary_display(request):
        """Display vocabulary information for current session - OPTIMIZED"""
        try:
            # This route would typically show vocabulary for the current session
            # For now, return a placeholder that loads efficiently
            
            return Div(
                Div(
                    H3("📚 Session Vocabulary", cls="text-lg font-semibold mb-4"),
                    P("Select words in the text above to see vocabulary information here.", 
                      cls="text-gray-600 text-center py-8"),
                    cls="p-4"
                ),
                id="vocabulary-info-content"
            )
            
        except Exception as e:
            logger.error(f"Error in vocabulary display: {e}")
            return Div(
                "Error loading vocabulary information",
                cls="text-center text-red-500 py-8"
            )

    @rt("/refresh-vocabulary", methods=["POST"])
    async def refresh_vocabulary(request):
        """Refresh vocabulary status for all sessions - OPTIMIZED WITH BACKGROUND PROCESSING"""
        try:
            if vocabulary_manager:
                # Start background refresh task
                asyncio.create_task(vocabulary_manager.refresh_all_sessions())
            
            return JSONResponse({
                "success": True,
                "message": "Vocabulary refresh started in background"
            })
            
        except Exception as e:
            logger.error(f"Error starting vocabulary refresh: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)

    @rt("/vocab-stats")
    def vocab_stats():
        """Get vocabulary statistics - OPTIMIZED"""
        try:
            # Use optimized query for statistics
            total_words = execute_query("SELECT COUNT(*) FROM vocabulary", fetch_one=True)
            ai_generated = execute_query(
                "SELECT COUNT(*) FROM vocabulary WHERE filename = 'AI_Generated'",
                fetch_one=True
            )
            
            total_count = total_words[0] if total_words else 0
            ai_count = ai_generated[0] if ai_generated else 0
            
            return JSONResponse({
                "total_words": total_count,
                "ai_generated": ai_count,
                "imported": total_count - ai_count
            })
            
        except Exception as e:
            logger.error(f"Error getting vocabulary stats: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)

    logger.info("Vocabulary routes registered successfully")
    return {
        "word_interaction": word_interaction,
        "define_word": define_word,
        "search_words": search_words,
        "tab_word_info": tab_word_info,
        "tab_word_list": tab_word_list,
        "vocabulary_display": vocabulary_display,
        "refresh_vocabulary": refresh_vocabulary,
        "vocab_stats": vocab_stats
    }