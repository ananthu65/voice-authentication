import os
import numpy as np
from resemblyzer import VoiceEncoder, preprocess_wav
import sounddevice as sd
from scipy.io.wavfile import write, read
import glob
from vosk import Model, KaldiRecognizer
import wave
import difflib
import noisereduce as nr
import pyttsx3
import time


fs = 16000
THRESHOLD = 0.7
RECORD_SECONDS = 5
VOSK_MODEL_PATH = "vosk-model-en-us-0.22"
USERS_DIR = 'users'

# TTS setup
def speak(text):
    print(f"[SAY]: {text}")
    engine = pyttsx3.init('sapi5')
    engine.say(text)
    engine.runAndWait()
    

def record_audio(filename, seconds=RECORD_SECONDS, prompt=""):
    if prompt:
        speak(prompt)
    print(f"Recording for {seconds} seconds... Please speak now.")
    audio = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait()
    audio_int16 = (audio * 32767).astype('int16')
    write(filename, fs, audio_int16)
    print("Recording saved as", filename)

def reduce_noise(filename):
    rate, data = read(filename)
    data = data.astype(np.float32)
    noise_sample = data[:int(rate * 0.5)]
    reduced = nr.reduce_noise(y=data, sr=rate, y_noise=noise_sample)
    reduced = np.clip(reduced, -32768, 32767).astype(np.int16)
    write(filename, rate, reduced)
    return filename

def transcribe_with_vosk(wav_file, model_path=VOSK_MODEL_PATH):
    if not os.path.isdir(model_path):
        raise Exception(f"Vosk model folder not found: {model_path}")
    wf = wave.open(wav_file, "rb")
    model = Model(model_path)
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)
    result_text = ""
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = eval(rec.Result())
            result_text += result.get("text", "") + " "
    final_result = eval(rec.FinalResult())
    result_text += final_result.get("text", "")
    return result_text.strip()

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def is_phrase_close(a, b, cutoff=0.8):
    ratio = difflib.SequenceMatcher(None, a, b).ratio()
    return ratio >= cutoff

def identify_user_and_password(test_audio='test.wav', users_dir=USERS_DIR):
    encoder = VoiceEncoder()
    wav = preprocess_wav(test_audio)
    test_emb = encoder.embed_utterance(wav)
    test_text = transcribe_with_vosk(test_audio).lower().strip()
    print(f"[VOSK Transcript] You said: '{test_text}'")
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
    print(f"[RESULT] Best match: {best_user} (Score: {best_score:.3f})")
    return best_user, best_score, test_text

def get_user_password(user, users_dir=USERS_DIR):
    pw_path = os.path.join(users_dir, user, "pw.txt")
    if not os.path.isfile(pw_path):
        return None
    with open(pw_path) as f:
        return f.read().strip().lower()

def main():
    speak("Hi user! Please say your password phrase after the beep.")
    speak("beep...")
    record_audio("test.wav", seconds=RECORD_SECONDS)
    reduce_noise("test.wav")

    matched_user, best_score, test_text = identify_user_and_password("test.wav", users_dir=USERS_DIR)

    if matched_user and best_score >= THRESHOLD:
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

if __name__ == "__main__":
    main()
