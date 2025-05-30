from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg
from spectrogram_visualisation import SpectrogramWidget
from pitch_analysis import get_pitch_score, get_latest_pitch
from resonance_analysis import get_resonance_score, get_latest_centroid
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
        self.pitch_value_label = QtWidgets.QLabel("Pitch: — Hz")
        self.layout.addWidget(self.pitch_value_label)

        self.resonance_label = QtWidgets.QLabel("Resonance: ...")
        self.resonance_value_label = QtWidgets.QLabel("Resonance: — Hz")
        self.layout.addWidget(self.resonance_value_label)

        self.intonation_label = QtWidgets.QLabel("Intonation: ...")
        self.pitch_plot = pg.PlotWidget(title="Pitch (Hz)")
        self.pitch_plot.setYRange(50, 400)
        self.pitch_curve = self.pitch_plot.plot(pen='y')
        self.layout.addWidget(self.pitch_plot)

        self.pitch_history = []

        input_device_index = sd.default.device[0]
        device_name = sd.query_devices(input_device_index)['name']
        self.device_label = QtWidgets.QLabel(f"Mic: {device_name}")

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
        current_pitch = get_latest_pitch()
        self.pitch_value_label.setText(f"Current pitch: {current_pitch:.1f} Hz")

        self.resonance_label.setText(f"Resonance in range: {res:.1f}%")
        centroid = get_latest_centroid()
        self.resonance_value_label.setText(f"Current resonance: {centroid:.0f} Hz")

        self.intonation_label.setText(f"Intonation healthy: {into:.1f}%")
        self.pitch_history.append(current_pitch)
        if len(self.pitch_history) > 100:
            self.pitch_history.pop(0)
        self.pitch_curve.setData(self.pitch_history)


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