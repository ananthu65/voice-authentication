# Voice Authentication System (Legacy)

A Python-based voice authentication system that combines speaker recognition and speech-to-text (STT) for access control. This legacy module contains the standalone desktop GUI application and command-line authentication utilities.

## Features

- **Desktop Graphical Interface:** Interactive GUI for user registration and real-time voice authentication.
- **Speaker Recognition:** Uses Resemblyzer to extract voice embeddings and identify users based on their acoustic characteristics.
- **Dual Speech-to-Text Support:**
  - **Offline STT (Desktop GUI):** Offline keyword transcription using the Vosk acoustic model (`vosk-model-en-us-0.22`).
  - **Whisper STT (CLI):** Speech-to-text transcription using OpenAI Whisper.
- **Noise Reduction:** Cleans microphone audio using spectral noise reduction with `noisereduce` before feature extraction and transcription.
- **Text-to-Speech:** Provides automated audio feedback using Windows SAPI5 through `pyttsx3`.
- **Multi-User Support:** Maintains individual user enrollment directories containing multiple voice embedding samples and stored passphrases.

## Requirements

- Python 3.10 or 3.11
- Windows operating system (required for SAPI5 text-to-speech)
- Microphone for audio input
- Vosk acoustic model: `vosk-model-en-us-0.22` (required for offline desktop GUI transcription)

## Installation

### 1. Install Dependencies

Navigate to the repository root and install the required Python packages:

```bash
pip install -r Legacy/requirements.txt
```

### 2. Download the Vosk Model

Download and extract the Vosk acoustic model `vosk-model-en-us-0.22` into the application root directory.

Ensure that the extracted folder is accessible at the path expected by the application configuration.

## Usage

### 1. Standalone Desktop GUI (Version 1)

Run the desktop GUI with offline Vosk speech recognition:

```bash
python Legacy/gui.py
```

From the GUI, you can:

- Register new users using three voice sample prompts.
- Perform live speaker verification and keyword matching.
- View real-time authentication logs in the interface.

### 2. Command-Line Interface (Whisper STT)

#### Register a New User

Run the registration script:

```bash
python Legacy/register_user.py
```

Follow the terminal prompts to:

1. Enter a username.
2. Record three baseline voice samples.
3. Set a password phrase.
4. Record the password phrase three times.

#### Authenticate a User

Run the Whisper-based authentication script:

```bash
python Legacy/identify_user.py
```

When prompted, speak your password phrase clearly after the beep.

The system will:

1. Record the voice sample and apply noise reduction.
2. Extract the speaker's voice embedding using Resemblyzer.
3. Compare the embedding against enrolled user profiles.
4. Transcribe the spoken passphrase using Whisper.
5. Evaluate speaker identity and phrase similarity.
6. Grant or deny access based on the authentication results.

### 3. Command-Line Interface (Offline Vosk STT)

Run the Vosk-based authentication script:

```bash
python Legacy/identify_user_vosk.py
```

This script performs voice authentication using local Vosk speech recognition, provided the required acoustic model is installed. Speech recognition can operate offline without sending audio to a cloud-based transcription service.

## Project Structure

```text
Legacy/
├── gui.py                   # Desktop GUI application
├── identify_user.py         # Whisper-based CLI authentication
├── identify_user_vosk.py    # Vosk-based CLI authentication
├── register_user.py         # CLI user registration
├── noise.py                 # Noise reduction utilities
├── record_and_play.py       # Audio recording and playback utilities
├── requirements.txt         # Python dependencies
└── README.md                # Legacy module documentation
```

## Configuration

Core parameters can be configured directly in the relevant Python scripts.

| Parameter | Description | Typical Value |
|---|---|---|
| `THRESHOLD` | Cosine similarity threshold for speaker recognition | `0.5`–`0.7` |
| `RECORD_SECONDS` | Duration of each audio recording | `3`–`5` seconds |
| `fs` | Audio sampling rate | `16000` Hz |
| `VOSK_MODEL_PATH` | Path to the downloaded Vosk model directory | `vosk-model-en-us-0.22` |

**Note:** These values are typical configuration examples. The actual values depend on the implementation in each script and may require adjustment for the recording environment.

## Dependencies

The system uses the following Python libraries:

- **`resemblyzer`** — Extracts voice embeddings for speaker recognition.
- **`vosk`** — Provides offline speech-to-text transcription.
- **`whisper`** — Provides speech-to-text transcription using OpenAI Whisper.
- **`sounddevice`** — Records audio from the microphone.
- **`scipy`** — Supports audio signal processing and input/output.
- **`noisereduce`** — Reduces background noise in recorded audio.
- **`pyttsx3`** — Provides offline text-to-speech functionality.
- **`numpy`** — Supports numerical operations and vector calculations.

For the complete dependency list and package versions, refer to `requirements.txt`.

## Security Notes

- **Local Storage:** Voice embeddings (`.npy`) and audio recordings (`.wav`) are stored locally in the `users/` directory.
- **Plain-Text Passphrases:** Passphrases are stored in plain-text files such as `pw.txt` for demonstration purposes. This approach is not suitable for production systems.
- **Threshold Configuration:** Speaker recognition thresholds should be calibrated for the microphone, background noise, and operating environment.
- **Biometric Privacy:** Voice recordings and voice embeddings are biometric data. Access to these files should be restricted, and unnecessary recordings should be deleted.
- **Authentication Limitations:** Voice similarity and passphrase matching alone do not guarantee secure identity verification. Production deployments should include appropriate anti-spoofing measures and secure credential storage.

## License

This project is intended for research, educational, and demonstration purposes. Add an explicit open-source license file, such as `LICENSE`, if you intend to distribute the project under a particular open-source license.