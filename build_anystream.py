#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
import platform

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return True, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def main():
    print("AnyStream Downloader - Single File Compiler")
    print("==========================================")

    if not os.path.exists('anystream_downloader.py'):
        print("[-] Error: anystream_downloader.py not found.")
        sys.exit(1)

    # 1. Locate the proper Python executable inside your virtual environment
    if platform.system() == "Windows":
        venv_python = os.path.join(".venv", "Scripts", "python.exe")
    else:
        venv_python = os.path.join(".venv", "bin", "python")

    # Fallback to system python if .venv folder doesn't exist
    if not os.path.exists(venv_python):
        print("[!] Local .venv not detected. Falling back to global system python.")
        venv_python = "python"
    else:
        print(f"[+] Using environment Python: {venv_python}")

    # 2. Make sure PyInstaller is actually installed in that environment
    print("[*] Ensuring PyInstaller and dependencies are installed...")
    run_command(f'"{venv_python}" -m pip install pyinstaller yt-dlp pillow')

    # Clean up old build folders so we start completely fresh
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)

    # Multi-platform asset separator (Windows uses ';', Mac/Linux uses ':')
    sep = ";" if platform.system() == "Windows" else ":"
    
    # Target assets to bake directly inside the executable
    asset_1 = f'--add-data "AnyStream Logo.png{sep}."'
    asset_2 = f'--add-data "AnyStream Background.png{sep}."'

    # Build the command using python -m PyInstaller
    pyinstaller_cmd = [
        f'"{venv_python}" -m PyInstaller',
        "--clean",
        "--onefile",                  # Combines everything into one single .exe file
        "--windowed",                 # Hides the black terminal console window
        "--noconfirm",
        asset_1,                      
        asset_2,
        "anystream_downloader.py"
    ]

    # If you created the AnyStreamLogo.ico asset, embed it into the file binary properties
    if os.path.exists('AnyStreamLogo.ico'):
        pyinstaller_cmd.insert(5, '--icon="AnyStreamLogo.ico"')

    print("[*] Packing application into a single executable... (This may take a minute)")
    full_cmd = " ".join(pyinstaller_cmd)
    success, stdout, stderr = run_command(full_cmd)

    if not success:
        print(f"[-] Compilation failed. Error log:\n{stderr}")
        sys.exit(1)

    print("[+] Success! Your standalone application is ready.")
    print(f" Look inside this folder for your single file: {os.path.abspath('dist')}")

if __name__ == "__main__":
    main()