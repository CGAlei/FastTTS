#!/bin/bash

# FastTTS with MFA - Linux Startup Script
# This script deactivates Python venv and activates the MFA conda environment

echo "🚀 Starting FastTTS with MFA Integration..."
echo "📁 Working directory: /home/alex/AI_Project/FastTTS"

# Clear any existing Python virtual environment
echo "🧹 Clearing Python venv..."
unset VIRTUAL_ENV
unset PYTHONHOME
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin"

# Navigate to FastTTS directory
cd /home/alex/AI_Project/FastTTS || {
    echo "❌ Error: Cannot find FastTTS directory at /home/alex/AI_Project/FastTTS"
    echo "   Please check the path and try again."
    exit 1
}

# Source conda
echo "🔧 Initializing conda..."
source $HOME/miniconda3/etc/profile.d/conda.sh || {
    echo "❌ Error: Cannot initialize conda"
    echo "   Please make sure Miniconda is installed properly."
    exit 1
}

# Activate MFA environment
echo "🎯 Activating fasttts-mfa environment..."
conda activate fasttts-mfa || {
    echo "❌ Error: Cannot activate fasttts-mfa environment"
    echo "   Please run: conda env create -f environment.yml"
    exit 1
}

# Verify MFA is available
echo "🧪 Testing MFA availability..."
python -c "
import sys
sys.path.insert(0, '/home/alex/AI_Project/FastTTS')
from alignment.mfa_aligner import MFAAligner
aligner = MFAAligner()
if aligner.is_available:
    print('✅ MFA is ready!')
else:
    print('⚠️  MFA not available - will use fallback timing')
"

# Start FastTTS
echo "🌟 Starting FastTTS application..."
echo "   Access at: http://localhost:5001"
echo "   Press Ctrl+C to stop"
echo ""

python main.py

echo ""
echo "👋 FastTTS stopped. Environment still active."
echo "   Type 'conda deactivate' to exit MFA environment"