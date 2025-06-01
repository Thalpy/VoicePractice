from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg
import sounddevice as sd
import numpy as np
import os

from spectrogram_visualisation import SpectrogramWidget
from pitch_analysis import get_pitch_score, get_latest_pitch
from resonance_analysis import get_resonance_score, get_latest_centroid
from intonation_analysis import get_intonation_score, get_latest_std
from audio_stream import set_volume_threshold

SAMPLE_RATE = 10
MAX_HISTORY = SAMPLE_RATE * 10

class VoicePracticeOverlay(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 128);")
        self.setGeometry(100, 100, 1000, 1000)

        self.drag_position = None
        self.latest_volume = 0
        self.show_spectrogram = True

        # === Layout ===
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        # --- Draggable Bar ---
        self.drag_bar = QtWidgets.QLabel("VoicePractice Overlay")
        self.drag_bar.setFixedHeight(30)
        self.drag_bar.setStyleSheet("background-color: rgba(255, 255, 255, 30); color: white; padding-left: 8px;")
        self.layout.addWidget(self.drag_bar)

        # --- Pitch Plot ---
        self.pitch_plot = pg.PlotWidget(title="Pitch (Hz)")
        self.pitch_plot.setYRange(50, 400)
        self.pitch_plot.setLimits(xMin=-10, xMax=0, yMin=50, yMax=400)
        self.pitch_plot.setMouseEnabled(x=False, y=False)
        self.pitch_plot.getAxis("bottom").setLabel(text="Time (s)")
        self.pitch_plot.addLine(y=165, pen=pg.mkPen('g', width=1, style=QtCore.Qt.DashLine))
        self.pitch_plot.addLine(y=255, pen=pg.mkPen('g', width=1, style=QtCore.Qt.DashLine))
        self.pitch_curve = self.pitch_plot.plot(pen='y')
        self.pitch_history = [np.nan] * MAX_HISTORY
        self.layout.addWidget(self.pitch_plot)

        # --- Resonance Plot ---
        self.resonance_plot = pg.PlotWidget(title="Resonance (Centroid Hz)")
        self.resonance_plot.setYRange(1000, 5000)
        self.resonance_plot.setLimits(xMin=-10, xMax=0, yMin=1000, yMax=5000)
        self.resonance_plot.setMouseEnabled(x=False, y=False)
        self.resonance_plot.getAxis("bottom").setLabel(text="Time (s)")
        self.resonance_plot.addLine(y=2500, pen=pg.mkPen('c', width=1, style=QtCore.Qt.DashLine))
        self.resonance_plot.addLine(y=3500, pen=pg.mkPen('c', width=1, style=QtCore.Qt.DashLine))
        self.resonance_curve = self.resonance_plot.plot(pen='m')
        self.resonance_history = [np.nan] * MAX_HISTORY
        self.layout.addWidget(self.resonance_plot)

        # --- Intonation Plot ---
        self.intonation_plot = pg.PlotWidget(title="Intonation (Pitch Std Dev)")
        self.intonation_plot.setYRange(0, 50)
        self.intonation_plot.setLimits(xMin=-10, xMax=0, yMin=0, yMax=50)
        self.intonation_plot.setMouseEnabled(x=False, y=False)
        self.intonation_plot.getAxis("bottom").setLabel(text="Time (s)")
        self.intonation_plot.addLine(y=15, pen=pg.mkPen('y', width=1, style=QtCore.Qt.DashLine))
        self.intonation_plot.addLine(y=25, pen=pg.mkPen('y', width=1, style=QtCore.Qt.DashLine))
        self.intonation_curve = self.intonation_plot.plot(pen='c')
        self.intonation_std_history = [np.nan] * MAX_HISTORY
        self.layout.addWidget(self.intonation_plot)

        # --- Volume Threshold & Bar ---
        self.volume_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(10)
        self.volume_slider.setPageStep(5)  # Enables nudging
        self.volume_slider.valueChanged.connect(lambda v: set_volume_threshold(v))
        set_volume_threshold(self.volume_slider.value())
        self.layout.addWidget(QtWidgets.QLabel("Mic Sensitivity Threshold", styleSheet="color: white;"))
        self.layout.addWidget(self.volume_slider)

        self.volume_bar = QtWidgets.QProgressBar()
        self.volume_bar.setMaximum(100)
        self.volume_bar.setTextVisible(True)
        self.volume_bar.setFormat("Volume: %p%")
        self.layout.addWidget(self.volume_bar)

        # --- Device Label ---
        input_device_index = sd.default.device[0]
        device_name = sd.query_devices(input_device_index)['name']
        self.device_label = QtWidgets.QLabel(f"Mic: {device_name}")
        self.device_label.setStyleSheet("font-size: 14px; color: white;")
        self.layout.addWidget(self.device_label)

        # --- Spectrogram Toggle ---
        self.spectrogram_toggle = QtWidgets.QCheckBox("Show Spectrogram")
        self.spectrogram_toggle.setChecked(True)
        self.spectrogram_toggle.stateChanged.connect(self.toggle_spectrogram)
        self.layout.addWidget(self.spectrogram_toggle)

        # --- Spectrogram Widget ---
        self.spectrogram = SpectrogramWidget()
        self.layout.addWidget(self.spectrogram)

        # --- Timer for Updates ---
        self.time_history = np.linspace(-10, 0, MAX_HISTORY).tolist()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_indicators)
        self.timer.start(100)

    def toggle_spectrogram(self, state):
        self.spectrogram.setVisible(bool(state))

    def update_volume(self, level):
        try:
            value = int(np.clip(level, 0, 1) * 100)
        except Exception:
            value = 0
        self.latest_volume = value

    def update_indicators(self):
        pitch = get_latest_pitch()
        pitch_score = get_pitch_score()
        res_score = get_resonance_score()
        centroid = get_latest_centroid()
        into_score = get_intonation_score()
        std_dev = get_latest_std()

        threshold = self.volume_slider.value()
        input_level = self.latest_volume
        is_silent = input_level < threshold

        self.volume_bar.setValue(input_level)
        self.volume_bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {'green' if not is_silent else 'gold'}; }}")

        # Update Spectrogram
        if self.spectrogram.isVisible():
            self.spectrogram.update_spectrogram(audio_frame=np.zeros(1024), is_silent=is_silent)  # Placeholder

        # Update Graphs
        self.pitch_plot.setTitle(f"Pitch (Hz) — {pitch_score:.1f}% | {pitch:.1f} Hz")
        self.resonance_plot.setTitle(f"Resonance — {res_score:.1f}% | {centroid:.0f} Hz")
        self.intonation_plot.setTitle(f"Intonation — {into_score:.1f}% | {std_dev:.1f} Hz")

        self.pitch_history.pop(0)
        self.pitch_history.append(pitch if not is_silent else np.nan)
        self.pitch_curve.setData(self.time_history, self.pitch_history)

        self.resonance_history.pop(0)
        self.resonance_history.append(centroid if not is_silent else np.nan)
        self.resonance_curve.setData(self.time_history, self.resonance_history)

        self.intonation_std_history.pop(0)
        self.intonation_std_history.append(std_dev if not is_silent else np.nan)
        self.intonation_curve.setData(self.time_history, self.intonation_std_history)

    def get_spectrogram_updater(self):
        def conditional_update(audio, is_silent=False):
            if self.spectrogram.isVisible():
                self.spectrogram.update_spectrogram(audio, is_silent)
        return conditional_update


    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            widget = self.childAt(event.pos())
            if widget == self.drag_bar:
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
