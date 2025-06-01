import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore

SAMPLE_RATE = 22050
WINDOW_SIZE = 1024
DISPLAY_SECONDS = 3
REFRESH_INTERVAL_MS = 30

class SpectrogramWidget(pg.GraphicsLayoutWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Spectrogram")
        self.setBackground('w')

        # Main plot
        self.plot = self.addPlot()
        self.img = pg.ImageItem()
        self.plot.addItem(self.img)

        self.plot.setLimits(xMin=0, xMax=DISPLAY_SECONDS, yMin=0, yMax=8000)
        self.plot.setLabel('left', 'Frequency', units='Hz')
        self.plot.setLabel('bottom', 'Time', units='s')

        # Colormap
        self.cmap = pg.colormap.get('inferno')
        self.img.setLookupTable(self.cmap.getLookupTable(nPts=256))

        # Rolling buffer of spectrogram slices
        self.img_array = np.zeros((WINDOW_SIZE // 2 + 1, DISPLAY_SECONDS * 100), dtype=np.float32)

        # Reference overlays
        self.target_band = pg.LinearRegionItem(values=(2500, 3500), orientation=pg.LinearRegionItem.Horizontal, brush=(50, 200, 50, 50))
        self.target_band.setMovable(False)
        self.plot.addItem(self.target_band)

        self.pitch_band = pg.LinearRegionItem(values=(165, 255), orientation=pg.LinearRegionItem.Horizontal, brush=(200, 100, 0, 40))
        self.pitch_band.setMovable(False)
        self.plot.addItem(self.pitch_band)

        resonance_label = pg.TextItem(text="🎯 Mask Resonance Target", color='g')
        resonance_label.setPos(0.1, 3600)
        self.plot.addItem(resonance_label)

        pitch_label = pg.TextItem(text="Pitch Range", color='orange')
        pitch_label.setPos(0.1, 265)
        self.plot.addItem(pitch_label)

        # Noise floor modeling
        self.noise_floor_db = np.zeros(WINDOW_SIZE // 2 + 1, dtype=np.float32)
        self.noise_update_count = 0

    def update_spectrogram(self, audio_frame, is_silent=False):
        """
        Update the spectrogram with a new frame of audio.
        If silent, update the noise model instead.
        """
        spectrum = np.abs(np.fft.rfft(audio_frame))
        spectrum_db = 20 * np.log10(spectrum + 1e-6).astype(np.float32)

        if is_silent:
            # Update rolling noise model
            self.noise_floor_db = (
                self.noise_floor_db * self.noise_update_count + spectrum_db
            ) / (self.noise_update_count + 1)
            self.noise_update_count += 1

        # Subtract noise floor and clamp
        adjusted_db = spectrum_db - self.noise_floor_db
        adjusted_db = np.clip(adjusted_db, a_min=-40, a_max=60)

        # Scroll image buffer
        self.img_array = np.roll(self.img_array, -1, axis=1)
        self.img_array[:, -1] = adjusted_db[:self.img_array.shape[0]]

        # Display updated spectrogram
        self.img.setImage(self.img_array.T, autoLevels=False,
                          levels=(np.min(self.img_array), np.max(self.img_array)))
        self.img.setRect(QtCore.QRectF(0, 0, DISPLAY_SECONDS, 8000))

    def start(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.redraw)
        timer.start(REFRESH_INTERVAL_MS)
        self.timer = timer

    def redraw(self):
        pass  # Hook for future animation or refresh logic