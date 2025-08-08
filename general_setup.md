# FastTTS with MFA - Complete Setup Guide

## ⚠️ CRITICAL: This guide includes ALL required dependencies that were previously missing!

FastTTS is a Chinese language learning application with Text-to-Speech (TTS) and Montreal Forced Alignment (MFA) for word-level audio synchronization.

## Prerequisites

- **Linux or macOS** (Windows may work but not tested)
- **Conda/Miniconda** installed
- **Internet connection** for downloading models

## Step 1: Create Conda Environment

```bash
# Navigate to the FastTTS directory
cd /path/to/FastTTS

# Create the conda environment (this takes 10-15 minutes)
conda env create -f environment.yml

# Activate the environment
conda activate fasttts-mfa
```

## Step 2: ⚠️ CRITICAL - Install Missing Chinese Tokenization Dependencies

**These packages are REQUIRED for MFA Chinese alignment and were previously missing:**

```bash
# Install Chinese tokenization support (REQUIRED for MFA)
pip install spacy-pkuseg dragonmapper hanziconv

# Install additional missing requirements
pip install -r requirements.txt
```

### What These Packages Do:
- **spacy-pkuseg**: Chinese word segmentation for MFA
- **dragonmapper**: Chinese character conversion utilities  
- **hanziconv**: Traditional/Simplified Chinese conversion
- **Without these, MFA alignment will fail with ImportError**

## Step 3: Download MFA Models

```bash
# Download Mandarin acoustic model
mfa model download acoustic mandarin_mfa

# Download Mandarin dictionary
mfa model download dictionary mandarin_mfa
```

## Step 4: Verify Installation

Run this complete verification test:

```bash
python -c "
import sys
sys.path.insert(0, '.')

# Test 1: Basic imports
print('Testing imports...')
from alignment.mfa_aligner import MFAAligner
import edge_tts
import jieba
print('✅ All imports successful')

# Test 2: MFA availability
aligner = MFAAligner()
print(f'✅ MFA available: {aligner.is_available}')
models = aligner._check_models_available()
print(f'✅ Models status: {models}')

# Test 3: Chinese tokenization (the critical missing piece)
try:
    import spacy_pkuseg
    import dragonmapper  
    import hanziconv
    print('✅ Chinese tokenization packages installed')
except ImportError as e:
    print(f'❌ Missing Chinese tokenization: {e}')
    exit(1)

# Test 4: Jieba segmentation
words = list(jieba.cut('你好世界'))
print(f'✅ Jieba test: {words}')

print('🎉 All verification tests passed!')
"
```

## Step 5: Launch the Application

### Option A: Using the Launch Script
```bash
# Make script executable
chmod +x start_fasttts_mfa.sh

# Launch application
./start_fasttts_mfa.sh
```

### Option B: Manual Launch
```bash
# Ensure environment is activated
conda activate fasttts-mfa

# Start the application
python main.py
```

## Step 6: Install Global Launcher (Optional but Recommended)

For maximum convenience, install the global launcher to run FastTTS from anywhere:

```bash
# Make the launcher executable
chmod +x fasttts

# Install to user bin directory
mkdir -p $HOME/.local/bin
cp fasttts $HOME/.local/bin/

# Add to PATH (add this line to your ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"

# Reload your shell or run:
source ~/.bashrc
```

### Alternative: System-wide Installation (requires sudo)
```bash
sudo cp fasttts /usr/local/bin/
```

## Step 7: Launch FastTTS

### Option A: Using Global Launcher (Recommended)
```bash
# Run from anywhere on your system
fasttts
```

### Option B: Using the Launch Script
```bash
# Navigate to FastTTS directory
cd /path/to/FastTTS

# Make script executable
chmod +x start_fasttts_mfa.sh

# Launch application
./start_fasttts_mfa.sh
```

### Option C: Manual Launch
```bash
# Ensure environment is activated
conda activate fasttts-mfa

# Navigate to FastTTS directory
cd /path/to/FastTTS

# Start the application
python main.py
```

## Step 8: Access the Application

Open your browser and navigate to:
```
http://localhost:5001
```

## Dependencies Overview

### Conda Dependencies (from environment.yml):
- `python=3.10`
- `montreal-forced-aligner=3.2.3`
- `kaldi`, `openfst` (MFA backends)
- `ffmpeg`, `sox` (audio processing)
- `pynini` (Chinese G2P processing)

### Python Dependencies (from requirements.txt):
- `python-fasthtml>=0.6.9` (web framework)
- `edge-tts>=6.1.9` (TTS engine)
- `pypinyin>=0.50.0` (Chinese pronunciation)
- `jieba>=0.42.1` (Chinese word segmentation)
- `openai>=1.0.0` (LLM integration)

### ⚠️ CRITICAL Chinese Tokenization Dependencies:
- `spacy-pkuseg` (Chinese word segmentation for MFA)
- `dragonmapper` (Chinese character utilities)
- `hanziconv` (Traditional/Simplified conversion)

## Troubleshooting

### Error: "ImportError: Please install Chinese tokenization support"
**Solution:** Run the critical installation step:
```bash
pip install spacy-pkuseg dragonmapper hanziconv
```

### Error: "MFA alignment failed (code 1)"
**Causes:**
1. Missing Chinese tokenization packages (see above)
2. Missing MFA models
3. Audio format issues

**Solutions:**
```bash
# Check MFA models
mfa model list acoustic
mfa model list dictionary

# Reinstall MFA models if missing
mfa model download acoustic mandarin_mfa
mfa model download dictionary mandarin_mfa
```

### Error: "mfa: command not found"
**Solution:** Ensure conda environment is activated:
```bash
conda activate fasttts-mfa
which mfa  # Should show path in fasttts-mfa environment
```

### Error: Audio processing issues
**Solution:** Verify ffmpeg installation:
```bash
ffmpeg -version  # Should show ffmpeg version
```

### Environment Creation Fails
**Solution:** Clean and retry:
```bash
conda env remove -n fasttts-mfa
conda clean -a
conda env create -f environment.yml
```

## Features

- **Chinese TTS**: Generate natural-sounding Chinese speech
- **Word-Level Alignment**: Precise timing for each Chinese character/word
- **Language Learning**: Interactive vocabulary and pronunciation practice
- **Session Management**: Save and replay audio sessions
- **Rating System**: Track learning progress

## Important Notes

1. **First run may be slow** due to model loading and jieba dictionary building
2. **MFA alignment requires the Chinese tokenization packages** - this is not optional
3. **Large audio files may take time** to process through MFA
4. **Environment must be activated** before each use
5. **Internet connection required** for initial setup and TTS

## Architecture

- **Frontend**: FastHTML web framework
- **TTS Engine**: Microsoft Edge TTS
- **Alignment**: Montreal Forced Aligner (MFA)
- **Text Processing**: Jieba + Chinese tokenization packages
- **Database**: SQLite for vocabulary and sessions

---

## Quick Start Checklist

- [ ] Conda environment created and activated
- [ ] ⚠️ Chinese tokenization packages installed (`spacy-pkuseg dragonmapper hanziconv`)
- [ ] MFA models downloaded
- [ ] Verification tests passed
- [ ] Application launches at http://localhost:5001
- [ ] Chinese text alignment working

**If any step fails, refer to the troubleshooting section above.**