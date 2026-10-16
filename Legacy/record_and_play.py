import sounddevice as sd
from scipy.io.wavfile import write, read
import os

fs = 16000  # 16kHz is standard for speech

def record_audio(filename='output.wav', seconds=3):
    print("Recording for", seconds, "seconds...")
    audio = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait()
    write(filename, fs, audio)
    print("Recording saved as", filename)

def play_audio(filename='output.wav'):
    fs, data = read(filename)
    print("Playing back", filename)
    sd.play(data, fs)
    sd.wait()

if __name__ == '__main__':
    record_audio()
    play_audio()
