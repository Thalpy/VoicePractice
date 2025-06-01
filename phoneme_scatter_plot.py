from PyQt5 import QtWidgets
import pyqtgraph as pg
import numpy as np

class PhonemeScatterPlotWidget(pg.PlotWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setBackground('w')
        self.setLabel('left', 'Pitch (Hz)')
        self.setLabel('bottom', 'Resonance (Normalized)')
        self.setYRange(50, 400)
        self.setXRange(0, 1)
        self.addLegend(offset=(10, 10))

        self.phoneme_dots = []
        self.text_items = []
        self.trail_data = []  # stores (median_pitch, median_resonance)
        self.max_trail = 50

        # Scatter plots
        self.phoneme_scatter = pg.ScatterPlotItem(pen=pg.mkPen(None), brush='blue', size=10, name='Phonemes')
        self.average_marker = pg.ScatterPlotItem(pen=pg.mkPen(None), brush='red', size=14, name='Average')

        self.addItem(self.phoneme_scatter)
        self.addItem(self.average_marker)

    def update_plot(self, phonemes, median_pitch, median_resonance):
        self.clear_dots()

        # Add phoneme dots
        spots = []
        for p in phonemes:
            x = p['resonance']
            y = p['pitch']
            spots.append({'pos': (x, y), 'data': p})
            label = pg.TextItem(p['phoneme'], anchor=(0.5, 1.0), color=(0, 0, 0))
            label.setPos(x, y)
            self.addItem(label)
            self.text_items.append(label)

        self.phoneme_scatter.setData(spots)

        # Add to trail
        if median_pitch and median_resonance:
            self.trail_data.append((median_resonance, median_pitch))
            if len(self.trail_data) > self.max_trail:
                self.trail_data.pop(0)

            avg_res = np.mean([r for r, _ in self.trail_data])
            avg_pitch = np.mean([p for _, p in self.trail_data])

            self.average_marker.setData([{'pos': (avg_res, avg_pitch)}])

    def clear_dots(self):
        self.phoneme_scatter.clear()
        for item in self.text_items:
            self.removeItem(item)
        self.text_items.clear()

    def clear_all(self):
        self.clear_dots()
        self.trail_data.clear()
        self.average_marker.clear()
