# Voice Authentication System

A Python-based voice authentication system that combines speaker recognition and speech-to-text for secure access control.

## Features

- **Speaker Recognition**: Uses Resemblyzer to identify users by their voice characteristics
- **Speech-to-Text**: Transcribes spoken passwords using OpenAI Whisper
- **Noise Reduction**: Automatically reduces background noise from audio recordings
- **Text-to-Speech**: Provides audio feedback throughout the authentication process
- **Multi-user Support**: Supports multiple users with individual voice profiles and passwords

## Requirements

- Python 3.10 or 3.11
- Windows OS (uses SAPI5 for text-to-speech)
- Microphone for audio input
- Internet connection

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/voice-authentication.git
cd voice-authentication
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

### Registering a New User

1. Run the registration script:
```bash
python register_user.py
```

2. Follow the prompts to:
   - Enter a username
   - Record voice samples (3 recordings)
   - Set a password phrase
   - Record the password phrase (3 recordings)

### Authentication

1. Run the identification script:
```bash
python identify_user.py
```

2. When prompted, speak your password phrase clearly
3. The system will:
   - Record your voice
   - Identify you as a speaker
   - Transcribe what you said
   - Verify the password phrase
   - Grant or deny access

## Project Structure

```
voice-authentication/
├── identify_user.py      # Main authentication script
├── register_user.py      # User registration script
├── users/                # User data directory
│   ├── username1/
│   │   ├── embedding_0.npy
│   │   ├── embedding_1.npy
│   │   ├── embedding_2.npy
│   │   ├── password_0.wav
│   │   ├── password_1.wav
│   │   ├── password_2.wav
│   │   └── pw.txt
│   └── username2/
│       └── ...
├── test.wav             # Temporary audio file
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Configuration

You can adjust these parameters in the scripts:

- `THRESHOLD`: Speaker recognition threshold (default: 0.5)
- `RECORD_SECONDS`: Recording duration (default: 3 seconds)
- `fs`: Sample rate (default: 16000 Hz)

## Troubleshooting

### Common Issues

1. **Microphone not detected**: Ensure your microphone is connected and working
2. **Whisper download fails**: Check your internet connection
3. **Low recognition accuracy**: Try speaking more clearly or adjusting the threshold
4. **Audio quality issues**: Ensure you're in a quiet environment

### Dependencies

- `resemblyzer`: Voice embedding generation
- `whisper`: Speech-to-text transcription
- `sounddevice`: Audio recording
- `scipy`: Audio processing
- `noisereduce`: Background noise reduction
- `pyttsx3`: Text-to-speech
- `numpy`: Numerical operations

## Security Notes

- Voice data is stored locally in the `users/` directory
- Password phrases are stored as plain text in `pw.txt` files
- Consider encrypting sensitive data for production use
- Voice recognition is not 100% secure and should be used with additional security measures

## License

This project is open source. Feel free to modify and distribute according to your needs.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## Author

Created for voice authentication and speaker recognition research.
