@echo off
REM FastTTS with MFA - Windows Startup Script
REM This script activates the MFA environment and starts FastTTS

echo 🚀 Starting FastTTS with MFA Integration...
echo 📁 Working directory: D:\FastTTS

REM Navigate to FastTTS directory (adjust path as needed)
cd /d "D:\FastTTS" 2>nul || (
    echo ❌ Error: Cannot find FastTTS directory at D:\FastTTS
    echo    Please adjust the path in this batch file.
    pause
    exit /b 1
)

REM Initialize conda for Windows
echo 🔧 Initializing conda...
call "%USERPROFILE%\miniconda3\Scripts\activate.bat" 2>nul || (
    echo ❌ Error: Cannot initialize conda
    echo    Please make sure Miniconda is installed properly.
    pause
    exit /b 1
)

REM Activate MFA environment
echo 🎯 Activating fasttts-mfa environment...
call conda activate fasttts-mfa || (
    echo ❌ Error: Cannot activate fasttts-mfa environment
    echo    Please run: conda env create -f environment.yml
    pause
    exit /b 1
)

REM Verify MFA is available
echo 🧪 Testing MFA availability...
python -c "import sys; sys.path.insert(0, 'D:/FastTTS'); from alignment.mfa_aligner import MFAAligner; aligner = MFAAligner(); print('✅ MFA is ready!' if aligner.is_available else '⚠️  MFA not available - will use fallback timing')"

REM Start FastTTS
echo 🌟 Starting FastTTS application...
echo    Access at: http://localhost:5001
echo    Press Ctrl+C to stop
echo.

python main.py

echo.
echo 👋 FastTTS stopped. Environment still active.
echo    Type 'conda deactivate' to exit MFA environment
pause