from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg
from spectrogram_visualisation import SpectrogramWidget
from pitch_analysis import get_pitch_score
from resonance_analysis import get_resonance_score
from intonation_analysis import get_intonation_score
import os
import sounddevice as sd

class VoicePracticeOverlay(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 128);")
        self.setGeometry(100, 100, 600, 500)

        self.drag_position = None

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        def create_label_with_icon(icon_name, fallback_text):
            label = QtWidgets.QLabel()
            icon_path = os.path.join("assets", icon_name)
            if os.path.exists(icon_path):
                pixmap = QtGui.QPixmap(icon_path).scaled(24, 24, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                label.setPixmap(pixmap)
                label.setToolTip(fallback_text)
            else:
                label.setText(f"🎯 {fallback_text}")
            return label

        self.pitch_label = QtWidgets.QLabel("Pitch: ...")
        self.resonance_label = QtWidgets.QLabel("Resonance: ...")
        self.intonation_label = QtWidgets.QLabel("Intonation: ...")
        self.device_label = QtWidgets.QLabel(f"Mic: {sd.default.device[0]}")

        for label in [self.pitch_label, self.resonance_label, self.intonation_label, self.device_label]:
            label.setStyleSheet("font-size: 16px; color: white;")

        pitch_row = QtWidgets.QHBoxLayout()
        pitch_row.addWidget(create_label_with_icon("pitch.png", "Pitch"))
        pitch_row.addWidget(self.pitch_label)

        resonance_row = QtWidgets.QHBoxLayout()
        resonance_row.addWidget(create_label_with_icon("resonance.png", "Resonance"))
        resonance_row.addWidget(self.resonance_label)

        intonation_row = QtWidgets.QHBoxLayout()
        intonation_row.addWidget(create_label_with_icon("intonation.png", "Intonation"))
        intonation_row.addWidget(self.intonation_label)

        self.layout.addLayout(pitch_row)
        self.layout.addLayout(resonance_row)
        self.layout.addLayout(intonation_row)
        self.layout.addWidget(self.device_label)

        self.spectrogram = SpectrogramWidget()
        self.layout.addWidget(self.spectrogram)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_indicators)
        self.timer.start(500)

    def update_indicators(self):
        pitch = get_pitch_score()
        res = get_resonance_score()
        into = get_intonation_score()

        self.pitch_label.setText(f"Pitch in range: {pitch:.1f}%")
        self.resonance_label.setText(f"Resonance in range: {res:.1f}%")
        self.intonation_label.setText(f"Intonation healthy: {into:.1f}%")

    def get_spectrogram_updater(self):
        return self.spectrogram.update_spectrogram

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            event.accept()