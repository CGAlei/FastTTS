# FastTTS Execution Guide

This guide provides step-by-step instructions for running FastTTS on both Linux and Windows systems.

## 🐧 Linux Instructions

### Quick Start (Current Setup)

1. **Open Terminal** anywhere
2. **Run the launch command:**
   ```bash
   fasttts
   ```
3. **Wait for confirmation:** Look for "✅ Server is responding on port 5001"
4. **Keep the terminal running** - Do not close it or press Ctrl+C
5. **Open Web Apps** (or browser) and navigate to: `http://127.0.0.1:5001`

### Easy Access Options

#### Option 1: Create Desktop Shortcut
1. Create a new file on your desktop: `FastTTS.desktop`
2. Add this content:
   ```ini
   [Desktop Entry]
   Name=FastTTS
   Comment=Launch FastTTS Application
   Exec=gnome-terminal -- fasttts
   Icon=applications-multimedia
   Terminal=true
   Type=Application
   Categories=AudioVideo;Audio;
   ```
3. Make it executable: `chmod +x ~/Desktop/FastTTS.desktop`
4. Double-click to launch FastTTS

#### Option 2: Already Available!
The `fasttts` command is already available system-wide. Just type `fasttts` in any terminal from anywhere.

**Note:** The launcher script has been updated to correctly point to the FastTTS project directory at `/home/alex/AI_Project/FastTTS`.

#### Option 3: Web Apps Integration
1. Start FastTTS using the launch script
2. Open **Web Apps** application
3. Click "+" to create new web app
4. Fill in:
   - **Name:** FastTTS
   - **Address:** http://127.0.0.1:5001
   - **Icon:** Choose any icon you like
5. Click **OK**
6. FastTTS will appear as a desktop application

### Auto-Start Options (Optional)

#### Systemd Service (Auto-start on boot)
Only if you want FastTTS to start automatically when your computer boots:

1. Create service file:
   ```bash
   sudo nano /etc/systemd/system/fasttts.service
   ```

2. Add this content:
   ```ini
   [Unit]
   Description=FastTTS Application
   After=network.target

   [Service]
   Type=simple
   User=alex
   WorkingDirectory=/home/alex/AI_Project/FastTTS
   ExecStart=/home/alex/AI_Project/FastTTS/launch-fasttts.sh
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start:
   ```bash
   sudo systemctl enable fasttts
   sudo systemctl start fasttts
   ```

4. Control commands:
   ```bash
   sudo systemctl start fasttts    # Start
   sudo systemctl stop fasttts     # Stop
   sudo systemctl restart fasttts  # Restart
   sudo systemctl status fasttts   # Check status
   ```

---

## 🪟 Windows Instructions

### Prerequisites
1. Install **Miniconda** or **Anaconda** from: https://docs.conda.io/en/latest/miniconda.html
2. Create the conda environment using the provided `environment.yml`

### Setup Steps

1. **Open Command Prompt or PowerShell as Administrator**
2. **Navigate to FastTTS directory:**
   ```cmd
   cd C:\path\to\AI_Project\FastTTS
   ```
3. **Create conda environment:**
   ```cmd
   conda env create -f environment.yml
   ```

### Windows Batch File

Create a file named `launch-fasttts.bat` in your FastTTS directory:

```batch
@echo off
title FastTTS Launcher
color 0B

echo.
echo ==========================================
echo           FastTTS Launcher
echo ==========================================
echo.

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"
echo Project directory: %SCRIPT_DIR%

REM Change to script directory
cd /d "%SCRIPT_DIR%"

REM Check if conda is available
where conda >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: conda not found in PATH
    echo Please install Miniconda/Anaconda or add it to your PATH
    pause
    exit /b 1
)

REM Initialize conda for batch
call conda activate fast_tts
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate conda environment 'fast_tts'
    echo Make sure the environment exists:
    echo   conda env create -f environment.yml
    pause
    exit /b 1
)

echo Environment activated: fast_tts

REM Check if main.py exists
if not exist "main.py" (
    echo ERROR: main.py not found in %SCRIPT_DIR%
    pause
    exit /b 1
)

echo.
echo Starting FastTTS application...
echo Web interface will be available at: http://127.0.0.1:5001
echo.
echo Press Ctrl+C to stop the application
echo ==========================================

REM Start the application
python main.py
```

### Quick Start (Windows)

1. **Double-click** `launch-fasttts.bat`
2. **Wait for the server to start**
3. **Open your browser** and go to: `http://127.0.0.1:5001`

### Easy Access Options (Windows)

#### Option 1: Desktop Shortcut
1. Right-click on `launch-fasttts.bat`
2. Select "Create shortcut"
3. Move the shortcut to your desktop
4. Rename it to "FastTTS"
5. Double-click to launch

#### Option 2: Start Menu Integration
1. Press `Win + R`, type `shell:startup`
2. Create a shortcut to `launch-fasttts.bat` in this folder
3. FastTTS will be available in Start Menu

#### Option 3: Task Scheduler (Auto-start)
1. Open **Task Scheduler**
2. Click "Create Basic Task"
3. Name: "FastTTS"
4. Trigger: "When I log on"
5. Action: "Start a program"
6. Program: Path to your `launch-fasttts.bat`
7. Finish

---

## 🌐 Web Apps Integration

### For Linux (GNOME Web Apps)
1. Install Web Apps: `sudo apt install epiphany-browser` (if not installed)
2. Launch **Web Apps** from applications menu
3. Create new web app with URL: `http://127.0.0.1:5001`

### For Windows (Progressive Web App)
1. Open **Edge** or **Chrome**
2. Navigate to: `http://127.0.0.1:5001`
3. Click the "Install" button in the address bar
4. Or go to Settings → Apps → Install this site as an app

---

## ⚠️ Troubleshooting

### Common Issues

**"Server not responding" or "Unable to connect"**
- Make sure the launch script is still running
- Check if port 5001 is being used by another application
- Try restarting the launch script

**"Conda environment not found"**
- Run: `conda env create -f environment.yml`
- Make sure conda is properly installed and in PATH

**"Permission denied" (Linux)**
- Make script executable: `chmod +x launch-fasttts.sh`

**"main.py not found" error**
- This has been fixed in the launcher script which now correctly points to `/home/alex/AI_Project/FastTTS`
- If you still see this error, ensure the `fasttts` command is using the updated launcher script

**Python import errors**
- Activate the environment manually: `conda activate fast_tts`
- Check if all packages are installed: `conda list`

### Stopping FastTTS

**Method 1: If you have the terminal open:**
- Press `Ctrl+C` in the terminal where `fasttts` is running

**Method 2: Force kill from any terminal:**
```bash
# Kill by process name
pkill -f "python main.py"
# or kill by port
sudo lsof -ti:5001 | xargs kill -9
```

**Method 3: If running as systemd service:**
```bash
sudo systemctl stop fasttts
```

### Checking if FastTTS is Running

**Linux:**
```bash
curl http://127.0.0.1:5001
# or
netstat -tlnp | grep 5001
```

**Windows:**
```cmd
curl http://127.0.0.1:5001
# or
netstat -an | findstr 5001
```

---

## 📝 Quick Reference

### Linux Commands
```bash
# Start FastTTS (from anywhere)
fasttts

# Check if running
curl http://127.0.0.1:5001
```

### Windows Commands
```cmd
# Start FastTTS
launch-fasttts.bat

# Check if running
curl http://127.0.0.1:5001
```

### URLs
- **Web Interface:** http://127.0.0.1:5001
- **Local Access Only:** FastTTS only accepts connections from your computer for security

---

*Need help? Check the logs in the `logs/` directory or run the commands manually to see detailed error messages.*