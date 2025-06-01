import sys
from PyQt5 import QtWidgets
import keyboard

from overlay_gui import VoicePracticeOverlay
from live_analysis_system import result_queue, start_stream, AnalysisWorker, audio_queue

# Start background analysis worker
worker = AnalysisWorker(audio_queue, result_queue)
worker.start()

# Start audio stream
stream = start_stream()

def main():
    app = QtWidgets.QApplication(sys.argv)

    overlay = VoicePracticeOverlay(result_queue=result_queue)
    overlay.show()

    keyboard.add_hotkey('ctrl+shift+v', lambda: overlay.setVisible(not overlay.isVisible()))

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
