import numpy as np
import time

# Configuration
WINDOW_DURATION = 5.0  # seconds per analysis window
ROLLING_WINDOW_SECONDS = 60
MIN_PITCH = 50.0
INTONATION_MIN_STD = 15.0  # Hz
INTONATION_MAX_STD = 25.0  # Hz

# Internal pitch history
_pitch_history = []  # List of (timestamp, pitch)
_intonation_windows = []  # List of (timestamp, in_range)
_latest_std = 0.0

def update_pitch_history(pitch, timestamp=None):
    global _pitch_history
    timestamp = timestamp or time.time()
    if pitch >= MIN_PITCH:
        _pitch_history.append((timestamp, pitch))
        # Prune to 60s
        cutoff = timestamp - ROLLING_WINDOW_SECONDS
        _pitch_history = [(t, p) for (t, p) in _pitch_history if t >= cutoff]


def evaluate_intonation(timestamp=None):
    """
    Every 5s, evaluate pitch variation in a window.
    """
    global _intonation_windows
    timestamp = timestamp or time.time()
    cutoff = timestamp - WINDOW_DURATION
    window_pitches = [p for (t, p) in _pitch_history if t >= cutoff]

    if len(window_pitches) < 5:
        return  # not enough data

    std_dev = np.std(window_pitches)
    in_range = INTONATION_MIN_STD <= std_dev <= INTONATION_MAX_STD
    _intonation_windows.append((timestamp, in_range))

    # Prune to 60s
    cutoff_60s = timestamp - ROLLING_WINDOW_SECONDS
    _intonation_windows = [(t, r) for (t, r) in _intonation_windows if t >= cutoff_60s]

    std_dev = np.std(window_pitches)
    _latest_std = std_dev

def get_intonation_score():
    if not _intonation_windows:
        return 0.0
    in_range_count = sum(1 for (_, ok) in _intonation_windows if ok)
    return 100.0 * in_range_count / len(_intonation_windows)

def get_latest_std():
    return _latest_std