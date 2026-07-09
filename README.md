# AI Buddy - IoT Voice Authentication Smart Home Security System

AI Buddy is a group project that turns voice recognition into a smart home access-control prototype. The system identifies a person from their voice, checks the spoken password phrase, gives voice feedback, and shows the authentication state through an interactive web-based AI buddy interface.

The project started as a legacy command-line voice authentication system and was later developed into a full Flask web application with browser voice recording, user registration, authentication logs, mobile access support, and a smart-home/IoT access-control workflow.

## Team Members

- Ananthasagaran
- Piranavini
- Hebavarshana
- Harishraj

## Project Overview

This project is designed for a smart door security use case. A user registers their voice by recording three samples of a password phrase. During authentication, the system records a new voice sample, compares it with saved voice embeddings, transcribes the spoken phrase, and grants or denies access.

The current application handles the software side of the IoT system: voice authentication, access decision-making, logs, mobile access, and door-opening feedback. A physical IoT device such as an ESP32, Arduino, Raspberry Pi, relay module, or smart lock can be connected at the successful authentication point in `app.py`.

## Main Features

- Voice-based user authentication
- Speaker recognition using Resemblyzer voice embeddings
- Spoken password verification using OpenAI Whisper
- Noise reduction for cleaner audio samples
- Browser-based user registration with three voice samples
- AI Buddy animated interface with different emotional states
- Text-to-speech feedback using `pyttsx3`
- Authentication logs with admin-protected log page
- Registered user management
- Mobile access over the same Wi-Fi network
- Legacy CLI version kept for reference and comparison

## From Legacy Code to Full App

The `Legacy` folder contains the original command-line version of the system. It includes separate scripts for registering users and identifying speakers.

The full application improves the legacy version by adding:

- A Flask backend
- A responsive web interface
- In-browser audio recording
- User registration from the UI
- Real-time AI Buddy status updates
- Authentication log viewing
- Mobile browser support
- A clearer smart-home access workflow

## How It Works

1. The user enters a username and password phrase.
2. The user records three voice samples in the browser.
3. The backend reduces noise and creates voice embeddings.
4. During authentication, the system records a new voice sample.
5. Resemblyzer compares the new sample with saved embeddings.
6. Whisper transcribes the spoken password phrase.
7. The app compares the transcript with the saved phrase.
8. If both speaker and phrase match, access is granted and AI Buddy announces that the door is opening.
9. Authentication attempts are saved in the system logs.

## Technology Stack

- Python 3.10+
- Flask
- HTML, CSS, JavaScript
- Resemblyzer
- OpenAI Whisper
- NumPy
- SciPy
- sounddevice
- noisereduce
- pyttsx3
- Werkzeug

## Folder Structure

```text
voice-authentication/
|-- app.py                         # Main Flask backend and voice auth flow
|-- run_app.py                     # Starts the Flask app and opens the browser
|-- start_mobile.py                # Starts server with mobile access instructions
|-- get_ip.py                      # Shows local IP address for phone access
|-- register_user.py               # CLI user registration script
|-- identify_user.py               # CLI authentication script
|-- gui.py                         # Desktop GUI/reference implementation
|-- test_app.py                    # Test/helper script
|-- requirements.txt               # Python dependencies
|-- authentication_logs.json       # JSON authentication log data
|-- system_log.txt                 # Text-based system log
|-- templates/
|   |-- index.html                 # Main web interface
|   |-- logs.html                  # Admin log viewer page
|-- static/
|   |-- style.css                  # Web UI styling and AI Buddy animations
|   |-- script.js                  # Frontend logic, recording, UI updates
|-- users/
|   |-- username/
|       |-- embedding_0.npy        # Voice embedding sample 1
|       |-- embedding_1.npy        # Voice embedding sample 2
|       |-- embedding_2.npy        # Voice embedding sample 3
|       |-- password_0.wav         # Recorded password sample 1
|       |-- password_1.wav         # Recorded password sample 2
|       |-- password_2.wav         # Recorded password sample 3
|       |-- pw.txt                 # Saved password phrase
|-- mybuddy/
|   |-- index.html                 # New AI Buddy UI reference
|   |-- style.css
|   |-- script.js
|-- mybuddyold/
|   |-- index.html                 # Older AI Buddy UI reference
|   |-- style.css
|   |-- script.js
|-- Legacy/
    |-- README.md                  # Legacy project notes
    |-- register_user.py           # Original registration flow
    |-- identify_user.py           # Original authentication flow
    |-- requirements.txt
    |-- users/                     # Legacy saved voice profiles
```

## Installation

### Requirements

- Python 3.10 or 3.11
- Windows is recommended because the current text-to-speech setup uses SAPI5
- Working microphone
- Modern browser such as Chrome, Edge, or Firefox
- FFmpeg for Whisper audio processing
- Internet connection for first-time Whisper model download

### Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

If PyTorch CPU packages fail to install from `requirements.txt`, install the compatible CPU version from the official PyTorch instructions, then run the requirements command again.

## Running the Application

Start the main Flask app:

```bash
python app.py
```

Then open:

```text
http://localhost:5000
```

You can also use:

```bash
python run_app.py
```

For phone access on the same Wi-Fi network:

```bash
python start_mobile.py
```

or:

```bash
python get_ip.py
```

Then open the shown IP address on your phone browser and allow microphone access.

## Usage

### Register a User

1. Open the web app.
2. Go to the Register tab.
3. Enter a username.
4. Enter a voice password phrase.
5. Record three voice samples.
6. Submit the registration form.

### Authenticate

1. Go to the Authenticate tab.
2. Click Start Voice Authentication.
3. Say the registered password phrase clearly.
4. The system checks both the speaker identity and password phrase.
5. AI Buddy shows the result and gives voice feedback.

### View Logs

1. Open the Logs page from the navigation bar.
2. Enter the admin password configured in `app.py`.
3. View authentication attempts, success/failure state, confidence, and details.

## IoT Integration Note

The current project is an IoT smart-home security prototype. The software already performs the access-control decision. To connect a real door lock, add the hardware trigger after successful authentication in `process_voice_authentication()` inside `app.py`, where the app currently says:

```python
speak(f"Perfect! Welcome home, {matched_user}! Door is opening!")
```

At that point, the project can send a signal to an ESP32, Arduino, Raspberry Pi GPIO pin, relay module, MQTT broker, or smart-lock API.

## Important Security Notes

- Voice samples and embeddings are stored locally in the `users/` folder.
- Password phrases are stored in plain text in `pw.txt`.
- Change the default admin password in `app.py` before sharing or deploying.
- Do not commit real users' voice samples or passwords to a public GitHub repository.
- For production use, encrypt sensitive data and add stronger authentication controls.

## Troubleshooting

- If the microphone does not work, check browser and system microphone permissions.
- If Whisper is slow the first time, wait for the model to download and load.
- If voice matching is inaccurate, record samples in a quiet place and speak clearly.
- If phone access does not work, make sure the phone and computer are on the same Wi-Fi network.
- If port `5000` is already in use, stop the other app or change the Flask port in `app.py`.

## Project Status

This is an academic group project for demonstrating voice recognition, smart authentication, and an IoT-ready home security workflow.

