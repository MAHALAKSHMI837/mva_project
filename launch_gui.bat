@echo off
echo Meeting Video Captioning ^& Documentation
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if required files exist
if not exist "run.py" (
    echo ERROR: run.py not found
    echo Please ensure you're in the correct directory
    pause
    exit /b 1
)

REM Launch the GUI
echo Launching GUI interface...
python run.py --gui

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo An error occurred. Check the logs for details.
    pause
)