# AnyStream Downloader

A simple GUI application for downloading videos and audio from various platforms using yt-dlp.

## Features

- Download videos in various formats
- Download audio only (MP3 format) with embedded metadata
- Choose custom download folder
- **Full metadata embedding** - thumbnails, titles, artists, descriptions
- Cross-platform support (macOS and Windows)

## Metadata Included

### For MP3 Audio Files:
- ✅ **Title** - Song/video title
- ✅ **Artist** - Channel/uploader name
- ✅ **Album** - Video title or playlist name (when available)
- ✅ **Album Art** - Video thumbnail embedded as cover art
- ✅ **Year** - Upload date
- ✅ **Description** - Video description (in metadata)
- ✅ **Genre** - Automatically detected or set to "Music"

### For Video Files:
- ✅ **Title** - Video title
- ✅ **Description** - Full video description
- ✅ **Thumbnail** - Embedded video thumbnail
- ✅ **Upload Date** - Creation date
- ✅ **Channel/Author** - Uploader information
- ✅ **Duration** - Video length

## Building the Application

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Quick Build (Recommended)

The easiest way to build the application is using the provided Python build script:

#### macOS
```bash
cd "/Users/papaz/Documents/Python Projects/AnyStream Downloader"
python3 build_anystream.py
```

#### Windows
```cmd
cd "C:\Path\To\Your AnyStream Downloader"
python build_anystream.py
```

### Manual Build

If you prefer to build manually:

#### macOS Build

1. Open Terminal and navigate to the project directory:
   ```bash
   cd "/Users/papaz/Documents/Python Projects/AnyStream Downloader"
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

4. Build the application:
   ```bash
   pyinstaller --clean --windowed --onedir --name="AnyStream Downloader" anystream_downloader.py
   ```

5. The built application will be in the `dist` folder

#### Windows Build

1. Open Command Prompt or PowerShell and navigate to the project directory:
   ```cmd
   cd "C:\Path\To\Your\AnyStream Downloader"
   ```

2. Create and activate a virtual environment:
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```cmd
   pip install -r requirements.txt
   pip install pyinstaller
   ```

4. Build the application:
   ```cmd
   pyinstaller --clean --windowed --onedir --name="AnyStream Downloader" anystream_downloader.py
   ```

5. The built application will be in the `dist` folder

## Usage

1. Launch the application
2. Enter the video URL
3. Choose a download folder using the Browse button
4. Check "Download audio only (MP3)" if you want audio only
5. Click "Download Video" to start the download

## Dependencies

- yt-dlp: For downloading videos
- tkinter: Built-in Python GUI library (comes with Python)

## Notes

- FFmpeg is required for audio conversion. yt-dlp will handle this automatically if FFmpeg is installed on your system.
- The application will create a standalone executable that doesn't require Python to be installed on the target machine.
- First run may take longer as yt-dlp updates its extractors.

## Troubleshooting

### Antivirus False Positives (Most Common Issue)

PyInstaller executables are often flagged as malware by antivirus software. This is a false positive. Here are solutions:

#### For Your Friend:
echo 1. **Add an exception** in their antivirus software for the AnyStream Downloader executable
2. **Temporarily disable** antivirus while running the app (not recommended for security)
3. **Check VirusTotal** - upload the exe to [virustotal.com](https://virustotal.com) to verify it's safe

#### For You (Developer):
1. **Use `--noupx`** flag when building (already included in our scripts)
2. **Code sign** the executable (requires Windows SDK and certificate)
3. **Submit to antivirus vendors** for whitelisting

### Build Issues

- If the build fails, ensure all dependencies are installed
- Make sure you have write permissions in the project directory
- On macOS, you may need to allow the app to run in System Preferences > Security & Privacy

### Runtime Issues

- **"Application cannot be opened"** on macOS: Right-click the app and select "Open"
- **Missing DLLs** on Windows: Ensure you built on the same Windows version as target
- **FFmpeg not found**: yt-dlp handles this automatically, but ensure internet connection on first run

### Cross-Platform Issues

- **Built on macOS, running on Windows**: Won't work - need to build on Windows for Windows exe
- **Built on Windows, running on macOS**: Won't work - need to build on macOS for .app bundles
- **Architecture mismatch**: Build on 64-bit systems for 64-bit targets

## Advanced Build Options

### For Better Antivirus Compatibility

Use the `build_anystream_windows_fixed.bat` script which includes:
- `--noupx` (disables compression that triggers false positives)
- `--hidden-import` flags for all dependencies
- One-folder bundle instead of single exe

### Code Signing (Windows)

To reduce false positives, sign your executable:

```bash
# Install Windows SDK first, then:
signtool sign /f your_cert.pfx /p your_password "dist\AnyStream Downloader\AnyStream Downloader.exe"
```
- If you get permission errors, try running the build script with `sudo` (not recommended for security reasons)