import os
import random
import sounddevice as sd
import soundfile as sf
import numpy as np
import time
from pitch_analysis import get_pitch, is_pitch_in_range
from resonance_analysis import estimate_resonance, is_resonance_in_range
from intonation_analysis import update_pitch_history, evaluate_intonation, get_intonation_score

EXAMPLES_DIR = "examples"
SAMPLE_RATE = 22050
BUFFER_SIZE = 1024


def play_audio_clip(file_path):
    data, fs = sf.read(file_path, dtype='float32')
    sd.play(data, fs)
    sd.wait()

def record_user_attempt(duration=3.0):
    print("🎙️ Now speak...", flush=True)
    audio = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
    sd.wait()
    return audio[:, 0]

def score_user_attempt(audio):
    pitch = get_pitch(audio)
    pitch_score = 100.0 if is_pitch_in_range(pitch) else 0.0

    centroid = estimate_resonance(audio)
    resonance_score = 100.0 if is_resonance_in_range(centroid) else 0.0

    # Use intonation module as live evaluation
    update_pitch_history(pitch)
    evaluate_intonation()
    intonation_score = get_intonation_score()

    avg_score = round((pitch_score + resonance_score + intonation_score) / 3, 2)
    return pitch_score, resonance_score, intonation_score, avg_score

def run_calibration():
    example_files = [f for f in os.listdir(EXAMPLES_DIR) if f.endswith(('.wav', '.mp3', '.ogg'))]
    random.shuffle(example_files)

    for file in example_files:
        path = os.path.join(EXAMPLES_DIR, file)
        print(f"\n📢 Repeat after this clip: {file}")
        play_audio_clip(path)

        user_audio = record_user_attempt()
        scores = score_user_attempt(user_audio)

        print(f"\nPitch: {scores[0]}%, Resonance: {scores[1]}%, Intonation: {scores[2]}%, Total: {scores[3]}%\n")

        cont = input("Press Enter for next clip, or type 'done' to finish: ")
        if cont.lower().strip() == 'done':
            break