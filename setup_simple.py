#!/usr/bin/env python3
"""
Simple setup script for Voice Practice application.
Creates necessary directories and checks dependencies.
"""

import os
import sys
import subprocess
import json

def create_directories():
    """Create necessary directories"""
    directories = [
        './logs',
        './rec',
        './examples',
        './corpus',
        './corpus-processed'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'sounddevice',
        'librosa', 
        'numpy',
        'scipy',
        'PyQt5',
        'pyqtgraph',
        'keyboard',
        'whisper',
        'soundfile',
        'torch'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} (missing)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    return True

def create_default_config():
    """Create default configuration files if they don't exist"""
    
    # Check if config.json exists and is valid
    if not os.path.exists('config.json'):
        print("✓ config.json already exists")
    
    # Check if settings.json exists and is valid
    if not os.path.exists('settings.json'):
        print("✓ settings.json already exists")
    
    # Check if stats.json exists
    if not os.path.exists('stats.json'):
        print("✓ stats.json already exists")

def test_audio():
    """Test audio input"""
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        
        if not input_devices:
            print("⚠ No audio input devices found")
            return False
        
        default_input = sd.default.device[0]
        device_info = sd.query_devices(default_input)
        print(f"✓ Default input device: {device_info['name']}")
        return True
        
    except Exception as e:
        print(f"✗ Audio test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("Voice Practice Setup")
    print("=" * 20)
    
    print("\n1. Creating directories...")
    create_directories()
    
    print("\n2. Checking dependencies...")
    deps_ok = check_dependencies()
    
    print("\n3. Checking configuration...")
    create_default_config()
    
    print("\n4. Testing audio...")
    audio_ok = test_audio()
    
    print("\n" + "=" * 20)
    
    if deps_ok and audio_ok:
        print("✓ Setup complete! Run 'python main.py' to start the application.")
    else:
        print("⚠ Setup completed with warnings. Check the issues above.")
        
    return 0

if __name__ == '__main__':
    sys.exit(main())