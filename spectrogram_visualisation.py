import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore  # ✅ This is the fix
import time

SAMPLE_RATE = 22050
WINDOW_SIZE = 1024
DISPLAY_SECONDS = 3
REFRESH_INTERVAL_MS = 30

class SpectrogramWidget(pg.GraphicsLayoutWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Spectrogram")
        self.setBackground('w')
        

        self.plot = self.addPlot()
        self.img = pg.ImageItem()
        self.plot.addItem(self.img)

        self.plot.setLimits(xMin=0, xMax=DISPLAY_SECONDS, yMin=0, yMax=8000)
        self.plot.setLabel('left', 'Frequency', units='Hz')
        self.plot.setLabel('bottom', 'Time', units='s')

        self.cmap = pg.colormap.get('inferno')
        self.img.setLookupTable(self.cmap.getLookupTable(nPts=256))


        self.img_array = np.zeros((WINDOW_SIZE // 2 + 1, DISPLAY_SECONDS * 100), dtype=np.float32)

    def update_spectrogram(self, audio_frame):
        spectrum = np.abs(np.fft.rfft(audio_frame))
        spectrum_db = 20 * np.log10(spectrum + 1e-6).astype(np.float32)

        # Transpose the buffer to scroll horizontally
        self.img_array = np.roll(self.img_array, -1, axis=1)
        self.img_array[:, -1] = spectrum_db[:self.img_array.shape[0]]

        # Better color levels and orientation
        self.img.setImage(self.img_array.T, autoLevels=False,
                        levels=(np.min(self.img_array), np.max(self.img_array)))
        self.img.setRect(QtCore.QRectF(0, 0, DISPLAY_SECONDS, 8000))


    def start(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.redraw)
        timer.start(REFRESH_INTERVAL_MS)
        self.timer = timer

    def redraw(self):
        pass
