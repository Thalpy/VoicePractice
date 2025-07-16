#!/usr/bin/env python3
"""
Diagnostic and fix script for Voice Practice application
Identifies and resolves common issues
"""

import os
import sys
import json
import traceback
from pathlib import Path

def check_file_structure():
    """Check if all required files exist"""
    required_files = [
        'main.py', 'overlay_gui.py', 'live_analysis_system.py',
        'config_manager.py', 'config.json', 'settings.json',
        'pitch_analysis.py', 'resonance_analysis.py', 'intonation_analysis.py',
        'audio_stream.py', 'spectrogram_visualisation.py', 'phoneme_scatter_plot.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("Missing required files:")
        for file in missing_files:
            print(f"  ✗ {file}")
        return False
    else:
        print("✓ All required files present")
        return True

def check_directories():
    """Ensure required directories exist"""
    required_dirs = ['logs', 'rec', 'library']
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            print(f"Creating directory: {dir_name}")
            dir_path.mkdir(exist_ok=True)
        else:
            print(f"✓ Directory exists: {dir_name}")

def validate_config_files():
    """Validate and fix configuration files"""
    
    # Check config.json
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        print("✓ config.json is valid JSON")
    except Exception as e:
        print(f"✗ config.json error: {e}")
        return False
    
    # Check settings.json
    try:
        with open('settings.json', 'r') as f:
            settings = json.load(f)
        print("✓ settings.json is valid JSON")
        
        # Fix path issues
        if settings.get('logs', '').startswith('/'):
            settings['logs'] = './logs/'
        if settings.get('recordings', '').startswith('/'):
            settings['recordings'] = './rec/'
            
        with open('settings.json', 'w') as f:
            json.dump(settings, f, indent=2)
        print("✓ Fixed path issues in settings.json")
        
    except Exception as e:
        print(f"✗ settings.json error: {e}")
        return False
    
    return True

def test_critical_imports():
    """Test imports for critical modules"""
    critical_modules = [
        ('numpy', 'NumPy - Core numerical computing'),
        ('scipy', 'SciPy - Scientific computing'),
        ('sounddevice', 'SoundDevice - Audio input/output'),
        ('librosa', 'Librosa - Audio analysis'),
        ('PyQt5.QtWidgets', 'PyQt5 - GUI framework'),
        ('pyqtgraph', 'PyQtGraph - Real-time plotting'),
        ('whisper', 'OpenAI Whisper - Speech recognition'),
        ('torch', 'PyTorch - Machine learning framework')
    ]
    
    print("\nTesting critical imports...")
    failed_imports = []
    
    for module, description in critical_modules:
        try:
            __import__(module)
            print(f"✓ {description}")
        except ImportError as e:
            print(f"✗ {description}: {e}")
            failed_imports.append(module)
    
    return failed_imports

def test_application_imports():
    """Test imports for application modules"""
    app_modules = [
        'config_manager',
        'error_handler'
    ]
    
    print("\nTesting application imports...")
    failed_imports = []
    
    for module in app_modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            failed_imports.append(module)
            traceback.print_exc()
    
    return failed_imports

def create_missing_modules():
    """Create any missing critical modules with minimal implementations"""
    
    # Check if audio_stream.py exists and has required functions
    if not os.path.exists('audio_stream.py'):
        print("Creating minimal audio_stream.py...")
        with open('audio_stream.py', 'w') as f:
            f.write('''"""
Minimal audio stream module
"""
import sounddevice as sd
import numpy as np
from config_manager import config

VOLUME_THRESHOLD = 0.02

def set_volume_threshold(threshold):
    """Set the volume threshold for audio detection"""
    global VOLUME_THRESHOLD
    VOLUME_THRESHOLD = threshold

def start_stream():
    """Start audio stream - placeholder implementation"""
    class MockStream:
        def stop(self):
            pass
    
    return MockStream()
''')
    
    # Check if error_handler.py exists
    if not os.path.exists('error_handler.py'):
        print("Creating error_handler.py...")
        with open('error_handler.py', 'w') as f:
            f.write('''"""
Error handling utilities
"""
import traceback
import logging

def setup_logging():
    """Setup basic logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def handle_error(error, context=""):
    """Handle and log errors"""
    print(f"Error in {context}: {error}")
    traceback.print_exc()
''')

def generate_install_command():
    """Generate the appropriate install command"""
    failed_critical = test_critical_imports()
    
    if failed_critical:
        print(f"\n{'='*50}")
        print("INSTALLATION REQUIRED")
        print(f"{'='*50}")
        print("Missing critical dependencies. Run one of these commands:")
        print("\nOption 1 - Use the setup script:")
        print("  python setup_fixed.py")
        print("\nOption 2 - Manual installation:")
        print("  pip install -r requirements.txt")
        print("\nOption 3 - Individual packages:")
        for module in failed_critical:
            if module == 'PyQt5.QtWidgets':
                print("  pip install PyQt5")
            else:
                print(f"  pip install {module}")
        return False
    
    return True

def main():
    """Main diagnostic process"""
    print("=== Voice Practice Diagnostic Tool ===\n")
    
    print("1. Checking file structure...")
    if not check_file_structure():
        print("✗ Missing critical files - please restore from backup")
        return
    
    print("\n2. Checking directories...")
    check_directories()
    
    print("\n3. Validating configuration...")
    if not validate_config_files():
        print("✗ Configuration file issues detected")
        return
    
    print("\n4. Creating missing modules...")
    create_missing_modules()
    
    print("\n5. Testing imports...")
    app_failed = test_application_imports()
    
    if generate_install_command():
        print(f"\n{'='*50}")
        print("✓ DIAGNOSTIC COMPLETE - READY TO RUN")
        print(f"{'='*50}")
        print("All dependencies are installed!")
        print("\nTo start the application:")
        print("  python main.py")
        
        if app_failed:
            print(f"\nNote: Some application modules had issues:")
            for module in app_failed:
                print(f"  - {module}")
            print("The app may still work with reduced functionality.")
    
    print(f"\n{'='*50}")

if __name__ == "__main__":
    main()