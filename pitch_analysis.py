import numpy as np
import time
import librosa

# Configuration
SAMPLE_RATE = 22050
TARGET_MIN = 165.0  # Hz
TARGET_MAX = 255.0  # Hz
ROLLING_WINDOW_SECONDS = 60

# Internal pitch buffer
_pitch_buffer = []  # List of (timestamp, pitch)

def get_pitch(audio_frame):
    """
    Estimate pitch from a mono audio frame using librosa YIN.
    Returns pitch in Hz.
    """
    try:
        f0 = librosa.yin(audio_frame, fmin=80, fmax=400, sr=SAMPLE_RATE)
        pitch = float(np.median(f0))
        return pitch
    except Exception as e:
        print(f"[PitchAnalysis] Error estimating pitch: {e}")
        return 0.0

def update_rolling_buffer(pitch, timestamp=None):
    """
    Add new pitch sample to the rolling buffer.
    """
    global _pitch_buffer
    timestamp = timestamp or time.time()
    _pitch_buffer.append((timestamp, pitch))
    # Remove entries older than 60 seconds
    cutoff = timestamp - ROLLING_WINDOW_SECONDS
    _pitch_buffer = [(t, p) for (t, p) in _pitch_buffer if t >= cutoff]

def get_pitch_score():
    """
    Returns the % of time pitch was within the target range over last 60 seconds.
    """
    if not _pitch_buffer:
        return 0.0
    in_range = [1 for (_, p) in _pitch_buffer if TARGET_MIN <= p <= TARGET_MAX]
    return 100.0 * sum(in_range) / len(_pitch_buffer)

def get_latest_pitch():
    return _pitch_buffer[-1][1] if _pitch_buffer else 0.0


def is_pitch_in_range(pitch):
    return TARGET_MIN <= pitch <= TARGET_MAX
