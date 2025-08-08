# FastTTS Audio Session Creator - `ftts-session` Command

A CLI tool that converts audio files into complete FastTTS sessions with MFA word-level alignment and timing data.

## What It Does

The `ftts-session` command takes any audio file and creates a FastTTS session folder containing:
- **audio.mp3** - The processed audio file  
- **metadata.json** - Session metadata (text, date, word count)
- **timestamps.json** - Word-level timing data for karaoke functionality

## Quick Start

```bash
# Basic usage - creates ./audio/ folder with session files
./ftts-session audio.wav

# Specify output directory
./ftts-session audio.wav --output /path/to/sessions/

# Verbose output for debugging
./ftts-session audio.wav --verbose
```

## How It Works

1. **Audio Processing**: Loads and validates the input audio file
2. **Text Input**: Prompts you to enter the Chinese text that corresponds to the audio
3. **MFA Alignment**: Uses Montreal Forced Alignment for precise word-level timing
4. **Session Creation**: Creates a folder with all FastTTS session files

## Features

### ✅ **Full MFA Integration**
- Uses the same MFA pipeline as FastTTS web interface
- Automatic model downloading if missing
- Falls back to Jieba segmentation if MFA unavailable

### ✅ **Smart Audio Handling**  
- Supports multiple formats (wav, mp3, m4a, aac, ogg, flac)
- Automatic format conversion for MFA compatibility
- Preserves original audio quality

### ✅ **Error Handling**
- Graceful fallbacks for missing dependencies
- Clear error messages and troubleshooting tips
- Validates input files before processing

### ✅ **FastTTS Compatibility**
- Creates sessions identical to web interface
- Same folder structure and file formats
- Integrates with existing session management

## Prerequisites

- FastTTS conda environment (`fasttts-mfa`) must be activated
- MFA models will be downloaded automatically if missing
- `ffmpeg` recommended for audio format conversion

## Usage Examples

### Create Session from Audio
```bash
./ftts-session lecture.wav
```
This creates a `lecture/` folder with session files.

### Specify Output Location
```bash
./ftts-session audio.wav --output ~/FastTTS/sessions/
```
Creates the session in your specified directory.

### Debug Processing
```bash
./ftts-session audio.wav --verbose
```
Shows detailed information about MFA alignment and processing steps.

## Session Folder Structure

After running `./ftts-session audio.wav`, you get:

```
audio/
├── audio.mp3          # Processed audio file
├── metadata.json      # Session info (text, date, word count)
└── timestamps.json    # Word-level timing for karaoke
```

These files are compatible with the FastTTS web interface and can be loaded directly.

## Installation for Global Access

To use `ftts-session` from anywhere, add the FastTTS directory to your PATH:

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="/home/alex/AI_Project/FastTTS:$PATH"

# Reload shell
source ~/.bashrc
```

Then you can use `ftts-session audio.wav` from any directory.

## Troubleshooting

### MFA Not Available
If MFA is not installed or models are missing:
- The tool automatically downloads required models
- Falls back to Jieba segmentation for basic timing
- Check `fasttts --test` for full system verification

### Audio Format Issues  
If audio conversion fails:
- Install `ffmpeg` for format conversion support
- Try converting audio to WAV format manually first
- Check that the audio file is not corrupted

### Text Input Tips
For best alignment results:
- Use the exact text that was spoken in the audio
- Include Chinese punctuation marks
- Copy text from your source material when possible

## Integration with FastTTS

Sessions created with `ftts-session` are fully compatible with FastTTS:
- Load sessions in the web interface
- Access word-level timing and karaoke features  
- Organize sessions in folders
- Export and share session data

The `ftts-session` command essentially provides the FastTTS workflow as a standalone CLI tool.