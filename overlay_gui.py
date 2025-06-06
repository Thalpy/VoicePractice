from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg
from spectrogram_visualisation import SpectrogramWidget
from pitch_analysis import get_pitch_score, get_latest_pitch
from resonance_analysis import get_resonance_score, get_latest_centroid
from intonation_analysis import get_intonation_score
import os
import sounddevice as sd
import numpy as np

SAMPLE_RATE = 10  # samples per second (update every 100ms)
MAX_HISTORY = SAMPLE_RATE * 10  # 10 seconds

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
        self.setGeometry(100, 100, 600, 600)

        self.drag_position = None
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        def create_label_with_icon(icon_name, fallback_text):
            container = QtWidgets.QHBoxLayout()
            icon_path = os.path.join("assets", icon_name)
            icon_label = QtWidgets.QLabel()
            if os.path.exists(icon_path):
                pixmap = QtGui.QPixmap(icon_path).scaled(24, 24, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                icon_label.setPixmap(pixmap)
            else:
                icon_label.setText(f"🎯")
            text_label = QtWidgets.QLabel(fallback_text)
            text_label.setStyleSheet("font-size: 16px; color: white;")
            container.addWidget(icon_label)
            container.addWidget(text_label)
            return container, text_label

        self.latest_volume = 0
        # Metric labels with values
        pitch_row, self.pitch_label = create_label_with_icon("pitch.png", "Pitch: ...")
        self.pitch_value_label = QtWidgets.QLabel("— Hz")
        self.pitch_value_label.setStyleSheet("font-size: 16px; color: white;")
        pitch_row.addWidget(self.pitch_value_label)

        resonance_row, self.resonance_label = create_label_with_icon("resonance.png", "Resonance: ...")
        self.resonance_value_label = QtWidgets.QLabel("— Hz")
        self.resonance_value_label.setStyleSheet("font-size: 16px; color: white;")
        resonance_row.addWidget(self.resonance_value_label)

        intonation_row, self.intonation_label = create_label_with_icon("intonation.png", "Intonation: ...")
        self.intonation_value_label = QtWidgets.QLabel("—")
        self.intonation_value_label.setStyleSheet("font-size: 16px; color: white;")
        intonation_row.addWidget(self.intonation_value_label)

        self.layout.addLayout(pitch_row)
        self.layout.addLayout(resonance_row)
        self.layout.addLayout(intonation_row)

        self.pitch_plot = pg.PlotWidget(title="Pitch (Hz)")
        self.pitch_plot.setYRange(50, 400)
        self.pitch_plot.setLimits(xMin=-10, xMax=0, yMin=50, yMax=400)
        self.pitch_plot.setMouseEnabled(x=False, y=False)
        self.pitch_plot.getAxis("bottom").setLabel(text="Time (s)")
        self.pitch_plot.addLine(y=165, pen=pg.mkPen('g', width=1, style=QtCore.Qt.DashLine))
        self.pitch_plot.addLine(y=255, pen=pg.mkPen('g', width=1, style=QtCore.Qt.DashLine))
        self.pitch_curve = self.pitch_plot.plot(pen='y')

        self.pitch_history = [np.nan] * MAX_HISTORY
        self.time_history = np.linspace(-10, 0, MAX_HISTORY).tolist()

        self.layout.addWidget(self.pitch_plot)

        self.volume_slider_label = QtWidgets.QLabel("Mic Sensitivity Threshold")
        self.volume_slider_label.setStyleSheet("font-size: 14px; color: white;")
        self.volume_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(10)
        self.volume_slider.setStyleSheet("QSlider::groove:horizontal { background: #bbb; height: 4px; } QSlider::handle:horizontal { background: white; width: 10px; margin: -5px 0; }")
        self.volume_bar = QtWidgets.QProgressBar()
        self.volume_bar.setMaximum(100)
        self.volume_bar.setTextVisible(True)
        self.volume_bar.setFormat("Volume: %p%")

        self.layout.addWidget(self.volume_slider_label)
        self.layout.addWidget(self.volume_slider)
        self.layout.addWidget(self.volume_bar)

        input_device_index = sd.default.device[0]
        device_name = sd.query_devices(input_device_index)['name']
        self.device_label = QtWidgets.QLabel(f"Mic: {device_name}")
        self.device_label.setStyleSheet("font-size: 14px; color: white;")
        self.layout.addWidget(self.device_label)

        self.spectrogram = SpectrogramWidget()
        self.layout.addWidget(self.spectrogram)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_indicators)
        self.timer.start(100)

    def update_volume(self, level):
        try:
            value = int(np.clip(level, 0, 1) * 100)
        except Exception:
            value = 0
        self.latest_volume = value

    def update_indicators(self):
        pitch_score = get_pitch_score()
        res_score = get_resonance_score()
        into_score = get_intonation_score()

        pitch = get_latest_pitch()
        centroid = get_latest_centroid()

        threshold = self.volume_slider.value()

        input_level = self.latest_volume
        self.volume_bar.setValue(input_level)

        if input_level < threshold:
            pitch = np.nan

        self.pitch_label.setText(f"Pitch: {pitch_score:.1f}%")
        self.pitch_value_label.setText(f"{pitch:.1f} Hz" if not np.isnan(pitch) else "—")
        self.resonance_label.setText(f"Resonance: {res_score:.1f}%")
        self.resonance_value_label.setText(f"{centroid:.0f} Hz")
        self.intonation_label.setText(f"Intonation: {into_score:.1f}%")
        self.intonation_value_label.setText(f"{into_score:.1f}%")

        self.pitch_history.pop(0)
        self.pitch_history.append(pitch)
        self.pitch_curve.setData(self.time_history, self.pitch_history)

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
