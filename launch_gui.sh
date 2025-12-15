#!/bin/bash

echo "Meeting Video Captioning & Documentation"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ERROR: Python is not installed"
        echo "Please install Python 3.8+ from https://python.org"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "ERROR: Python $REQUIRED_VERSION or higher is required"
    echo "Current version: $PYTHON_VERSION"
    exit 1
fi

# Check if required files exist
if [ ! -f "run.py" ]; then
    echo "ERROR: run.py not found"
    echo "Please ensure you're in the correct directory"
    exit 1
fi

# Launch the GUI
echo "Launching GUI interface..."
$PYTHON_CMD run.py --gui

# Check exit status
if [ $? -ne 0 ]; then
    echo
    echo "An error occurred. Check the logs for details."
    read -p "Press Enter to continue..."
fi