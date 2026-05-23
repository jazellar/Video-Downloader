@echo off
echo Building AnyStream Downloader for Windows...
echo.

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
call venv\Scripts\activate

REM Upgrade pip
echo Upgrading pip...
pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install requirements
    pause
    exit /b 1
)

pip install pyinstaller
if errorlevel 1 (
    echo Failed to install PyInstaller
    pause
    exit /b 1
)

REM Build the app with antivirus-friendly options
echo Building application...
python -m PyInstaller --clean --windowed --onedir --name="AnyStream Downloader" --noupx --hidden-import=yt_dlp --hidden-import=tkinter --hidden-import=tkinter.filedialog --hidden-import=tkinter.messagebox anystream_downloader.py

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Build successful!
echo Your app is in the 'dist\AnyStream Downloader' folder
echo.
echo To reduce antivirus false positives, you can:
echo 1. Submit the exe to VirusTotal for analysis
echo 2. Sign the executable with a code signing certificate
echo 3. Ask your friend to add an exception in their antivirus
echo.
pause