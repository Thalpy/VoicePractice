import threading
import queue
import numpy as np
import sounddevice as sd
import whisper
import os
import time
import wave

from library import preprocessing, phones, resonance

# === CONFIGURATION ===
SAMPLE_RATE = 22050
BUFFER_DURATION = 5  # seconds
MIN_CLIP_DURATION = 1  # seconds
VOLUME_THRESHOLD = 0.02  # relative to max (0–1)

# === GLOBAL STATE ===
audio_queue = queue.Queue()
result_queue = queue.Queue()
model = whisper.load_model("base")

class LiveClipBuffer:
    def __init__(self, sample_rate=SAMPLE_RATE, buffer_duration=BUFFER_DURATION):
        self.sample_rate = sample_rate
        self.buffer_frames = int(sample_rate * buffer_duration)
        self.buffer = np.zeros(self.buffer_frames, dtype=np.float32)
        self.write_ptr = 0
        self.last_speech_time = time.time()
        self.lock = threading.Lock()

    def add_audio(self, data):
        with self.lock:
            length = len(data)
            if self.write_ptr + length > self.buffer_frames:
                shift = self.write_ptr + length - self.buffer_frames
                self.buffer = np.roll(self.buffer, -shift)
                self.write_ptr -= shift
            self.buffer[self.write_ptr:self.write_ptr+length] = data
            self.write_ptr += length

    def is_silence(self, data):
        return np.max(np.abs(data)) < VOLUME_THRESHOLD

    def get_clip(self):
        with self.lock:
            return np.copy(self.buffer[:self.write_ptr])

    def reset(self):
        with self.lock:
            self.buffer[:] = 0
            self.write_ptr = 0

def audio_callback(indata, frames, time_info, status):
    mono = indata[:, 0]
    clip_buffer.add_audio(mono)
    is_silent = clip_buffer.is_silence(mono)

    now = time.time()
    if not is_silent:
        clip_buffer.last_speech_time = now
    elif now - clip_buffer.last_speech_time > 0.3 and clip_buffer.write_ptr > SAMPLE_RATE * MIN_CLIP_DURATION:
        clip = clip_buffer.get_clip()
        audio_queue.put(clip)
        clip_buffer.reset()

clip_buffer = LiveClipBuffer()

class AnalysisWorker(threading.Thread):
    def __init__(self, audio_queue, result_queue):
        super().__init__(daemon=True)
        self.audio_queue = audio_queue
        self.result_queue = result_queue

    def run(self):
        while True:
            audio = self.audio_queue.get()
            try:
                rec_dir = './rec'
                os.makedirs(rec_dir, exist_ok=True)
                filepath = os.path.join(rec_dir, 'clip.wav')

                # Save to WAV
                with wave.open(filepath, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(SAMPLE_RATE)
                    int_audio = np.int16(audio * 32767)
                    wf.writeframes(int_audio.tobytes())

                if not os.path.exists(filepath):
                    print("[Worker Error] clip.wav not written.")
                    continue

                # Transcribe
                try:
                    result = model.transcribe(filepath, fp16=False)
                except Exception as e:
                    print("[Worker Error] Whisper transcription failed:", e)
                    continue

                transcript = result['text'].strip()
                if not transcript:
                    continue

                # Process
                with open(filepath, 'rb') as f:
                    audio_bytes = f.read()

                tsv = preprocessing.process(audio_bytes, transcript, rec_dir)
                data = phones.parse(tsv)
                resonance.compute_resonance(data)

                self.result_queue.put({
                    'phonemes': [
                        {
                            'phoneme': p['phoneme'],
                            'pitch': p['F'][0],
                            'resonance': p.get('resonance', None)
                        } for p in data['phones'] if p.get('F') and p['F'][0] and p.get('resonance')
                    ],
                    'medianPitch': data.get('medianPitch'),
                    'medianResonance': data.get('medianResonance')
                })

            except Exception as e:
                print("[Worker Error]", e)


# Start audio stream and worker
worker = AnalysisWorker(audio_queue, result_queue)
worker.start()

stream = sd.InputStream(
    channels=1,
    samplerate=SAMPLE_RATE,
    blocksize=1024,
    callback=audio_callback
)
stream.start()

print("🎤 Listening... Press Ctrl+C to stop.")

try:
    while True:
        if not result_queue.empty():
            result = result_queue.get()
            print("\n[NEW CLIP RESULT]\n")
            for p in result['phonemes']:
                print(f"{p['phoneme']}: Pitch={p['pitch']:.1f}, Res={p['resonance']:.2f}")
            print(f"Median Pitch: {result['medianPitch']:.1f} Hz")
            print(f"Median Resonance: {result['medianResonance']:.2f}")
        time.sleep(0.1)
except KeyboardInterrupt:
    stream.stop()
    print("\nStopped.")