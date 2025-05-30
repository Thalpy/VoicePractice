import sounddevice as sd
import numpy as np
import librosa

# Audio stream config
BUFFER_SIZE = 2048
SAMPLERATE = 22050
FRAME_DURATION = BUFFER_SIZE / SAMPLERATE

# Target pitch range (cis female default)
TARGET_MIN = 165.0
TARGET_MAX = 255.0

def estimate_pitch(audio):
    try:
        f0 = librosa.yin(audio, fmin=80, fmax=400, sr=SAMPLERATE)
        pitch = float(np.median(f0))
        return pitch
    except Exception as e:
        print(f"Error estimating pitch: {e}")
        return 0.0

def audio_callback(indata, frames, time, status):
    if status:
        print(status, flush=True)
    mono = indata[:, 0]
    pitch = estimate_pitch(mono)
    if pitch > 50:
        if TARGET_MIN <= pitch <= TARGET_MAX:
            indicator = "✅"
        else:
            indicator = "❌"
        print(f"Pitch: {pitch:.2f} Hz {indicator}", flush=True)

def main():
    print("🎤 VoicePractice CLI Pitch Tester (librosa) — Press Ctrl+C to stop")
    with sd.InputStream(channels=1, callback=audio_callback,
                        blocksize=BUFFER_SIZE, samplerate=SAMPLERATE):
        try:
            while True:
                sd.sleep(1000)
        except KeyboardInterrupt:
            print("Stopped.")

if __name__ == "__main__":
    main()