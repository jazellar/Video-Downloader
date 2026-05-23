#!/usr/bin/env python3
"""
AnyStream Downloader Builder
Cross-platform build script for creating standalone applications
"""

import os
import sys
import subprocess
import shutil
import platform

def run_command(command, cwd=None):
    """Run a command and return True if successful"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, check=True,
                              capture_output=True, text=True)
        return True, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def create_virtual_env():
    """Create virtual environment if it doesn't exist"""
    if not os.path.exists('venv'):
        print("Creating virtual environment...")
        success, stdout, stderr = run_command("python3 -m venv venv")
        if not success:
            print(f"Failed to create virtual environment: {stderr}")
            return False
    return True

def install_dependencies():
    """Install required dependencies in virtual environment"""
    print("Installing dependencies...")

    # Activate virtual environment and install packages
    if platform.system() == "Windows":
        activate_cmd = "venv\\Scripts\\activate"
        python_cmd = "python3"
        pip_cmd = "python3 -m pip"
    else:
        activate_cmd = "source venv/bin/activate"
        python_cmd = "python3"
        pip_cmd = "python3 -m pip"

    # Install requirements
    success, stdout, stderr = run_command(f"{activate_cmd} && {pip_cmd} install --upgrade pip")
    if not success:
        print(f"Failed to upgrade pip: {stderr}")
        return False

    success, stdout, stderr = run_command(f"{activate_cmd} && {pip_cmd} install -r requirements.txt")
    if not success:
        print(f"Failed to install requirements: {stderr}")
        return False

    success, stdout, stderr = run_command(f"{activate_cmd} && {pip_cmd} install pyinstaller")
    if not success:
        print(f"Failed to install PyInstaller: {stderr}")
        return False

    return True

def build_app():
    """Build the application using PyInstaller"""
    print("Building application...")

    # Clean previous builds
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')

    # Build command - use --onedir for better compatibility
    data_sep = ";" if platform.system() == "Windows" else ":"
    data_args = " ".join([
        f'--add-data "AnyStream Logo.png{data_sep}."',
        #f'--add-data "logo.png{data_sep}."',
        #f'--add-data "AnyStreamLogo.png{data_sep}."',
        #f'--add-data "app_icon.png{data_sep}."',
    ])
    icon_arg = "--icon=AnyStreamLogo.icns" if platform.system() != "Windows" else ""

    if platform.system() == "Windows":
        cmd = (
            "venv\\Scripts\\activate && "
            f'python3 -m PyInstaller --clean --windowed --onedir --name="AnyStream Downloader" --noupx {icon_arg} {data_args} anystream_downloader.py'
        )
    else:
        cmd = (
            "source venv/bin/activate && "
            f'python3 -m PyInstaller --clean --windowed --onedir --name="AnyStream Downloader" --noupx {icon_arg} {data_args} anystream_downloader.py'
        )

    success, stdout, stderr = run_command(cmd)
    if not success:
        print(f"Build failed: {stderr}")
        return False

    print("Build successful!")
    return True

def main():
    """Main build function"""
    print("AnyStream Downloader Builder")
    print("=" * 30)

    # Check if we're in the right directory
    if not os.path.exists('anystream_downloader.py'):
        print("Error: anystream_downloader.py not found in current directory")
        sys.exit(1)

    if not os.path.exists('requirements.txt'):
        print("Error: requirements.txt not found")
        sys.exit(1)

    # Create virtual environment
    if not create_virtual_env():
        sys.exit(1)

    # Install dependencies
    if not install_dependencies():
        sys.exit(1)

    # Build application
    if not build_app():
        sys.exit(1)

    # Show results
    dist_path = os.path.join('dist', 'AnyStream Downloader')
    if platform.system() == "Darwin":  # macOS
        app_path = dist_path + ".app"
        if os.path.exists(app_path):
            print(f"\nApplication created at: {os.path.abspath(app_path)}")
            print("You can copy this to your Applications folder or run it directly.")
        else:
            print(f"\nApplication created in: {os.path.abspath(dist_path)}")
    else:
        exe_path = os.path.join(dist_path, 'AnyStream Downloader.exe')
        if os.path.exists(exe_path):
            print(f"\nApplication created at: {os.path.abspath(exe_path)}")
        else:
            print(f"\nApplication created in: {os.path.abspath(dist_path)}")

    print("\nBuild complete!")

if __name__ == "__main__":
    main()