"""
Reusable UI elements for FastTTS application.
"""

from fasthtml.common import *


def render_mobile_toggle():
    """
    Renders the mobile menu toggle button.
    
    Returns:
        Button: Mobile menu toggle button
    """
    return Button(
        "☰",
        onclick="toggleMobileMenu()",
        cls="mobile-menu-toggle",
        id="mobile-menu-toggle"
    )


def render_sidebar_toggles():
    """
    Renders the sidebar toggle buttons positioned outside sidebars.
    
    Returns:
        Tuple[Button, Button]: Left and right sidebar toggle buttons
    """
    return (
        # Left sidebar toggle
        Button(
            "⟨",
            cls="sidebar-toggle left-toggle",
            onclick="toggleLeftSidebar()",
            id="left-toggle",
            title="Collapse Sessions Panel",
            **{"aria-label": "Toggle sessions panel visibility"}
        ),
        # Right sidebar toggle
        Button(
            "⟨",
            cls="sidebar-toggle right-toggle",
            onclick="toggleRightSidebar()",
            id="right-toggle",
            title="Collapse Dictionary Panel",
            **{"aria-label": "Toggle dictionary panel visibility"}
        )
    )


def render_accessibility_controls():
    """
    Renders the accessibility controls (font size and theme buttons).
    
    Returns:
        Div: Accessibility controls container
    """
    return Div(
        # Background spacer to prevent black showing behind accessibility controls
        Div(
            cls="theme-bg-spacer",
            style="position: absolute; top: 0; left: 0; right: 0; height: 60px; z-index: 999;"
        ),
        Div(
            Div(
                Div(
                    Button("A", onclick="adjustFontSize('1')", 
                           cls="font-btn font-small", id="font-small", title="Small Font"),
                    Button("A", onclick="adjustFontSize('2')", 
                           cls="font-btn font-medium active", id="font-medium", title="Medium Font"),
                    Button("A", onclick="adjustFontSize('3')", 
                           cls="font-btn font-large", id="font-large", title="Large Font"),
                    Button("A", onclick="adjustFontSize('4')", 
                           cls="font-btn font-xlarge", id="font-xlarge", title="Extra Large Font"),
                    cls="font-buttons"
                ),
                cls="flex items-center gap-2"
            ),
            Div(
                Div(
                    Button("🌞", onclick="changeColorScheme('default')", 
                           cls="theme-btn theme-default active", id="theme-default", title="Light Theme"),
                    Button("⚫", onclick="changeColorScheme('high-contrast')", 
                           cls="theme-btn theme-contrast", id="theme-contrast", title="High Contrast"),
                    Button("🌙", onclick="changeColorScheme('dark-mode')", 
                           cls="theme-btn theme-dark", id="theme-dark-mode", title="Dark Theme"),
                    Button("⚙️", onclick="openSettingsPopup()", 
                           cls="theme-btn settings-btn", id="settings-btn", title="Settings"),
                    cls="theme-buttons"
                ),
                cls="flex items-center gap-2"
            ),
            
            # Enhanced Audio Player - Inspired by Green Audio Player
            Div(
                Button("▶", id="mini-play-btn", onclick="toggleMiniAudio()", cls="play-btn"),
                Div("0:00", id="mini-time-display", cls="time-display"),
                Div(
                    Div("", id="mini-progress-bar", cls="progress-bar"),
                    onclick="seekMiniAudio(event)",
                    cls="progress-container"
                ),
                id="mini-audio-player",
                cls="mini-audio-player"
            ),
            cls="accessibility-controls"
        )
    )


def render_input_area(chinese_text="", DEFAULT_VOICE="zh-CN-XiaoxiaoNeural", 
                     DEFAULT_SPEED="1.0", DEFAULT_VOLUME="1.0", DEFAULT_ENGINE="edge"):
    """
    Renders the input area with progress bar and form.
    
    Args:
        chinese_text: Default text to show in textarea
        DEFAULT_VOICE: Default TTS voice
        DEFAULT_SPEED: Default speech speed
        DEFAULT_VOLUME: Default volume level
        DEFAULT_ENGINE: Default TTS engine
        
    Returns:
        Div: Input area container
    """
    return Div(
        # MiniMax Progress Bar with Messages (Always visible)
        Div(
            Div(
                hx_get="/minimax-progress",
                hx_trigger="startProgress from:body, every 600ms",
                hx_target="this",
                hx_swap="innerHTML",
                cls="progress-container"
            )(
                # Progress message area
                Div("", id="progress-message", cls="progress-message"),
                # Progress bar
                Div(
                    Div(id="minimax-progress-bar", cls="progress-bar", style="width:0%"),
                    cls="progress"
                )
            ),
            cls="mb-3"
        ),
        Form(
            Div(
                Textarea(chinese_text, 
                       name="custom_text",
                       id="custom-text",
                       rows="4",
                       placeholder="Enter Chinese text for TTS...",
                       cls="w-full p-4 pr-16 border-0 resize-none focus:outline-none text-base bg-transparent"),
                Div(
                    Button("🔊", 
                           hx_post="/generate-custom-tts", 
                           hx_target="#audio-container",
                           hx_include="#custom-text",
                           hx_vals=f"js:{{'voice': window.settingsManager ? window.settingsManager.getCurrentVoice() : '{DEFAULT_VOICE}', 'speed': window.settingsManager ? window.settingsManager.getCurrentSpeed() : '{DEFAULT_SPEED}', 'volume': window.settingsManager ? window.settingsManager.getCurrentVolume() : '{DEFAULT_VOLUME}', 'tts_engine': window.settingsManager ? window.settingsManager.getCurrentEngine() : '{DEFAULT_ENGINE}'}}",
                           **{"hx-trigger": "click, startProgress from:this"},
                           title="Generate TTS",
                           cls="input-action-btn",
                           onclick="window.ttsPending = true; if(window.resetTTSTimeout) window.resetTTSTimeout(); htmx.trigger(document.body, 'startProgress')"),
                    Button("💾", 
                           onclick="saveCurrentSession(event)",
                           title="Save Session",
                           type="button",
                           cls="input-action-btn"),
                    cls="absolute right-6 top-2 flex flex-col gap-1"
                ),
                cls="relative"
            ),
            cls="chat-input-container"
        ),
        cls="input-area"
    )