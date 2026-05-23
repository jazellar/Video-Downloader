#!/bin/bash

# AnyStream Downloader Build Script for macOS
echo "Building AnyStream Downloader for macOS..."

# Clean up any existing build
rm -rf build dist *.spec

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
python3 -m pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
python3 -m pip install -r requirements.txt
python3 -m pip install pyinstaller

# Verify installations
python3 -c "import yt_dlp; print('yt-dlp version:', yt_dlp.version.__version__)"
python3 -c "import PyInstaller; print('PyInstaller imported successfully')"

# Build the app
echo "Building application..."
python3 -m PyInstaller --clean --windowed --onedir --name="AnyStream Downloader" \
    --icon="AnyStreamLogo.icns" \
    --add-data "AnyStream Logo.png:." \
    --add-data "logo.png:." \
    --add-data "AnyStreamLogo.png:." \
    --add-data "app_icon.png:." \
    anystream_downloader.py

# Check if build was successful
if [ -d "dist/AnyStream Downloader.app" ]; then
    echo "Build successful!"
    echo "Your app is located at: $(pwd)/dist/AnyStream Downloader.app"
    echo "You can copy this app to your Applications folder or run it directly."
else
    echo "Build completed. Check the dist folder for the application."
fi

echo "Build complete!"

# Deactivate virtual environment
deactivate