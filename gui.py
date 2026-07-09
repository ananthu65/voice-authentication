import os
import numpy as np
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
from tkinter import ttk
from resemblyzer import preprocess_wav, VoiceEncoder
import sounddevice as sd
from scipy.io.wavfile import write, read
import noisereduce as nr
import glob
from vosk import Model, KaldiRecognizer
import wave
import difflib
import pyttsx3
import threading
import time
from datetime import datetime
import winsound  # For beep (Windows)

# ===== Parameters =====
fs = 16000
NUM_SAMPLES = 3
RECORD_SECONDS = 5
THRESHOLD = 0.8   
USERS_DIR = 'users'
LOG_FILE = "system_log.txt"
VOSK_MODEL_PATH = "vosk-model-en-us-0.22"

# ===== Log Helper =====
def write_log(action, user=None, result=None, detail=None):
    time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        line = f"{time_str} | {action.upper()} | "
        if user:
            line += f"User: {user} | "
        if result:
            line += f"Result: {result} | "
        if detail:
            line += f"Detail: {detail}"
        f.write(line.strip() + "\n")

# ===== Helper Functions (TTS, Audio, Noise, etc.) =====
def speak(text):
    try:
        engine = pyttsx3.init('sapi5')
        engine.say(text)
        engine.runAndWait()
    except Exception:
        pass

def play_beep():
    try:
        winsound.Beep(800, 200)
    except:
        pass

def record_audio(filename, seconds=RECORD_SECONDS, prompt=""):
    if prompt:
        speak(prompt)
    audio = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait()
    audio_int16 = (audio * 32767).astype('int16')
    write(filename, fs, audio_int16)

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

def get_user_password(user, users_dir=USERS_DIR):
    pw_path = os.path.join(users_dir, user, "pw.txt")
    if not os.path.isfile(pw_path):
        return None
    with open(pw_path) as f:
        return f.read().strip().lower()

# ===== Registration with Main-thread Prompting =====
def register_user_gui():
    user = simpledialog.askstring("Register User", "Enter new username:")
    if not user:
        set_status("Registration cancelled.", "danger")
        write_log("REGISTER", user=None, result="Cancelled")
        return

    pw = simpledialog.askstring("Register User", "Enter your voice password phrase (type, then say aloud):")
    if not pw:
        set_status("Registration cancelled.", "danger")
        write_log("REGISTER", user=user, result="Cancelled")
        return

    def task():
        btn_register.config(state="disabled")
        btn_verify.config(state="disabled")
        btn_log.config(state="disabled")
        set_status("Registration started...", "primary")
        progressbar['value'] = 0
        progressbar.pack(pady=5)
        root.update()

        encoder = VoiceEncoder()
        user_dir = os.path.join(USERS_DIR, user)
        os.makedirs(user_dir, exist_ok=True)
        with open(os.path.join(user_dir, "pw.txt"), "w") as f:
            f.write(pw)

        for i in range(NUM_SAMPLES):
            sample_num = i + 1
            set_status(f"Recording sample {sample_num} of {NUM_SAMPLES}...", "warn")
            speak(f"Recording sample {sample_num}")
            progressbar['value'] = (i / NUM_SAMPLES) * 100
            root.update()
            filename = os.path.join(user_dir, f"password_{i}.wav")
            record_audio(filename, seconds=RECORD_SECONDS)
            set_status(f"Reducing noise (sample {sample_num})...", "warn")
            reduce_noise(filename)
            set_status(f"Saving embedding (sample {sample_num})...", "warn")
            wav = preprocess_wav(filename)
            emb = encoder.embed_utterance(wav)
            np.save(os.path.join(user_dir, f"embedding_{i}.npy"), emb)
            progressbar['value'] = ((i+1) / NUM_SAMPLES) * 100
            set_status(f"Sample {sample_num} recorded and saved.", "success")
            root.update()
            time.sleep(0.8)

        set_status(f"✅ User '{user}' registered with {NUM_SAMPLES} samples!", "success")
        speak(f"User {user} registered successfully!")
        write_log("REGISTER", user=user, result="Success")
        progressbar.pack_forget()
        btn_register.config(state="normal")
        btn_verify.config(state="normal")
        btn_log.config(state="normal")

    threading.Thread(target=task).start()

# ===== Verification: Smart gap, user-friendly output =====
def verify_user_gui():
    def task():
        btn_verify.config(state="disabled")
        btn_register.config(state="disabled")
        btn_log.config(state="disabled")
        set_status("Recording for verification...", "primary")
        progressbar['value'] = 0
        progressbar.pack(pady=5)
        root.update()
        speak("Please say your password phrase after the beep.")
        time.sleep(0.4)
        play_beep()
        record_audio("test.wav", seconds=RECORD_SECONDS)
        progressbar['value'] = 40
        set_status("Processing voice...", "primary")
        root.update()
        reduce_noise("test.wav")
        progressbar['value'] = 60

        # Speaker identification
        encoder = VoiceEncoder()
        wav = preprocess_wav("test.wav")
        test_emb = encoder.embed_utterance(wav)
        scores = []
        for user in os.listdir(USERS_DIR):
            user_dir = os.path.join(USERS_DIR, user)
            for emb_file in glob.glob(os.path.join(user_dir, "embedding_*.npy")):
                emb = np.load(emb_file)
                score = cosine_similarity(test_emb, emb)
                scores.append((user, score))
        if not scores:
            set_status("❌ No users enrolled.", "danger")
            set_output("Identified User: None\nNo users in system.")
            return

        scores.sort(key=lambda x: x[1], reverse=True)
        best_user, best_score = scores[0]
        if len(scores) > 1:
            second_user, second_score = scores[1]
        else:
            second_user, second_score = best_user, 0
        score_gap = best_score - second_score

        print(f"Best: {best_user} {best_score:.3f}, 2nd: {second_user} {second_score:.3f}, Gap: {score_gap:.3f}")  # DEBUG

        test_text = transcribe_with_vosk("test.wav", model_path=VOSK_MODEL_PATH).strip().lower()
        progressbar['value'] = 100
        root.update()
        time.sleep(0.3)
        progressbar.pack_forget()
        btn_verify.config(state="normal")
        btn_register.config(state="normal")
        btn_log.config(state="normal")

        # SMART GAP LOGIC
        if best_score >= THRESHOLD and (best_user == second_user or score_gap > 0.07):
            identified_user = best_user
            correct_phrase = get_user_password(identified_user, users_dir=USERS_DIR)
            if correct_phrase and is_phrase_close(test_text, correct_phrase):
                result_info = f" Access granted! Welcome, {identified_user}."
                set_status("✅ Access Granted!", "success")
                speak(result_info)
                write_log("VERIFY", user=identified_user, result="Success")
            else:
                result_info = f"❌ Access denied. Incorrect password phrase."
                set_status("❌ Wrong password!", "danger")
                speak("Access denied. Incorrect password phrase.")
                write_log("VERIFY", user=identified_user, result="Phrase mismatch")
        else:
            identified_user = "None"
            correct_phrase = ""
            result_info = f"❌ Access denied. Speaker not recognized."
            set_status("❌ Access denied. Speaker not recognized.", "danger")
            speak("Access denied. Speaker not recognized.")
            write_log("VERIFY", result="No match", detail=f"You said: {test_text}")

        expected_phrase_line = f"Expected: {correct_phrase}\n" if correct_phrase else ""
        set_output(
            f"Identified User: {identified_user}\n"
            f"You said: {test_text}\n"
            f"{expected_phrase_line}"
            f"{result_info}"
        )

    threading.Thread(target=task).start()

# ===== Log Viewer =====
def show_log_window():
    log_window = tk.Toplevel(root)
    log_window.title("System Log Viewer")
    log_window.geometry("650x400")
    log_window.config(bg="#222831")
    log_area = scrolledtext.ScrolledText(
        log_window, font=("Consolas", 11), bg="#232931", fg="#00adb5"
    )
    log_area.pack(fill="both", expand=True, padx=10, pady=10)
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            log_area.insert(tk.END, "".join(lines) if lines else "No log entries yet.")
    except FileNotFoundError:
        log_area.insert(tk.END, "No log entries yet.")
    log_area.config(state='disabled')

def set_status(msg, style="primary"):
    color_map = {
        "primary": "#00adb5",
        "success": "#43ea72",
        "danger": "#ef4444",
        "warn": "#ffc107"
    }
    result_label.config(text=msg, fg=color_map.get(style, "#00adb5"))
    result_label.update()

def set_output(msg):
    output_box.config(state='normal')
    output_box.delete(1.0, tk.END)
    output_box.insert(tk.END, msg)
    output_box.config(state='disabled')

# ===== Tkinter GUI Layout =====
root = tk.Tk()
root.title("🎤 Voice Password Recognition System")
root.geometry("760x470")
root.config(bg="#232931")

header = tk.Label(
    root,
    text="🔒 Voice Password Recognition",
    font=("Arial Rounded MT Bold", 23, "bold"),
    bg="#00adb5", fg="#222831",
    pady=18, bd=0
)
header.pack(fill="x")

btn_frame = tk.Frame(root, bg="#232931")
btn_frame.pack(pady=18)

btn_register = tk.Button(
    btn_frame,
    text="➕ Register (Enroll User)",
    width=22, height=2,
    font=("Arial", 12, "bold"),
    bg="#393e46", fg="#fff", activebackground="#00adb5", activeforeground="#222831",
    relief="flat",
    cursor="hand2",
    command=register_user_gui
)
btn_register.grid(row=0, column=0, padx=14)

btn_verify = tk.Button(
    btn_frame,
    text="🔑 Verify (Login/Unlock)",
    width=22, height=2,
    font=("Arial", 12, "bold"),
    bg="#393e46", fg="#fff", activebackground="#00adb5", activeforeground="#222831",
    relief="flat",
    cursor="hand2",
    command=verify_user_gui
)
btn_verify.grid(row=0, column=1, padx=14)

btn_log = tk.Button(
    btn_frame,
    text="📄 View Log",
    width=14, height=2,
    font=("Arial", 12, "bold"),
    bg="#393e46", fg="#fff", activebackground="#00adb5", activeforeground="#222831",
    relief="flat",
    cursor="hand2",
    command=show_log_window
)
btn_log.grid(row=0, column=2, padx=14)

result_label = tk.Label(
    root, text="Status: Idle", fg="#00adb5",
    bg="#232931", font=("Arial", 14, "bold"),
    pady=5
)
result_label.pack(pady=7)

progressbar = ttk.Progressbar(root, orient='horizontal', length=550, mode='determinate')
progressbar.pack_forget()

output_box = scrolledtext.ScrolledText(
    root, height=9, width=94,
    font=("Consolas", 12, "bold"),
    bg="#393e46", fg="#eeeeee", insertbackground="#eeeeee",
    borderwidth=0, relief="flat"
)
output_box.pack(pady=8)
output_box.insert(tk.END, "Recognized phrase/output will appear here.")
output_box.config(state='disabled')

footer = tk.Label(
    root,
    text="© 2025 Team 14 | Exhibition Demo",
    font=("Arial", 9, "bold"),
    fg="#7b8fa1", bg="#232931"
)
footer.pack(side=tk.BOTTOM, pady=6)

root.mainloop()
