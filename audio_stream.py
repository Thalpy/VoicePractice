import sounddevice as sd
import numpy as np
from pitch_analysis import get_pitch, update_rolling_buffer as update_pitch_buffer
from resonance_analysis import estimate_resonance, is_resonance_in_range, update_rolling_buffer as update_resonance_buffer
from intonation_analysis import update_pitch_history, evaluate_intonation
# Spectrogram will be passed externally via callback

SAMPLE_RATE = 22050
BUFFER_SIZE = 1024

# Optional: register external visualizers or consumers
spectrogram_updater = None
volume_callback = None

def set_volume_callback(func):
    global volume_callback
    volume_callback = func


def set_spectrogram_callback(func):
    global spectrogram_updater
    spectrogram_updater = func


def audio_callback(indata, frames, time, status):
    if status:
        print(status, flush=True)

    mono = indata[:, 0]

    # --- Volume ---
    level = np.max(np.abs(indata))
    if volume_callback:
        volume_callback(level)


    # --- Pitch ---
    pitch = get_pitch(mono)
    update_pitch_buffer(pitch)
    update_pitch_history(pitch)

    # --- Intonation ---
    evaluate_intonation()

    # --- Resonance ---
    centroid = estimate_resonance(mono)
    resonance_ok = is_resonance_in_range(centroid)
    update_resonance_buffer(resonance_ok)

    # --- Spectrogram ---
    if spectrogram_updater:
        spectrogram_updater(mono)


def start_stream():
    stream = sd.InputStream(
        channels=1,
        callback=audio_callback,
        blocksize=BUFFER_SIZE,
        samplerate=SAMPLE_RATE
    )
    stream.start()
    return stream