import sys
import os
import traceback
from PyQt5 import QtWidgets, QtCore
import keyboard

from overlay_gui import VoicePracticeOverlay
from live_analysis_system import result_queue, start_stream, AnalysisWorker, audio_queue
from config_manager import config

def setup_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        config.get_setting('logs', './logs/'),
        config.get_setting('recordings', './rec/'),
        './examples'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def main():
    """Main application entry point with proper error handling"""
    try:
        # Setup application
        app = QtWidgets.QApplication(sys.argv)
        app.setApplicationName("Voice Practice")
        app.setApplicationVersion("1.0")
        
        # Setup directories
        setup_directories()
        
        # Start background analysis worker
        worker = AnalysisWorker(audio_queue, result_queue)
        worker.start()
        
        # Start audio stream
        stream = start_stream()
        
        # Create and show overlay
        overlay = VoicePracticeOverlay(result_queue=result_queue)
        overlay.show()
        
        # Setup hotkey for toggling overlay
        try:
            keyboard.add_hotkey('ctrl+shift+v', lambda: overlay.setVisible(not overlay.isVisible()))
        except Exception as e:
            print(f"[Main] Warning: Could not register hotkey: {e}")
        
        # Handle application exit
        def cleanup():
            try:
                stream.stop()
                worker.join(timeout=1.0)
            except Exception as e:
                print(f"[Main] Cleanup error: {e}")
        
        app.aboutToQuit.connect(cleanup)
        
        print("[Main] Voice Practice application started successfully")
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"[Main] Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
