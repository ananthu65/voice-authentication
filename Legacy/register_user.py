import os
import sounddevice as sd
from scipy.io.wavfile import write, read
import numpy as np
from resemblyzer import preprocess_wav, VoiceEncoder
import noisereduce as nr

fs = 16000
NUM_SAMPLES = 3
RECORD_SECONDS = 5

def record_audio(filename, seconds=RECORD_SECONDS):
    print(f"Recording for {seconds} seconds... Say your password phrase clearly.")
    audio = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait()
    audio_int16 = (audio * 32767).astype('int16')
    write(filename, fs, audio_int16)
    print("Recording saved as", filename)

def reduce_noise(filename):
    rate, data = read(filename)
    data = data.astype(np.float32)
    # Simple noise estimate: first 0.5 sec as noise
    noise_sample = data[:int(rate * 0.5)]
    reduced = nr.reduce_noise(y=data, sr=rate, y_noise=noise_sample)
    # Normalize to int16 for embedding
    reduced = np.clip(reduced, -32768, 32767).astype(np.int16)
    write(filename, rate, reduced)
    return filename

def register_user():
    encoder = VoiceEncoder()
    user = input("Enter username: ").strip()
    if not user:
        print("Username cannot be empty.")
        return

    pw = input("Enter your voice password phrase (type here, then say aloud): ").strip()
    if not pw:
        print("Password phrase cannot be empty.")
        return

    user_dir = os.path.join("users", user)
    os.makedirs(user_dir, exist_ok=True)

    # Save the text password
    with open(os.path.join(user_dir, "pw.txt"), "w") as f:
        f.write(pw)

    for i in range(NUM_SAMPLES):
        filename = os.path.join(user_dir, f"password_{i}.wav")
        print(f"\nSample {i+1} of {NUM_SAMPLES}")
        input("Press Enter and then say your password phrase aloud...")
        record_audio(filename, seconds=RECORD_SECONDS)
        reduce_noise(filename)
        # Embed after denoise
        wav = preprocess_wav(filename)
        emb = encoder.embed_utterance(wav)
        np.save(os.path.join(user_dir, f"embedding_{i}.npy"), emb)
        print("Voice embedding saved.")

    print(f"\nUser '{user}' registered successfully with {NUM_SAMPLES} samples!")

if __name__ == "__main__":
    register_user() 
