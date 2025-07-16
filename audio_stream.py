import sounddevice as sd
import numpy as np

from pitch_analysis import get_pitch, update_rolling_buffer as update_pitch_buffer
from resonance_analysis import estimate_resonance, is_resonance_in_range, update_rolling_buffer as update_resonance_buffer
from intonation_analysis import update_pitch_history, evaluate_intonation

# === Config ===
SAMPLE_RATE = 22050
BUFFER_SIZE = 1024

# === External callbacks ===
spectrogram_updater = None
volume_callback = None
volume_threshold = 10  # default threshold (0–100 scale)

def set_volume_callback(func):
    global volume_callback
    volume_callback = func

def set_spectrogram_callback(func):
    global spectrogram_updater
    spectrogram_updater = func

def set_volume_threshold(threshold):
    global volume_threshold
    volume_threshold = threshold

def audio_callback(indata, frames, time, status):
    if status:
        print("[Audio Stream Warning]", status, flush=True)

    mono = indata[:, 0]  # mono channel only
    level = np.max(np.abs(mono))

    # --- Volume Feedback ---
    if volume_callback:
        volume_callback(level)

    # --- Pitch Tracking ---
    pitch = get_pitch(mono)
    update_pitch_buffer(pitch)
    update_pitch_history(pitch)

    # --- Intonation ---
    evaluate_intonation()

    # --- Resonance ---
    centroid = estimate_resonance(mono)
    resonance_ok = is_resonance_in_range(centroid)
    update_resonance_buffer(resonance_ok)

    # --- Spectrogram Update ---
    if spectrogram_updater:
        # Scale: level is from 0–1, threshold is 0–100
        is_silent = level * 100 < volume_threshold
        spectrogram_updater(mono, is_silent)

def start_stream():
    stream = sd.InputStream(
        channels=1,
        callback=audio_callback,
        blocksize=BUFFER_SIZE,
        samplerate=SAMPLE_RATE
    )
    stream.start()
    return stream
