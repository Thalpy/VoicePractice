import numpy as np
import time
import librosa

# === Pitch Tracking Configuration ===
SAMPLE_RATE = 22050
TARGET_MIN = 165.0  # Hz (cis female range lower bound)
TARGET_MAX = 255.0  # Hz (cis female range upper bound)
ROLLING_WINDOW_SECONDS = 60

_pitch_buffer = []  # List of (timestamp, pitch)

def get_pitch(audio_frame):
    """Estimate pitch (Hz) using YIN algorithm."""
    try:
        f0 = librosa.yin(audio_frame, fmin=80, fmax=400, sr=SAMPLE_RATE)
        return float(np.median(f0))
    except Exception as e:
        print(f"[PitchAnalysis] Error: {e}")
        return 0.0

def update_rolling_buffer(pitch, timestamp=None):
    """Add pitch value to buffer and prune to 60s window."""
    global _pitch_buffer
    timestamp = timestamp or time.time()
    _pitch_buffer.append((timestamp, pitch))
    _pitch_buffer = [(t, p) for (t, p) in _pitch_buffer if t >= timestamp - ROLLING_WINDOW_SECONDS]

def get_pitch_score():
    """Return % of time pitch was in target range (last 60s)."""
    if not _pitch_buffer:
        return 0.0
    in_range = [1 for (_, p) in _pitch_buffer if TARGET_MIN <= p <= TARGET_MAX]
    return 100.0 * sum(in_range) / len(_pitch_buffer)

def get_latest_pitch():
    return _pitch_buffer[-1][1] if _pitch_buffer else np.nan

def is_pitch_in_range(pitch):
    return TARGET_MIN <= pitch <= TARGET_MAX
