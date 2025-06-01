import numpy as np
import time

# === Resonance Tracking (Spectral Centroid Proxy) ===
SAMPLE_RATE = 22050
ROLLING_WINDOW_SECONDS = 60
TARGET_CENTROID_MIN = 2500  # Hz
TARGET_CENTROID_MAX = 3500  # Hz

_resonance_buffer = []  # List of (timestamp, in_range)
_latest_centroid = np.nan

def estimate_resonance(audio_frame):
    """Estimate spectral centroid (proxy for mask resonance zone)."""
    global _latest_centroid
    magnitude = np.abs(np.fft.rfft(audio_frame))
    freqs = np.fft.rfftfreq(len(audio_frame), 1.0 / SAMPLE_RATE)
    centroid = np.sum(freqs * magnitude) / (np.sum(magnitude) + 1e-6)
    _latest_centroid = centroid
    return centroid

def is_resonance_in_range(centroid):
    return TARGET_CENTROID_MIN <= centroid <= TARGET_CENTROID_MAX

def update_rolling_buffer(in_range, timestamp=None):
    global _resonance_buffer
    timestamp = timestamp or time.time()
    _resonance_buffer.append((timestamp, in_range))
    _resonance_buffer = [(t, r) for (t, r) in _resonance_buffer if t >= timestamp - ROLLING_WINDOW_SECONDS]

def get_resonance_score():
    if not _resonance_buffer:
        return 0.0
    in_range_count = sum(1 for (_, r) in _resonance_buffer if r)
    return 100.0 * in_range_count / len(_resonance_buffer)

def get_latest_centroid():
    return _latest_centroid
