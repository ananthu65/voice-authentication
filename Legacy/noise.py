import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import read, write
import noisereduce as nr

# --- Load your raw (noisy) .wav file ---
rate, data = read('pass_1.wav')   # Change filename here!

# If stereo, convert to mono:
if len(data.shape) > 1:
    data = data.mean(axis=1)

# --- Apply Noise Reduction ---
noise_sample = data[:int(rate * 0.5)]  # First half second as noise sample
reduced = nr.reduce_noise(y=data, sr=rate, y_noise=noise_sample)

# --- Plot before & after waveforms ---
plt.figure(figsize=(12,5))
plt.subplot(2,1,1)
plt.plot(data, color='gray')
plt.title("Before Noise Reduction")
plt.ylabel("Amplitude")
plt.subplot(2,1,2)
plt.plot(reduced, color='blue')
plt.title("After Noise Reduction")
plt.ylabel("Amplitude")
plt.xlabel("Sample Index")
plt.tight_layout()
plt.show()

# --- (Optional) Save cleaned audio to new file ---
write('cleaned_recording.wav', rate, reduced.astype(np.int16))
