# AnyStream Downloader Build Script for Windows
# Run this in Command Prompt or PowerShell

@echo off
echo Building AnyStream Downloader for Windows...

# Check if virtual environment exists, create if not
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

# Activate virtual environment
call venv\Scripts\activate

# Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller

# Build the app
echo Building application...
pyinstaller --clean --windowed --onedir --name="AnyStream Downloader" anystream_downloader.py

echo Build complete!
echo Your app is in the 'dist' folder.
echo To run: dist\AnyStream Downloader\AnyStream Downloader.exe

# Deactivate virtual environment
deactivate

pause