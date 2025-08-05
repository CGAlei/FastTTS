# FastTTS Installation Guide for Linux

## Complete setup instructions for Chinese Text-to-Speech with AI vocabulary learning

---

## 🎯 **Quick Overview**

FastTTS supports **three installation methods** for Linux systems:

1. **🔥 Conda Environment (Recommended)** - Complete setup with MFA included
2. **⚡ Pip + System Dependencies** - For advanced users who prefer pip
3. **🐳 Docker Deployment** - Containerized solution, zero conflicts

Choose the method that best fits your system and experience level.

---

## 📋 **System Requirements**

### **Supported Linux Distributions:**
- Ubuntu 20.04+ / Debian 11+
- CentOS 8+ / RHEL 8+ / Rocky Linux 8+
- Arch Linux / Manjaro
- openSUSE Leap 15.3+

### **Hardware Requirements:**
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space (3GB with MFA models)
- **CPU**: x64 architecture (Intel/AMD)

---

## 🔥 **Method 1: Conda Environment (Recommended)**

### **Why Choose Conda?**
✅ **One-command setup** - Everything included  
✅ **MFA pre-compiled** - No build dependencies  
✅ **FFmpeg included** - Audio processing ready  
✅ **Isolated environment** - No system conflicts  

### **Step 1: Install Miniconda**

**Ubuntu/Debian:**
```bash
# Download and install Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3
source $HOME/miniconda3/etc/profile.d/conda.sh
```

**CentOS/RHEL/Rocky Linux:**
```bash
# Download and install Miniconda
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3
source $HOME/miniconda3/etc/profile.d/conda.sh
```

**Arch Linux:**
```bash
# Install from AUR or use official installer
yay -S miniconda3
# OR download official installer as above
```

### **Step 2: Create FastTTS Environment**
```bash
# Clone the FastTTS repository
git clone https://github.com/CGAlei/FastTTS.git
cd FastTTS

# Create conda environment with all dependencies
conda env create -f environment.yml -n fasttts-mfa

# Activate the environment
conda activate fasttts-mfa
```

### **Step 3: Download MFA Models (Optional but Recommended)**
```bash
# Download Chinese acoustic model and dictionary
mfa model download acoustic mandarin_mfa
mfa model download dictionary mandarin_mfa

# Verify models are installed
mfa model list
```

### **Step 4: Configure API Keys**
```bash
# Copy example environment file
cp .env.example .env

# Edit with your API keys (optional)
nano .env
```

### **Step 5: Launch FastTTS**
```bash
# Use the convenient launch script
./start_fasttts_mfa.sh

# OR run directly
python main.py
```

**🎉 Open http://localhost:5001 in your browser!**

---

## ⚡ **Method 2: Pip + System Dependencies**

### **For Advanced Users Who Prefer Pip**

### **Step 1: Install System Dependencies**

**Ubuntu/Debian:**
```bash
# Essential system packages
sudo apt update
sudo apt install -y python3 python3-pip python3-venv ffmpeg sox

# Optional: Montreal Forced Alignment
sudo apt install -y build-essential cmake libopenblas-dev
pip install montreal-forced-alignment==3.2.3
```

**CentOS/RHEL/Rocky Linux:**
```bash
# Enable EPEL repository
sudo dnf install -y epel-release

# Essential system packages
sudo dnf install -y python3 python3-pip ffmpeg sox

# Development tools for MFA
sudo dnf groupinstall -y "Development Tools"
sudo dnf install -y cmake openblas-devel
pip install montreal-forced-alignment==3.2.3
```

**Arch Linux:**
```bash
# Essential system packages
sudo pacman -S python python-pip ffmpeg sox

# Optional: Montreal Forced Alignment
sudo pacman -S base-devel cmake openblas
pip install montreal-forced-alignment==3.2.3
```

### **Step 2: Create Python Virtual Environment**
```bash
# Clone and setup
git clone https://github.com/CGAlei/FastTTS.git
cd FastTTS

# Create virtual environment
python3 -m venv fasttts-env
source fasttts-env/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### **Step 3: Configure and Launch**
```bash
# Configure API keys (optional)
cp .env.example .env
nano .env

# Launch FastTTS
python main.py
```

---

## 🐳 **Method 3: Docker Deployment**

### **For Containerized Deployment**

### **Step 1: Install Docker**

**Ubuntu/Debian:**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
```

**CentOS/RHEL/Rocky Linux:**
```bash
# Install Docker
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
newgrp docker
```

### **Step 2: Run FastTTS Container**
```bash
# Pull and run FastTTS container
docker run -d \
  --name fasttts \
  -p 5001:5001 \
  -v fasttts-data:/app/data \
  -e MINIMAX_API_KEY=your_key_here \
  -e OPENAI_API_KEY=your_key_here \
  cgalei/fasttts:latest

# Check container status
docker ps
```

### **Step 3: Access FastTTS**
**🎉 Open http://localhost:5001 in your browser!**

---

## 🔧 **Configuration**

### **Environment Variables (.env file)**
```bash
# TTS Engine API Keys (Optional)
MINIMAX_API_KEY=your_minimax_api_key
MINIMAX_GROUP_ID=your_group_id
OPENAI_API_KEY=your_openai_api_key

# FastTTS Settings
FASTTTS_DEFAULT_VOICE=zh-CN-XiaoxiaoNeural
FASTTTS_DEFAULT_ENGINE=edge
FASTTTS_LOG_LEVEL=INFO

# MFA Settings (Advanced)
MINIMAX_CHUNK_SIZE=120
FASTTTS_DEBUG_MODE=false
```

### **Voice Selection**
- **Edge TTS**: 50+ Chinese voices (free)
- **MiniMax**: Premium voices with custom options
- **Voice samples**: Test in the web interface

---

## ❓ **Troubleshooting**

### **Common Issues**

**🔴 "conda command not found"**
```bash
# Add conda to PATH
echo 'export PATH="$HOME/miniconda3/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**🔴 "FFmpeg not found"**
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# CentOS/RHEL
sudo dnf install ffmpeg

# Arch Linux
sudo pacman -S ffmpeg
```

**🔴 "MFA models not found"**
```bash
# Ensure conda environment is activated
conda activate fasttts-mfa

# Download models manually
mfa model download acoustic mandarin_mfa
mfa model download dictionary mandarin_mfa
```

**🔴 "Permission denied on port 5001"**
```bash
# Use different port
python main.py --port 5002

# Or check what's using port 5001
sudo netstat -tulpn | grep 5001
```

### **Performance Issues**

**🔴 "TTS generation is slow"**
- **Edge TTS**: Should be fast (2-3 seconds)
- **MiniMax**: Requires API key, premium service
- **MFA alignment**: First run downloads models (slow)

**🔴 "High memory usage"**
- **Expected**: 500MB-1GB with MFA models loaded
- **Reduce**: Disable MFA in settings for lower memory usage

---

## 🔄 **Updating FastTTS**

### **Conda Environment:**
```bash
cd FastTTS
git pull origin main
conda env update -f environment.yml
```

### **Pip Installation:**
```bash
cd FastTTS
git pull origin main
source fasttts-env/bin/activate
pip install -r requirements.txt --upgrade
```

### **Docker:**
```bash
docker pull cgalei/fasttts:latest
docker stop fasttts
docker rm fasttts
# Run new container with same command as above
```

---

## 📞 **Support**

### **Getting Help**
- **GitHub Issues**: https://github.com/CGAlei/FastTTS/issues
- **Wiki**: https://github.com/CGAlei/FastTTS/wiki
- **Email**: serinoac@gmail.com

### **Before Reporting Issues**
1. Check this installation guide
2. Verify system requirements
3. Test with a fresh environment
4. Include system info and error logs

---

## 🎉 **Success!**

If everything worked, you should see:
- **Web interface** at http://localhost:5001
- **TTS generation** working with Chinese text
- **Vocabulary learning** features active
- **Audio playback** with word-level timing

**Ready to explore Chinese TTS with AI-powered learning!**