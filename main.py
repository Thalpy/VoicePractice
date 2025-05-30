import sys
from PyQt5 import QtWidgets
from overlay_gui import VoicePracticeOverlay
from audio_stream import start_stream, set_spectrogram_callback
import keyboard

# Global toggle
overlay_window = None
stream = None

def toggle_overlay():
    global overlay_window, stream

    if overlay_window and overlay_window.isVisible():
        overlay_window.hide()
    else:
        if not overlay_window:
            overlay_window = VoicePracticeOverlay()
            set_spectrogram_callback(overlay_window.get_spectrogram_updater())
        if not stream:
            stream = start_stream()
        overlay_window.show()

def main():
    app = QtWidgets.QApplication(sys.argv)
    toggle_overlay()  # Start visible by default

    # Register global hotkey
    keyboard.add_hotkey('ctrl+shift+v', toggle_overlay)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
