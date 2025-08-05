#!/bin/bash

# FastTTS Launcher Script
# Auto-detects project location and launches the application

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 FastTTS Launcher${NC}"
echo "=================================="

# Get the directory where this script is actually located (resolve symlinks)
SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
echo -e "${BLUE}📁 Project directory: ${SCRIPT_DIR}${NC}"

# Navigate to project directory
cd "$SCRIPT_DIR"

# Check for conda installation
if ! command -v conda &> /dev/null; then
    echo -e "${RED}❌ Error: conda not found in PATH${NC}"
    echo "Please install Miniconda/Anaconda or add it to your PATH"
    exit 1
fi

# Initialize conda for bash
echo -e "${YELLOW}🔧 Initializing conda...${NC}"

# Source conda profile script for proper initialization
CONDA_BASE=$(conda info --base 2>/dev/null)
if [ -n "$CONDA_BASE" ] && [ -f "$CONDA_BASE/etc/profile.d/conda.sh" ]; then
    source "$CONDA_BASE/etc/profile.d/conda.sh"
elif [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/miniconda3/etc/profile.d/conda.sh"
elif [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/anaconda3/etc/profile.d/conda.sh"
elif [ -f "/opt/conda/etc/profile.d/conda.sh" ]; then
    source "/opt/conda/etc/profile.d/conda.sh"
else
    echo -e "${YELLOW}⚠️  Falling back to conda hook...${NC}"
    eval "$(conda shell.bash hook)"
fi

# Check if fast_tts environment exists
if ! conda env list | grep -q "fast_tts"; then
    echo -e "${RED}❌ Error: conda environment 'fast_tts' not found${NC}"
    echo "Please create the environment first:"
    echo "  conda env create -f environment.yml -n fast_tts"
    exit 1
fi

# Activate the environment
echo -e "${YELLOW}🔄 Activating fast_tts environment...${NC}"
conda activate fast_tts

# Verify conda activation worked
if [[ "$CONDA_DEFAULT_ENV" != "fast_tts" ]]; then
    echo -e "${RED}❌ Error: Failed to activate conda environment 'fast_tts'${NC}"
    echo "Current environment: $CONDA_DEFAULT_ENV"
    echo "Try running the following manually:"
    echo "  conda activate fast_tts"
    echo "  python main.py"
    exit 1
fi

echo -e "${GREEN}✅ Environment activated: $CONDA_DEFAULT_ENV${NC}"

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo -e "${RED}❌ Error: main.py not found in ${SCRIPT_DIR}${NC}"
    exit 1
fi


# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down FastTTS...${NC}"
    if [ ! -z "$PYTHON_PID" ]; then
        kill $PYTHON_PID 2>/dev/null || true
        echo -e "${GREEN}✅ FastTTS stopped${NC}"
    fi
}

# Set trap to cleanup on script exit
trap cleanup EXIT INT TERM

# Start the FastTTS application
echo -e "${YELLOW}🌟 Starting FastTTS application...${NC}"
python main.py &
PYTHON_PID=$!

# Wait for the server to start and verify it's responding
echo -e "${YELLOW}⏳ Waiting for server to start...${NC}"
sleep 3

# Check if the server is running
if ! ps -p $PYTHON_PID > /dev/null; then
    echo -e "${RED}❌ Error: FastTTS failed to start${NC}"
    exit 1
fi

# Verify server is responding on the expected port
echo -e "${YELLOW}🔍 Verifying server is responding...${NC}"
for i in {1..10}; do
    if curl -s http://127.0.0.1:5001 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Server is responding on port 5001${NC}"
        break
    fi
    if [ $i -eq 10 ]; then
        echo -e "${YELLOW}⚠️  Server may still be starting up...${NC}"
        break
    fi
    sleep 1
done

# Server is ready for Web Apps
echo -e "${BLUE}🌐 FastTTS server ready at: http://127.0.0.1:5001${NC}"
echo -e "${YELLOW}💡 You can now create a Web App pointing to this address${NC}"

echo -e "${GREEN}✅ FastTTS is running!${NC}"
echo -e "${BLUE}🌐 Web interface: http://127.0.0.1:5001${NC}"
echo -e "${YELLOW}💡 Press Ctrl+C to stop the application${NC}"
echo "=================================="

# Keep the script running and wait for the Python process
wait $PYTHON_PID