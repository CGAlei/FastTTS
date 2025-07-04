# FastTTS MiniMax Integration Setup Guide

## Overview

FastTTS now supports multiple TTS engines:
- **Microsoft Edge TTS** (Default, fully functional)
- **MiniMax Hailuo TTS** (Advanced, requires API credentials and MFA)

## 🚀 Quick Start

### Option 1: Use Edge TTS Only (Recommended for most users)
No additional setup required. FastTTS works out of the box with Microsoft Edge TTS.

### Option 2: Add MiniMax Hailuo TTS Support

#### Step 1: Configure MiniMax API Credentials

1. **Get API Credentials:**
   - Visit [MiniMax Console](https://www.minimax.io/)
   - Sign up and get your API key and Group ID

2. **Configure Through Settings UI (Recommended):**
   - Open FastTTS application
   - Click the ⚙️ settings button in the top controls bar
   - Scroll to "MiniMax API Configuration" section
   - Enter your API Key and Group ID
   - Click "Save Credentials"
   - Credentials are automatically saved to `.env` file

3. **Alternative: Manual Configuration:**
   ```bash
   # Create .env file from template
   cp .env.example .env
   # Edit .env file with your credentials
   ```

#### Step 2: Install Montreal Forced Aligner (Optional but Recommended)

MFA provides word-level timing for MiniMax TTS. Without it, FastTTS falls back to duration-based estimation.

```bash
# Install MFA using conda (recommended)
conda install -c conda-forge montreal-forced-aligner

# OR using pip (alternative)
pip install montreal-forced-aligner

# Verify installation
mfa version
```

#### Step 3: Download Chinese Models (Optional)

```bash
# Download Chinese acoustic model and dictionary
mfa model download acoustic mandarin_china_mfa
mfa model download dictionary mandarin_china_mfa

# Verify models
mfa model list acoustic
mfa model list dictionary
```

## 🎛️ Usage

### Web Interface

1. **Open Settings:** Click the ⚙️ settings button in the top controls bar
2. **Select TTS Engine:** Choose between "Microsoft Edge TTS" or "MiniMax Hailuo TTS"
3. **Select Voice:** Available voices update automatically based on selected engine
4. **Adjust Speed:** 0.5× to 2.0× speech speed control
5. **Generate TTS:** Click 🔊 to generate speech with selected engine

### Engine Comparison

| Feature | Edge TTS | MiniMax Hailuo |
|---------|----------|----------------|
| **Setup** | ✅ No setup required | ⚙️ Requires API credentials |
| **Quality** | 🟢 High quality | 🔵 Premium quality |
| **Speed** | ⚡ Fast generation | 🐌 Slower (forced alignment) |
| **Voices** | 8 Chinese voices | 6 Chinese voices |
| **Word Timing** | ✅ Native word boundaries | 🔧 MFA-generated |
| **Cost** | 🆓 Free | 💰 API usage costs |
| **Offline** | ❌ Requires internet | ❌ Requires internet |

### TTS Engine Status Checking

FastTTS provides endpoints to check engine and MFA status:

```bash
# Check TTS engines info
curl http://localhost:5001/tts-engines-info

# Check MFA installation status
curl http://localhost:5001/mfa-status

# Download MFA models (if needed)
curl -X POST http://localhost:5001/mfa-setup
```

## 🔧 Technical Architecture

### Engine Selection Flow

1. **Settings UI:** User selects TTS engine in settings modal
2. **Voice Update:** Available voices dynamically update for selected engine
3. **Form Submission:** HTMX includes `tts_engine` parameter in TTS requests
4. **Backend Processing:** `TTSFactory.create_engine(engine_type)` instantiates appropriate engine
5. **Audio Generation:** Engine-specific `generate_speech()` method called
6. **Word Alignment:** MFA processing (Hailuo) or native timing (Edge)

### File Structure

```
/mnt/d/FastTTS/
├── tts/                      # TTS engines module
│   ├── __init__.py
│   ├── base_tts.py          # Abstract base class
│   ├── edge_tts_engine.py   # Microsoft Edge TTS
│   ├── minimax_tts_engine.py # MiniMax Hailuo TTS
│   └── tts_factory.py       # Engine factory
├── alignment/               # Forced alignment module
│   ├── __init__.py
│   └── mfa_aligner.py      # Montreal Forced Aligner
├── main.py                 # Updated with multi-engine support
├── requirements.txt        # Updated dependencies
└── .env.example           # Environment configuration template
```

### API Endpoints

- `POST /generate-custom-tts` - Generate TTS with engine selection
- `GET /tts-engines-info` - Get available engines and voices
- `GET /mfa-status` - Check MFA installation status
- `POST /mfa-setup` - Download MFA models

## 🐛 Troubleshooting

### Common Issues

#### 1. MiniMax TTS Not Working
```
Error: "MiniMax API credentials not configured"
```
**Solution:** Set `MINIMAX_API_KEY` and `MINIMAX_GROUP_ID` environment variables.

#### 2. MFA Alignment Fails
```
Warning: "MFA alignment failed, falling back to duration estimation"
```
**Solutions:**
- Install MFA: `conda install -c conda-forge montreal-forced-aligner`
- Download models: `mfa model download acoustic mandarin_china_mfa`
- Check installation: `mfa version`

#### 3. Voice Options Don't Update
**Solution:** Refresh the page or check browser console for JavaScript errors.

#### 4. Slow TTS Generation with MiniMax
**Expected Behavior:** MiniMax + MFA processing takes longer (5-15 seconds) due to forced alignment.

### Debug Information

Check browser console for debug messages:
- `🔧 TTS Engine changed to: hailuo`
- `🚀 Generating TTS with MiniMax Hailuo`
- `🔄 Running MFA alignment for word-level timing...`
- `⚠️ MFA not available, falling back to duration estimation`

## 📊 Performance Optimization

### Edge TTS (Recommended for most users)
- ✅ Fast generation (2-5 seconds)
- ✅ Reliable word-level timing
- ✅ No external dependencies
- ✅ Free usage

### MiniMax Hailuo (Advanced users)
- 🔵 Premium audio quality
- ⚙️ Requires API setup and costs
- 🐌 Slower due to forced alignment
- 🔧 Optional MFA dependency

## 🚀 Future Enhancements

Planned improvements for the multi-engine TTS system:

1. **Additional Engines:** Support for more TTS providers
2. **Voice Cloning:** Custom voice training capabilities
3. **Batch Processing:** Multiple text segments at once
4. **Caching:** Audio and alignment result caching
5. **Offline Mode:** Local TTS engine support

## 📄 Environment Variables Reference

Create a `.env` file or set these environment variables:

```bash
# MiniMax TTS Configuration
MINIMAX_API_KEY=your_api_key_here
MINIMAX_GROUP_ID=your_group_id_here

# Application Configuration
DEFAULT_TTS_ENGINE=edge          # Options: "edge", "hailuo"
DEBUG=false                      # Enable debug logging
```

## 🆘 Support

If you encounter issues:

1. **Check Status Endpoints:** Visit `/tts-engines-info` and `/mfa-status`
2. **Review Logs:** Check console output for error messages
3. **Verify Setup:** Ensure environment variables are set correctly
4. **Test Basic Functionality:** Try Edge TTS first, then add MiniMax

The FastTTS application gracefully handles missing dependencies and falls back to working alternatives, ensuring a robust user experience regardless of configuration complexity.