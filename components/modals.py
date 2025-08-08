"""
Modal components for FastTTS application.
"""

from fasthtml.common import *
from config.defaults import DEFAULT_VOLUME, DEFAULT_VOLUME_DISPLAY


def render_settings_modal(credentials_manager=None):
    """
    Renders the settings modal popup with tabbed interface.
    
    Args:
        credentials_manager: Instance of CredentialsManager for API credentials
        
    Returns:
        Div: Settings modal container
    """
    # Default empty credentials if manager not provided
    minimax_creds = credentials_manager.get_credentials('minimax') if credentials_manager else {}
    
    return Div(
        Div(
            # Modal Header with Title and Close Button
            Div(
                H3("⚙️ Settings", cls="text-xl font-bold text-gray-800"),
                Button("×", onclick="closeSettingsPopup()", cls="close-btn", **{"aria-label": "Close Settings"}),
                cls="modal-header flex justify-between items-center"
            ),
            
            # Tab Navigation
            Div(
                Button(
                    Span("🎵", cls="tab-icon"),
                    Span("Voice & Speech", cls="tab-label"),
                    cls="settings-tab active",
                    **{"data-tab": "voice"},
                    onclick="switchSettingsTab('voice')"
                ),
                Button(
                    Span("🔧", cls="tab-icon"),
                    Span("Advanced API", cls="tab-label"),
                    cls="settings-tab",
                    **{"data-tab": "api"},
                    onclick="switchSettingsTab('api')"
                ),
                cls="settings-tabs flex border-b border-gray-200 mb-6"
            ),
            
            # Tab Content Container
            Div(
                # Tab 1: Voice & Speech Settings
                render_voice_settings_tab(),
                
                # Tab 2: Advanced API Configuration
                render_api_settings_tab(minimax_creds),
                
                cls="tab-content-container"
            ),
            
            cls="modal-content bg-white rounded-lg p-0 max-w-3xl w-full max-h-[90vh] overflow-hidden shadow-2xl"
        ),
        cls="settings-modal fixed inset-0 bg-black bg-opacity-50 hidden flex items-center justify-center p-4",
        id="settings-modal",
        onclick="closeSettingsPopup(event)"
    )


def render_voice_settings_tab():
    """
    Renders the voice and speech settings tab content.
    
    Returns:
        Div: Voice settings tab container
    """
    return Div(
        # TTS Engine Selection
        Div(
            Label("TTS Engine:", cls="block text-sm font-medium mb-2 text-gray-700"),
            Select(
                Option("Microsoft Edge TTS", value="edge", selected=True),
                Option("MiniMax Hailuo TTS", value="hailuo"),
                cls="engine-select w-full p-3 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                id="engine-selector",
                onchange="changeTTSEngine(this.value)"
            ),
            cls="mb-6"
        ),
        
        # Voice Selection
        Div(
            Label("Voice:", cls="block text-sm font-medium mb-2 text-gray-700"),
            Select(
                Option("Microsoft Xiaoxiao (Female)", value="zh-CN-XiaoxiaoNeural", selected=True),
                Option("Microsoft Xiaoyi (Female)", value="zh-CN-XiaoyiNeural"),
                Option("Microsoft Yunjian (Male)", value="zh-CN-YunjianNeural"),
                Option("Microsoft Yunxi (Male)", value="zh-CN-YunxiNeural"),
                Option("Microsoft Yunxia (Female)", value="zh-CN-YunxiaNeural"),
                Option("Microsoft Yunyang (Male)", value="zh-CN-YunyangNeural"),
                Option("Microsoft Xiaobei (Female - Northeastern)", value="zh-CN-liaoning-XiaobeiNeural"),
                Option("Microsoft Xiaoni (Female - Shaanxi)", value="zh-CN-shaanxi-XiaoniNeural"),
                cls="voice-select w-full p-3 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                id="voice-selector",
                onchange="changeVoice(this.value)"
            ),
            cls="mb-6"
        ),
        
        # Speed Control
        Div(
            Label("Speech Speed:", cls="block text-sm font-medium mb-2 text-gray-700"),
            Div(
                Input(
                    type="range",
                    min="0.5",
                    max="2.0",
                    step="0.1",
                    value="1.0",
                    cls="speed-slider w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer",
                    id="speed-slider",
                    oninput="changeSpeed(this.value)"
                ),
                cls="mb-3"
            ),
            Div(
                Span("0.5×", cls="text-xs text-gray-500 font-medium"),
                Span("1.0× Normal", cls="text-sm font-semibold text-blue-600", id="speed-display"),
                Span("2.0×", cls="text-xs text-gray-500 font-medium"),
                cls="flex justify-between items-center"
            ),
            cls="mb-6"
        ),
        
        # Audio Settings Section
        Div(
            Label("Audio Settings:", cls="block text-sm font-medium mb-3 text-gray-700"),
            Div(
                Div(
                    Label("Output Quality:", cls="block text-xs font-medium mb-1 text-gray-600"),
                    Select(
                        Option("High Quality (Recommended)", value="high", selected=True),
                        Option("Standard Quality", value="standard"),
                        cls="w-full p-2 border border-gray-300 rounded-md text-sm focus:ring-1 focus:ring-blue-500 focus:border-blue-500",
                        id="quality-selector"
                    ),
                    cls="mb-4"
                ),
                Div(
                    Label("Audio Format:", cls="block text-xs font-medium mb-1 text-gray-600"),
                    Select(
                        Option("MP3 (Compatible)", value="mp3", selected=True),
                        Option("WAV (Uncompressed)", value="wav"),
                        cls="w-full p-2 border border-gray-300 rounded-md text-sm focus:ring-1 focus:ring-blue-500 focus:border-blue-500",
                        id="format-selector"
                    ),
                    cls="mb-4"
                ),
                Div(
                    Label("Volume Level:", cls="block text-xs font-medium mb-1 text-gray-600"),
                    Div(
                        Input(
                            type="range",
                            min="0",
                            max="2",
                            step="0.1",
                            value=str(DEFAULT_VOLUME),
                            cls="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider",
                            id="volume-slider",
                            oninput="updateVolumeDisplay(this.value)"
                        ),
                        Div(
                            Span("0%", cls="text-xs text-gray-500"),
                            Span(DEFAULT_VOLUME_DISPLAY, cls="text-xs font-medium text-blue-600", id="volume-display"),
                            Span("200%", cls="text-xs text-gray-500"),
                            cls="flex justify-between items-center mt-1"
                        ),
                        cls="mb-4"
                    )
                ),
                cls="p-4 bg-gray-50 rounded-lg border"
            ),
            cls="mb-6"
        ),
        
        # Help Section
        Div(
            Label("Quick Help:", cls="block text-sm font-medium mb-3 text-gray-700"),
            Div(
                P("• Select your preferred TTS engine above", cls="text-xs text-gray-600 mb-2"),
                P("• Choose a voice that matches your content style", cls="text-xs text-gray-600 mb-2"),
                P("• Adjust speech speed for comfortable listening", cls="text-xs text-gray-600 mb-2"),
                P("• Use MiniMax for custom voices and advanced features", cls="text-xs text-gray-600"),
                cls="p-4 bg-blue-50 rounded-lg border border-blue-200"
            ),
            cls="mb-4"
        ),
        
        cls="tab-content active",
        id="voice-tab",
        **{"data-tab-content": "voice"}
    )


def render_api_settings_tab(minimax_creds):
    """
    Renders the API configuration settings tab content.
    
    Args:
        minimax_creds: Dictionary containing MiniMax credentials
        
    Returns:
        Div: API settings tab container
    """
    return Div(
        # MiniMax Credentials Section
        Div(
            # Two-column layout for API credentials
            Div(
                # Left Column - Credentials
                Div(
                    # API Key Input
                    Div(
                        Label("API Key:", cls="block text-sm font-medium mb-1 text-gray-700"),
                        Input(
                            type="password",
                            placeholder="Enter your MiniMax API Key",
                            value="••••••••••" if minimax_creds.get('api_key') else "",
                            cls="w-full p-2 border border-gray-300 rounded-md text-sm focus:ring-1 focus:ring-blue-500 focus:border-blue-500",
                            id="minimax-api-key",
                            onchange="validateMinimaxCredentials()"
                        ),
                        cls="mb-3"
                    ),
                    
                    # Group ID Input
                    Div(
                        Label("Group ID:", cls="block text-sm font-medium mb-1 text-gray-700"),
                        Input(
                            type="text",
                            placeholder="Enter your MiniMax Group ID",
                            value=minimax_creds.get('group_id', ''),
                            cls="w-full p-2 border border-gray-300 rounded-md text-sm focus:ring-1 focus:ring-blue-500 focus:border-blue-500",
                            id="minimax-group-id",
                            onchange="validateMinimaxCredentials()"
                        ),
                        cls="mb-3"
                    ),
                    
                    # Status Display
                    Div(
                        Span("Status: ", cls="text-sm font-medium text-gray-700"),
                        Span("Not configured", cls="text-sm text-gray-500"),
                        id="minimax-status",
                        cls="text-sm p-2 bg-gray-50 rounded border"
                    ),
                    
                    cls="flex-1 mr-4"
                ),
                
                # Right Column - Configuration
                Div(
                    # Model Selection
                    Div(
                        Label("Model:", cls="block text-sm font-medium mb-1 text-gray-700"),
                        Select(
                            Option("Speech-02 Turbo (Recommended)", value="speech-2.5-turbo-preview", 
                                   selected=(minimax_creds.get('model', 'speech-2.5-turbo-preview') == 'speech-2.5-turbo-preview')),
                            Option("Speech-02 HD (High Quality)", value="speech-02-hd",
                                   selected=(minimax_creds.get('model', 'speech-2.5-turbo-preview') == 'speech-02-hd')),
                            Option("Speech-01 Turbo (Legacy)", value="speech-01-turbo",
                                   selected=(minimax_creds.get('model', 'speech-2.5-turbo-preview') == 'speech-01-turbo')),
                            Option("Speech-01 HD (Legacy)", value="speech-01-hd",
                                   selected=(minimax_creds.get('model', 'speech-2.5-turbo-preview') == 'speech-01-hd')),
                            cls="w-full p-2 border border-gray-300 rounded-md text-sm focus:ring-1 focus:ring-blue-500 focus:border-blue-500",
                            id="minimax-model",
                            onchange="validateMinimaxCredentials()"
                        ),
                        cls="mb-3"
                    ),
                    
                    # Chunk Size Configuration
                    Div(
                        Label("Chunk Size (words):", cls="block text-sm font-medium mb-1 text-gray-700"),
                        Div(
                            Input(
                                type="range",
                                min="50",
                                max="300",
                                value=str(minimax_creds.get('chunk_size', 120)),
                                cls="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider",
                                id="minimax-chunk-size",
                                oninput="updateChunkSizeDisplay(this.value)"
                            ),
                            Div(
                                Span("50", cls="text-xs text-gray-500"),
                                Span(f"{minimax_creds.get('chunk_size', 120)} words (~{int(minimax_creds.get('chunk_size', 120) * 1.67)} chars)", cls="text-sm font-medium text-blue-600", id="chunk-size-display"),
                                Span("300", cls="text-xs text-gray-500"),
                                cls="flex justify-between items-center mt-1"
                            ),
                            cls="mb-1"
                        ),
                        P("Estimated chunks: ", 
                          Span("1", id="chunk-estimate", cls="font-medium text-orange-600"),
                          cls="text-xs text-gray-500"),
                        cls="mb-3"
                    ),
                    
                    cls="flex-1"
                ),
                
                cls="flex gap-4 mb-4"
            ),
            
            # Custom Voice Configuration (Full Width)
            Div(
                Label("Custom Voice ID (Optional):", cls="block text-sm font-medium mb-2 text-gray-700"),
                Input(
                    type="text",
                    placeholder="e.g., moss_audio_4dc076ac-da6d-11ef-bd8d-f27a76fcd434",
                    value=minimax_creds.get('custom_voice_id', ''),
                    cls="w-full p-2 border border-gray-300 rounded-md text-sm font-mono focus:ring-1 focus:ring-blue-500 focus:border-blue-500",
                    id="minimax-custom-voice",
                    onchange="validateMinimaxCredentials()"
                ),
                P("Leave empty to use standard voices. Custom voices override the voice selector above.", 
                  cls="text-xs text-gray-500 mt-2"),
                cls="mb-6"
            ),
            
            # Action Buttons
            Div(
                Button(
                    "💾 Save Credentials",
                    onclick="saveMinimaxCredentials()",
                    cls="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium mr-2 transition-colors",
                    id="save-credentials-btn"
                ),
                Button(
                    "🗑️ Clear All",
                    onclick="clearMinimaxCredentials()",
                    cls="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors",
                    id="clear-credentials-btn"
                ),
                cls="flex items-center"
            ),
            
            cls="p-4 bg-gray-50 rounded-lg border"
        ),
        
        cls="tab-content",
        id="api-tab",
        **{"data-tab-content": "api"},
        style="display: none;"
    )