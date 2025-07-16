#!/usr/bin/env python3
"""
Improved setup script for Voice Practice application
Handles dependency installation with better error handling and platform detection
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def run_command(command, description=""):
    """Run a command with proper error handling"""
    print(f"Running: {description or command}")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✓ Success: {description}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed: {description}")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Ensure Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("✗ Python 3.8+ required")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    return True

def install_system_dependencies():
    """Install system-level dependencies based on platform"""
    system = platform.system().lower()
    
    if system == "windows":
        print("Windows detected - most dependencies should install via pip")
        return True
    elif system == "darwin":  # macOS
        print("macOS detected - checking for Homebrew...")
        if not run_command("brew --version", "Checking Homebrew"):
            print("Please install Homebrew first: https://brew.sh/")
            return False
        run_command("brew install portaudio", "Installing PortAudio")
    elif system == "linux":
        print("Linux detected - installing system dependencies...")
        # Try different package managers
        if run_command("which apt-get", "Checking apt"):
            run_command("sudo apt-get update", "Updating package list")
            run_command("sudo apt-get install -y portaudio19-dev python3-dev", 
                       "Installing PortAudio and Python dev headers")
        elif run_command("which yum", "Checking yum"):
            run_command("sudo yum install -y portaudio-devel python3-devel", 
                       "Installing PortAudio and Python dev headers")
    
    return True

def create_virtual_environment():
    """Create and activate virtual environment"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✓ Virtual environment already exists")
        return True
    
    if not run_command(f"{sys.executable} -m venv venv", "Creating virtual environment"):
        return False
    
    print("✓ Virtual environment created")
    print("To activate: ")
    if platform.system().lower() == "windows":
        print("  venv\\Scripts\\activate")
    else:
        print("  source venv/bin/activate")
    
    return True

def install_python_dependencies():
    """Install Python dependencies with proper ordering"""
    
    # Core dependencies first
    core_deps = [
        "wheel",
        "setuptools",
        "numpy>=1.23",
        "scipy>=1.9"
    ]
    
    # Audio dependencies
    audio_deps = [
        "sounddevice>=0.4.6",
        "soundfile>=0.12",
        "librosa>=0.10"
    ]
    
    # ML dependencies
    ml_deps = [
        "torch>=2.0",
        "torchaudio>=2.0",
        "openai-whisper>=20231117"
    ]
    
    # GUI dependencies
    gui_deps = [
        "PyQt5>=5.15",
        "pyqtgraph>=0.13",
        "matplotlib>=3.5"
    ]
    
    # Utility dependencies
    util_deps = [
        "keyboard>=0.13"
    ]
    
    all_deps = [core_deps, audio_deps, ml_deps, gui_deps, util_deps]
    dep_names = ["Core", "Audio", "ML", "GUI", "Utility"]
    
    for deps, name in zip(all_deps, dep_names):
        print(f"\nInstalling {name} dependencies...")
        for dep in deps:
            if not run_command(f"pip install {dep}", f"Installing {dep}"):
                print(f"⚠ Warning: Failed to install {dep}")
                # Continue with other dependencies
    
    return True

def verify_installation():
    """Verify that key modules can be imported"""
    test_imports = [
        ("numpy", "NumPy"),
        ("scipy", "SciPy"),
        ("sounddevice", "SoundDevice"),
        ("librosa", "Librosa"),
        ("PyQt5", "PyQt5"),
        ("pyqtgraph", "PyQtGraph"),
        ("whisper", "OpenAI Whisper"),
        ("torch", "PyTorch")
    ]
    
    print("\nVerifying installation...")
    success_count = 0
    
    for module, name in test_imports:
        try:
            __import__(module)
            print(f"✓ {name}")
            success_count += 1
        except ImportError as e:
            print(f"✗ {name}: {e}")
    
    print(f"\nInstallation verification: {success_count}/{len(test_imports)} modules working")
    return success_count == len(test_imports)

def create_launcher_scripts():
    """Create convenient launcher scripts"""
    
    # Windows batch file
    with open("run.bat", "w") as f:
        f.write("""@echo off
echo Starting Voice Practice...
if exist venv\\Scripts\\activate.bat (
    call venv\\Scripts\\activate.bat
    python main.py
) else (
    python main.py
)
pause
""")
    
    # Unix shell script
    with open("run.sh", "w") as f:
        f.write("""#!/bin/bash
echo "Starting Voice Practice..."
if [ -f venv/bin/activate ]; then
    source venv/bin/activate
fi
python main.py
""")
    
    # Make shell script executable on Unix systems
    if platform.system().lower() != "windows":
        os.chmod("run.sh", 0o755)
    
    print("✓ Created launcher scripts (run.bat / run.sh)")

def main():
    """Main setup process"""
    print("=== Voice Practice Setup ===\n")
    
    if not check_python_version():
        return False
    
    if not install_system_dependencies():
        print("⚠ System dependency installation had issues")
    
    if not create_virtual_environment():
        print("✗ Failed to create virtual environment")
        return False
    
    if not install_python_dependencies():
        print("⚠ Some Python dependencies failed to install")
    
    create_launcher_scripts()
    
    print("\n=== Setup Summary ===")
    if verify_installation():
        print("✓ Setup completed successfully!")
        print("\nTo run the application:")
        print("1. Activate virtual environment (if created)")
        print("2. Run: python main.py")
        print("   Or use: run.bat (Windows) / ./run.sh (Unix)")
    else:
        print("⚠ Setup completed with some issues")
        print("Some dependencies may need manual installation")
    
    return True

if __name__ == "__main__":
    main()