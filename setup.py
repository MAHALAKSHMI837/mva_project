#!/usr/bin/env python3
"""
Setup script for Meeting Video Captioning & Documentation
Handles installation of dependencies and system requirements
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def run_command(cmd, check=True):
    """Run a command and return the result"""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        if check:
            raise
        return e

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("ERROR: Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        sys.exit(1)
    print(f"✓ Python version {version.major}.{version.minor}.{version.micro} is compatible")

def install_system_dependencies():
    """Install system-level dependencies"""
    system = platform.system().lower()
    
    print(f"Detected system: {system}")
    
    if system == "windows":
        print("On Windows, please ensure you have:")
        print("1. FFmpeg installed and in PATH")
        print("2. Chrome browser installed (for private platform access)")
        print("You can download FFmpeg from: https://ffmpeg.org/download.html")
        
    elif system == "darwin":  # macOS
        print("Installing system dependencies on macOS...")
        # Check if Homebrew is installed
        try:
            run_command(["brew", "--version"])
            run_command(["brew", "install", "ffmpeg"])
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Homebrew not found. Please install FFmpeg manually:")
            print("https://ffmpeg.org/download.html")
            
    elif system == "linux":
        print("Installing system dependencies on Linux...")
        try:
            # Try apt-get first (Ubuntu/Debian)
            run_command(["sudo", "apt-get", "update"], check=False)
            run_command(["sudo", "apt-get", "install", "-y", "ffmpeg"], check=False)
        except:
            try:
                # Try yum (CentOS/RHEL)
                run_command(["sudo", "yum", "install", "-y", "ffmpeg"], check=False)
            except:
                print("Could not install FFmpeg automatically.")
                print("Please install FFmpeg manually for your distribution.")

def install_python_dependencies():
    """Install Python package dependencies"""
    print("Installing Python dependencies...")
    
    # Upgrade pip first
    run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    # Install requirements
    requirements_file = Path(__file__).parent / "requirements.txt"
    if requirements_file.exists():
        run_command([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
    else:
        # Fallback to manual installation
        packages = [
            "opencv-python",
            "numpy",
            "pytube",
            "moviepy",
            "ffmpeg-python",
            "openai-whisper",
            "python-docx",
            "reportlab",
            "requests",
            "scikit-image",
            "tqdm",
            "selenium",
            "webdriver-manager",
            "tkinter"  # Usually comes with Python
        ]
        
        for package in packages:
            try:
                run_command([sys.executable, "-m", "pip", "install", package])
            except subprocess.CalledProcessError:
                print(f"Warning: Failed to install {package}")

def create_directories():
    """Create necessary directories"""
    print("Creating project directories...")
    
    directories = [
        "data",
        "data/videos",
        "data/frames", 
        "data/transcripts",
        "data/captioned",
        "data/reports",
        "logs"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {dir_path}")

def test_installation():
    """Test if key components are working"""
    print("\nTesting installation...")
    
    # Test imports
    try:
        import cv2
        print("✓ OpenCV imported successfully")
    except ImportError:
        print("✗ OpenCV import failed")
    
    try:
        import whisper
        print("✓ Whisper imported successfully")
    except ImportError:
        print("✗ Whisper import failed")
    
    try:
        import moviepy.editor
        print("✓ MoviePy imported successfully")
    except ImportError:
        print("✗ MoviePy import failed")
    
    # Test FFmpeg
    try:
        result = run_command(["ffmpeg", "-version"], check=False)
        if result.returncode == 0:
            print("✓ FFmpeg is available")
        else:
            print("✗ FFmpeg not found in PATH")
    except FileNotFoundError:
        print("✗ FFmpeg not found")

def main():
    """Main setup function"""
    print("=" * 60)
    print("Meeting Video Captioning & Documentation Setup")
    print("=" * 60)
    
    try:
        check_python_version()
        install_system_dependencies()
        install_python_dependencies()
        create_directories()
        test_installation()
        
        print("\n" + "=" * 60)
        print("SETUP COMPLETED!")
        print("=" * 60)
        print("You can now run the application using:")
        print("  python run.py --gui                    # Launch GUI")
        print("  python run.py -i video.mp4             # Process local video")
        print("  python run.py -i <youtube_url> -t youtube  # Process YouTube video")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nSetup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()