#!/bin/bash
#
# qBittorrent Management Panel - Linux/macOS Startup Script
# Usage: ./start.sh [port]
#

set -e

echo "========================================"
echo "  qBittorrent Management Panel"
echo "  Linux/macOS Startup Script"
echo "========================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.13 or later"
    exit 1
fi

# Get Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(sys.version_info.major + sys.version_info.minor / 10)')
REQUIRED_VERSION=3.13

# Check Python version (allow slightly older versions for compatibility)
if (( $(echo "$PYTHON_VERSION < 3.10" | bc -l 2>/dev/null || echo 0) )); then
    echo "WARNING: Python version $PYTHON_VERSION detected. Python 3.13+ is recommended."
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
echo "Checking dependencies..."
pip install -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "Creating .env file from template..."
        cp .env.example .env
        echo "WARNING: Please edit .env to set secure passwords!"
        echo ""
    fi
fi

# Get port from argument or use default
PORT=${1:-8000}

echo ""
echo "Starting server..."
echo "Server will be available at: http://127.0.0.1:$PORT"
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python3 -m uvicorn app.main:app --host 127.0.0.1 --port $PORT --reload