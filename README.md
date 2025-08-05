# 🎤 FastTTS - Chinese Text-to-Speech with AI Vocabulary Learning

<div align="center">

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastHTML](https://img.shields.io/badge/FastHTML-0.6.9+-green.svg)](https://fastht.ml/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Linux Support](https://img.shields.io/badge/Linux-Supported-success.svg)](https://github.com/CGAlei/FastTTS/blob/main/INSTALLATION.md)

**Advanced Chinese TTS with karaoke-style word highlighting and AI-powered vocabulary learning**

[🚀 Quick Start](#-quick-start) • [✨ Features](#-features) • [📖 Installation](#-installation) • [🎯 Usage](#-usage) • [🤝 Contributing](#-contributing)

</div>

---

## 🌟 **What is FastTTS?**

FastTTS transforms Chinese language learning through **intelligent text-to-speech** with **real-time word highlighting** and **AI-powered vocabulary management**. Perfect for students, teachers, and language enthusiasts who want to master Chinese pronunciation and vocabulary.

### **🎯 Core Features:**

🎤 **Multiple TTS Engines**  
- **Edge TTS**: 50+ free Chinese voices  
- **MiniMax**: Premium AI voices with custom options  

🎵 **Karaoke-Style Learning**  
- Real-time word highlighting during playback  
- Click words for instant pronunciation practice  
- Montreal Forced Alignment for precise timing  

🧠 **AI Vocabulary Assistant**  
- Right-click unknown words for instant AI definitions  
- Automatic vocabulary database building  
- Smart word rating and progress tracking  

📁 **Session Management**  
- Save and organize TTS sessions by topic  
- Folder-based organization (Culture, Politics, Philosophy, etc.)  
- Export audio and timing data  

🎨 **Modern Web Interface**  
- Responsive design for desktop and mobile  
- Dark/Light theme support  
- Touch-friendly controls

---

## 🚀 **Quick Start**

### **1. One-Command Installation (Recommended)**
```bash
# Clone the repository
git clone https://github.com/CGAlei/FastTTS.git
cd FastTTS

# Create conda environment with all dependencies
conda env create -f environment.yml -n fasttts-mfa
conda activate fasttts-mfa

# Launch FastTTS
./start_fasttts_mfa.sh
```

### **2. Open in Browser**
🌐 **http://localhost:5001**

### **3. Start Learning!**
1. **Paste Chinese text** in the input area
2. **Select voice** (Edge TTS voices are free)
3. **Generate TTS** and enjoy karaoke-style learning
4. **Right-click words** for AI definitions

---

## ✨ **Features Overview**

### **🎤 Text-to-Speech Engines**

| Engine | Voices | Quality | Cost | Features |
|--------|--------|---------|------|----------|
| **Edge TTS** | 50+ Chinese | High | Free | Multiple regional accents |
| **MiniMax** | Premium AI | Ultra-High | Paid | Custom voices, emotions |

### **🎵 Advanced Audio Features**

- **Montreal Forced Alignment (MFA)**: Precise word-level timing
- **Real-time highlighting**: Words highlight as they're spoken
- **Audio controls**: Speed, volume, pause/resume
- **Export capabilities**: Save audio as MP3 with timing data

### **🧠 AI Vocabulary Learning**

- **Instant definitions**: Right-click any word for AI explanation
- **Multi-language support**: Chinese, English, Spanish translations
- **Progress tracking**: Rate words 1-5 stars, track learning progress
- **Smart database**: Automatic vocabulary building and management
- **Contextual examples**: Real usage examples for better understanding

### **📁 Session Organization**

- **Topic-based folders**: Culture, Politics, Sports, Philosophy, etc.
- **Session metadata**: Date, word count, favorite marking
- **Search and filter**: Find sessions by content or metadata
- **Backup and sync**: Export/import sessions and vocabulary

### **🎨 User Experience**

- **Responsive design**: Works on desktop, tablet, and mobile
- **Theme support**: Dark and light modes
- **Keyboard shortcuts**: Efficient navigation and controls
- **Accessibility**: Screen reader support, keyboard navigation

---

## 📖 **Installation**

FastTTS supports multiple installation methods for different Linux distributions:

### **📋 System Requirements**
- **OS**: Ubuntu 20.04+, Debian 11+, CentOS 8+, Arch Linux
- **RAM**: 4GB minimum, 8GB recommended  
- **Storage**: 2GB free space (3GB with MFA models)
- **CPU**: x64 architecture (Intel/AMD)

### **🔥 Method 1: Conda (Recommended)**
```bash
# Install Miniconda (if not already installed)
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3
source $HOME/miniconda3/etc/profile.d/conda.sh

# Clone and setup FastTTS
git clone https://github.com/CGAlei/FastTTS.git
cd FastTTS
conda env create -f environment.yml -n fasttts-mfa
conda activate fasttts-mfa

# Launch application
./start_fasttts_mfa.sh
```

### **⚡ Method 2: Pip + System Dependencies**
```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt update && sudo apt install -y python3 python3-pip ffmpeg sox

# Clone and setup
git clone https://github.com/CGAlei/FastTTS.git
cd FastTTS
python3 -m venv fasttts-env
source fasttts-env/bin/activate
pip install -r requirements.txt

# Launch application
python main.py
```

### **🐳 Method 3: Docker**
```bash
# Run FastTTS container
docker run -d \
  --name fasttts \
  -p 5001:5001 \
  -v fasttts-data:/app/data \
  cgalei/fasttts:latest
```

**📚 Detailed installation instructions for all Linux distributions: [INSTALLATION.md](INSTALLATION.md)**

---

## 🎯 **Usage**

### **Basic TTS Generation**
1. **Enter Chinese text** in the main input area
2. **Select TTS engine**: Edge TTS (free) or MiniMax (premium)
3. **Choose voice**: Browse available voices by region/style
4. **Adjust settings**: Speed (0.5x-2.0x), volume, pitch
5. **Generate**: Click the TTS button to create audio

### **Karaoke Learning Mode**
1. **Generate TTS** as above
2. **Play audio**: Words highlight in real-time as they're spoken
3. **Click words**: Hear individual word pronunciation
4. **Interactive learning**: Practice problem words repeatedly

### **AI Vocabulary Assistant**
1. **Right-click any word** in the text display
2. **Get instant definitions**: AI generates comprehensive explanations
3. **Save to database**: Words automatically added to vocabulary
4. **Rate and track**: Mark difficulty and track learning progress
5. **Review vocabulary**: Browse saved words with search and filter

### **Session Management**
1. **Save sessions**: Click save after generating TTS
2. **Organize by topic**: Choose folder (Culture, Sports, etc.)
3. **Browse history**: Left sidebar shows all saved sessions
4. **Search and filter**: Find sessions by text content or favorites

### **Configuration**
Create `.env` file for advanced settings:
```bash
# TTS Engine API Keys (Optional)
MINIMAX_API_KEY=your_api_key
OPENAI_API_KEY=your_openai_key

# Default Settings
FASTTTS_DEFAULT_VOICE=zh-CN-XiaoxiaoNeural
FASTTTS_DEFAULT_ENGINE=edge
FASTTTS_LOG_LEVEL=INFO
```

---

## 🏗️ **Architecture**

### **Technology Stack**
- **Backend**: Python 3.10+ with FastHTML framework
- **Frontend**: Modern HTML5 + HTMX for reactive UI
- **TTS Engines**: Edge TTS, MiniMax API integration
- **Audio Processing**: FFmpeg, Montreal Forced Alignment (MFA)
- **AI Integration**: OpenAI API for vocabulary definitions
- **Database**: SQLite for vocabulary and session management

### **Project Structure**
```
FastTTS/
├── main.py                 # Main application entry point
├── components/             # UI components and layout
├── tts/                   # TTS engine implementations
│   ├── edge_tts_engine.py # Edge TTS integration
│   └── minimax_tts_engine.py # MiniMax TTS integration
├── alignment/             # Montreal Forced Alignment
├── utils/                 # Utilities and helpers
├── static/                # CSS, JavaScript, assets
├── sessions/              # User TTS sessions (auto-created)
├── db/                    # Vocabulary database (auto-created)
└── logs/                  # Application logs (auto-created)
```

---

## 🤝 **Contributing**

We welcome contributions! Here's how to get started:

### **🔧 Development Setup**
```bash
# Clone and setup development environment
git clone https://github.com/CGAlei/FastTTS.git
cd FastTTS
conda env create -f environment.yml -n fasttts-dev
conda activate fasttts-dev

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Start development server with auto-reload
python main.py --debug
```

### **📝 Contribution Guidelines**
1. **Fork** the repository
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Write tests** for new functionality
4. **Follow code style**: Black formatting, type hints
5. **Submit pull request** with detailed description

### **🐛 Bug Reports**
- Use GitHub Issues with detailed reproduction steps
- Include system info, logs, and error messages
- Check existing issues before creating new ones

### **💡 Feature Requests**
- Describe the use case and expected behavior
- Consider implementation complexity and user impact
- Participate in discussion and feedback

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

- **Montreal Forced Alignment (MFA)** - Precise word-level timing
- **Microsoft Edge TTS** - High-quality free Chinese voices  
- **MiniMax** - Premium AI voice generation
- **FastHTML** - Modern Python web framework
- **OpenAI** - AI-powered vocabulary definitions

---

## 📞 **Support**

### **Getting Help**
- **📖 Wiki**: [Comprehensive documentation](https://github.com/CGAlei/FastTTS/wiki)
- **🐛 Issues**: [Bug reports and feature requests](https://github.com/CGAlei/FastTTS/issues)
- **💬 Discussions**: [Community Q&A](https://github.com/CGAlei/FastTTS/discussions)
- **📧 Email**: serinoac@gmail.com

### **Stay Updated**
- ⭐ **Star this repository** to follow updates
- 👀 **Watch releases** for new features and bug fixes
- 🐦 **Follow development** on social media

---

<div align="center">

**🎉 Ready to revolutionize your Chinese language learning?**

[🚀 **Get Started Now**](https://github.com/CGAlei/FastTTS/blob/main/INSTALLATION.md) • [📖 **Read the Docs**](https://github.com/CGAlei/FastTTS/wiki) • [💬 **Join Discussion**](https://github.com/CGAlei/FastTTS/discussions)

---

**Made with ❤️ by [CGAlei](https://github.com/CGAlei) for the Chinese language learning community**

</div>