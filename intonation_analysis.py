import numpy as np
import time

# === Intonation Detection (Pitch Variation) ===
ROLLING_WINDOW_SECONDS = 60
WINDOW_DURATION = 5.0  # seconds
INTONATION_MIN_STD = 15.0  # Hz
INTONATION_MAX_STD = 25.0  # Hz
MIN_PITCH = 50.0

_pitch_history = []          # (timestamp, pitch)
_intonation_windows = []     # (timestamp, is_in_range)
_latest_std = np.nan

def update_pitch_history(pitch, timestamp=None):
    global _pitch_history
    timestamp = timestamp or time.time()
    if pitch >= MIN_PITCH:
        _pitch_history.append((timestamp, pitch))
        _pitch_history = [(t, p) for (t, p) in _pitch_history if t >= timestamp - ROLLING_WINDOW_SECONDS]

def evaluate_intonation(timestamp=None):
    global _intonation_windows, _latest_std
    timestamp = timestamp or time.time()
    window_pitches = [p for (t, p) in _pitch_history if t >= timestamp - WINDOW_DURATION]

    if len(window_pitches) < 5:
        return  # Not enough data

    std_dev = np.std(window_pitches)
    _latest_std = std_dev
    in_range = INTONATION_MIN_STD <= std_dev <= INTONATION_MAX_STD
    _intonation_windows.append((timestamp, in_range))
    _intonation_windows = [(t, r) for (t, r) in _intonation_windows if t >= timestamp - ROLLING_WINDOW_SECONDS]

def get_intonation_score():
    if not _intonation_windows:
        return 0.0
    return 100.0 * sum(1 for (_, ok) in _intonation_windows if ok) / len(_intonation_windows)

def get_latest_std():
    return _latest_std
