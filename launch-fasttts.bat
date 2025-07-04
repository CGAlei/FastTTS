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

echo Initializing conda...

REM Initialize conda for batch (try multiple approaches)
if exist "%USERPROFILE%\miniconda3\Scripts\activate.bat" (
    call "%USERPROFILE%\miniconda3\Scripts\activate.bat" "%USERPROFILE%\miniconda3"
) else if exist "%USERPROFILE%\anaconda3\Scripts\activate.bat" (
    call "%USERPROFILE%\anaconda3\Scripts\activate.bat" "%USERPROFILE%\anaconda3"
) else if exist "C:\ProgramData\miniconda3\Scripts\activate.bat" (
    call "C:\ProgramData\miniconda3\Scripts\activate.bat" "C:\ProgramData\miniconda3"
) else (
    REM Try to initialize conda environment
    call conda info --envs >nul 2>nul
    if %errorlevel% neq 0 (
        echo ERROR: Could not initialize conda
        echo Please make sure conda is properly installed and configured
        pause
        exit /b 1
    )
)

REM Check if fast_tts environment exists
conda env list | findstr "fast_tts" >nul
if %errorlevel% neq 0 (
    echo ERROR: conda environment 'fast_tts' not found
    echo Please create the environment first:
    echo   conda env create -f environment.yml
    pause
    exit /b 1
)

echo Activating fast_tts environment...
call conda activate fast_tts
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate conda environment 'fast_tts'
    echo Try running this manually:
    echo   conda activate fast_tts
    echo   python main.py
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
echo.
echo Web interface will be available at: http://127.0.0.1:5001
echo You can now create a Web App pointing to this address
echo.
echo Press Ctrl+C to stop the application
echo ==========================================
echo.

REM Start the application
python main.py