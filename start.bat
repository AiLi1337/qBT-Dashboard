@echo off
REM qBittorrent Management Panel - Windows Startup Script
REM Double-click this file or run from command line

echo ========================================
echo   qBittorrent Management Panel
echo   Windows Startup Script
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.13 or later from https://python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists, create if not
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies if needed
echo Checking dependencies...
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Check for .env file
if not exist ".env" (
    if exist ".env.example" (
        echo Creating .env file from template...
        copy .env.example .env
        echo WARNING: Please edit .env to set secure passwords!
        echo.
    )
)

echo.
echo Starting server...
echo Server will be available at: http://127.0.0.1:8000
echo Press Ctrl+C to stop the server
echo.

REM Start the server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

REM Deactivate virtual environment on exit
deactivate