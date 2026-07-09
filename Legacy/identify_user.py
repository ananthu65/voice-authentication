import os
import numpy as np
from resemblyzer import VoiceEncoder, preprocess_wav
import sounddevice as sd
from scipy.io.wavfile import write, read
import glob
import difflib
import noisereduce as nr
import pyttsx3
import time
import whisper

# Constants
fs = 16000  # Sample rate
THRESHOLD = 0.5  # Lowered threshold for better speaker recognition (adjust as needed)
RECORD_SECONDS = 3  # Recording duration
USERS_DIR = 'users'  # Directory for user data

# Text to Speech function
def speak(text):
    print(f"[SAY]: {text}")
    engine = pyttsx3.init('sapi5')  # Initialize with Windows SAPI5
    engine.say(text)
    engine.runAndWait()

# Record audio function
def record_audio(filename, seconds=RECORD_SECONDS, prompt=""):
    if prompt:
        speak(prompt)
    print(f"Recording for {seconds} seconds... Please speak now.")
    audio = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait()  # Wait until recording is finished
    audio_int16 = (audio * 32767).astype(np.int16)
    write(filename, fs, audio_int16)
    print(f"Recording saved as {filename}")

# Reduce noise from audio (using a later segment for noise sample)
def reduce_noise(filename):
    rate, data = read(filename)
    data = data.astype(np.float32)
    noise_sample = data[int(rate * 0.5):int(rate * 1.0)]  # Use 0.5-1s as noise if silent
    if len(noise_sample) == 0:  # Fallback if segment is too short
        noise_sample = data[:int(rate * 0.5)]
    reduced = nr.reduce_noise(y=data, sr=rate, y_noise=noise_sample)
    reduced = np.clip(reduced, -32768, 32767).astype(np.int16)
    write(filename, rate, reduced)
    return filename

# Transcribe audio with Whisper
def transcribe_with_whisper(wav_file):
    model = whisper.load_model("medium")  # Use "base" for faster processing if needed
    result = model.transcribe(wav_file, language="en")
    return result["text"].strip().lower()

# Calculate cosine similarity between two vectors
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Check if two phrases are similar
def is_phrase_close(a, b, cutoff=0.8):
    ratio = difflib.SequenceMatcher(None, a, b).ratio()
    return ratio >= cutoff

# Identify speaker using Resemblyzer (show only best match name)
def identify_speaker(test_audio='test.wav', users_dir=USERS_DIR):
    encoder = VoiceEncoder()
    wav = preprocess_wav(test_audio)
    test_emb = encoder.embed_utterance(wav)
    best_user = None
    best_score = -1
    for user in os.listdir(users_dir):
        user_dir = os.path.join(users_dir, user)
        for emb_file in glob.glob(os.path.join(user_dir, "embedding_*.npy")):
            emb = np.load(emb_file)
            score = cosine_similarity(test_emb, emb)
            if score > best_score:
                best_score = score
                best_user = user
    print(f"[RESULT] Best match: {best_user}")  # Show only the best user's name
    return best_user, best_score

# Get user's password from file
def get_user_password(user, users_dir=USERS_DIR):
    pw_path = os.path.join(users_dir, user, "pw.txt")
    if not os.path.isfile(pw_path):
        return None
    with open(pw_path, 'r') as f:
        return f.read().strip().lower()

# Main function to run the authentication process
def main():
    speak("Hi user! Please say your password phrase after the beep.")
    speak("beep...")
    record_audio("test.wav", seconds=RECORD_SECONDS)
    reduce_noise("test.wav")

    # Step 1: Identify speaker first with Resemblyzer
    matched_user, best_score = identify_speaker("test.wav", users_dir=USERS_DIR)
    if matched_user and best_score >= THRESHOLD:
        speak(f"Speaker recognized as {matched_user}. Verifying password...")
        print(f"[Speaker] Recognized: {matched_user}")
        
        # Step 2: Transcribe and verify keyword with Whisper
        test_text = transcribe_with_whisper("test.wav")
        print(f"[Whisper Transcript] You said: '{test_text}'")
        correct_phrase = get_user_password(matched_user, users_dir=USERS_DIR)
        if correct_phrase and is_phrase_close(test_text, correct_phrase):
            result_msg = f"Door opens! Welcome, {matched_user}."
            speak(result_msg)
            time.sleep(4)
            print(f"✅ {result_msg}")
        else:
            speak("Access denied. Incorrect password phrase.")
            print("❌ Access denied. Incorrect password phrase.")
            time.sleep(2)
    else:
        speak("Access denied. Speaker not recognized.")
        print("❌ Access denied. Speaker not recognized.")
        time.sleep(2)

if __name__ == "__main__":  # Correct entry point
    main()
