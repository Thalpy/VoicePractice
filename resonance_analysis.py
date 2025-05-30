import numpy as np
import time

# Constants for FFT and resonance
ROLLING_WINDOW_SECONDS = 60
TARGET_CENTROID_MIN = 2500  # Hz
TARGET_CENTROID_MAX = 3500  # Hz
SAMPLE_RATE = 22050
_latest_centroid = 0.0


# Internal resonance buffer
_resonance_buffer = []  # List of (timestamp, bool)

def estimate_resonance(audio_frame):
    """
    Estimate resonance using spectral centroid as proxy for mask resonance.
    Returns centroid frequency in Hz.
    """
    global _latest_centroid # HEE HOO BAD CODE!

    magnitude_spectrum = np.abs(np.fft.rfft(audio_frame))
    freqs = np.fft.rfftfreq(len(audio_frame), 1.0 / SAMPLE_RATE)
    centroid = np.sum(freqs * magnitude_spectrum) / np.sum(magnitude_spectrum + 1e-6)
    _latest_centroid = centroid  # Update the latest centroid
    return centroid

def is_resonance_in_range(centroid):
    return TARGET_CENTROID_MIN <= centroid <= TARGET_CENTROID_MAX

def update_rolling_buffer(in_range, timestamp=None):
    """
    Add new resonance sample (in range or not) to the rolling buffer.
    """
    global _resonance_buffer
    timestamp = timestamp or time.time()
    _resonance_buffer.append((timestamp, in_range))
    cutoff = timestamp - ROLLING_WINDOW_SECONDS
    _resonance_buffer = [(t, r) for (t, r) in _resonance_buffer if t >= cutoff]

def get_resonance_score():
    """
    Returns the % of time resonance was in range over last 60 seconds.
    """
    if not _resonance_buffer:
        return 0.0
    in_range_count = sum(1 for _, r in _resonance_buffer if r)
    return 100.0 * in_range_count / len(_resonance_buffer)

def get_latest_centroid():
    return _latest_centroid

