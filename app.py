# Python 3.10+ compatibility
from __future__ import annotations

from flask import Flask, render_template, request, jsonify
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
import base64
import io
import threading
import random
import uuid
from werkzeug.utils import secure_filename
import json
from datetime import datetime
from typing import Optional, Tuple, Dict, Any, List

app = Flask(__name__)

# Constants
fs = 16000  # Sample rate
THRESHOLD = 0.5  # Lowered threshold for better speaker recognition (matching identify_user.py)
RECORD_SECONDS = 3  # Recording duration (matching identify_user.py)
USERS_DIR = 'users'  # Directogoinry for user data

# Global variables for buddy state
buddy_state = {
    'emotion': 'happy',
    'is_processing': False,
    'current_user': None,
    'is_dancing': False
}

# Log storage
LOGS_FILE = 'authentication_logs.json'
TEXT_LOG_FILE = 'system_log.txt'
ADMIN_PASSWORD = '123123123'

# Text-to-Speech function
def speak(text: str) -> None:
    print(f"[SAY]: {text}")
    engine = pyttsx3.init('sapi5')  # Initialize with Windows SAPI5
    engine.say(text)
    engine.runAndWait()

# Record audio function
def record_audio(filename: str, seconds: int = RECORD_SECONDS, prompt: str = "") -> str:
    if prompt:
        speak(prompt)
    print(f"Recording for {seconds} seconds... Please speak now.")
    audio = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait()  # Wait until recording is finished
    audio_int16 = (audio * 32767).astype(np.int16)
    write(filename, fs, audio_int16)
    print(f"Recording saved as {filename}")
    return filename

# Reduce noise from audio (matching identify_user.py implementation)
def reduce_noise(filename: str) -> str:
    rate, data = read(filename)
    data = data.astype(np.float32)
    # Use first 0.5 seconds as noise sample (matching register_user.py)
    noise_sample = data[:int(rate * 0.5)]
    if len(noise_sample) == 0:  # Fallback if segment is too short
        noise_sample = data[int(rate * 0.5):int(rate * 1.0)]
    reduced = nr.reduce_noise(y=data, sr=rate, y_noise=noise_sample)
    reduced = np.clip(reduced, -32768, 32767).astype(np.int16)
    write(filename, rate, reduced)
    return filename

# Global Whisper model cache
_whisper_model = None

# Transcribe audio with Whisper (optimized for accuracy)
def transcribe_with_whisper(wav_file):
    global _whisper_model
    
    try:
        # Load model with caching for better performance
        if _whisper_model is None:
            print("[WHISPER] Loading medium model (fast and accurate for voice passwords)...")
            _whisper_model = whisper.load_model("medium")
            print("[WHISPER] Medium model loaded successfully!")
        
        # Optimized parameters for better transcription
        result = _whisper_model.transcribe(
            wav_file, 
            language="en",
            beam_size=5,           # Better beam search for accuracy
            best_of=5,             # Try multiple candidates
            temperature=0.0,       # Deterministic output
            compression_ratio_threshold=2.4,  # Reduce hallucinations
            logprob_threshold=-1.0,           # Filter low-confidence words
            no_speech_threshold=0.6,          # Better silence detection
            condition_on_previous_text=False,  # Don't bias based on previous text
            initial_prompt="The following is a voice password phrase for home security access."  # Context hint
        )
        
        # Clean up the transcription
        text = result["text"].strip().lower()
        
        # Remove common Whisper artifacts
        text = text.replace("...", "")
        text = text.replace("..", "")
        text = text.replace("  ", " ")
        
        # Get confidence score
        segments = result.get('segments', [])
        confidence = segments[0].get('avg_logprob', 0) if segments else 0
        
        print(f"[WHISPER DEBUG] Raw: '{result['text']}' -> Cleaned: '{text}'")
        print(f"[WHISPER DEBUG] Confidence: {confidence:.3f}")
        
        return text
        
    except Exception as e:
        print(f"[WHISPER ERROR] Failed to transcribe: {e}")
        return ""

# Calculate cosine similarity between two vectors
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Check if two phrases are similar (more flexible matching)
def is_phrase_close(a, b, cutoff=0.6):
    if not a or not b:
        return False
    
    # Normalize both phrases
    a_clean = a.strip().lower()
    b_clean = b.strip().lower()
    
    # Exact match
    if a_clean == b_clean:
        return True
    
    # Sequence similarity
    ratio = difflib.SequenceMatcher(None, a_clean, b_clean).ratio()
    
    # Word-based similarity (more flexible)
    a_words = set(a_clean.split())
    b_words = set(b_clean.split())
    
    if len(a_words) == 0 or len(b_words) == 0:
        return ratio >= cutoff
    
    # Calculate word overlap
    common_words = a_words.intersection(b_words)
    word_similarity = len(common_words) / max(len(a_words), len(b_words))
    
    # Use the higher of sequence similarity or word similarity
    final_similarity = max(ratio, word_similarity)
    
    print(f"[PHRASE MATCH] '{a_clean}' vs '{b_clean}' - Sequence: {ratio:.3f}, Words: {word_similarity:.3f}, Final: {final_similarity:.3f}")
    
    return final_similarity >= cutoff

# Log management functions
def load_logs():
    """Load authentication logs from file"""
    try:
        if os.path.exists(LOGS_FILE):
            with open(LOGS_FILE, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading logs: {e}")
        return []

def save_logs(logs):
    """Save authentication logs to file"""
    try:
        with open(LOGS_FILE, 'w') as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        print(f"Error saving logs: {e}")

def write_log(action, user=None, result=None, detail=None):
    """Write to text log file (exactly like gui.py)"""
    try:
        time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(TEXT_LOG_FILE, "a", encoding="utf-8") as f:
            line = f"{time_str} | {action.upper()} | "
            if user:
                line += f"User: {user} | "
            if result:
                line += f"Result: {result} | "
            if detail:
                line += f"Detail: {detail}"
            f.write(line.strip() + "\n")
        print(f"[LOG] {line.strip()}")  # Also print to console
    except Exception as e:
        print(f"Error writing log: {e}")

def add_log_entry(username, success, confidence=None, error_message=None, ip_address='unknown'):
    """Add a new log entry"""
    logs = load_logs()
    
    log_entry = {
        'id': str(uuid.uuid4()),
        'timestamp': datetime.now().isoformat(),
        'username': username,
        'success': success,
        'confidence': confidence,
        'error_message': error_message,
        'ip_address': ip_address
    }
    
    logs.append(log_entry)
    
    # Keep only last 100 entries to prevent file from growing too large
    if len(logs) > 100:
        logs = logs[-100:]
    
    save_logs(logs)
    
    # Also write to text log
    result = "Success" if success else "Failed"
    detail = error_message if error_message else f"Confidence: {confidence:.2f}" if confidence else None
    write_log("AUTH", user=username, result=result, detail=detail)
    
    return log_entry

# Identify speaker using Resemblyzer (improved reliability)
def identify_speaker(test_audio='test.wav', users_dir=USERS_DIR):
    encoder = VoiceEncoder()
    wav = preprocess_wav(test_audio)
    test_emb = encoder.embed_utterance(wav)
    
    user_scores = {}  # Store average scores per user
    
    for user in os.listdir(users_dir):
        user_dir = os.path.join(users_dir, user)
        if not os.path.isdir(user_dir):
            continue
            
        user_scores[user] = []
        
        # Compare against all embeddings for this user
        for emb_file in glob.glob(os.path.join(user_dir, "embedding_*.npy")):
            emb = np.load(emb_file)
            score = cosine_similarity(test_emb, emb)
            user_scores[user].append(score)
    
    # Find user with highest average score
    best_user = None
    best_avg_score = -1
    best_max_score = -1
    
    for user, scores in user_scores.items():
        if not scores:  # Skip users with no embeddings
            continue
            
        avg_score = np.mean(scores)
        max_score = np.max(scores)
        
        # Use both average and max score for better reliability
        combined_score = (avg_score * 0.7) + (max_score * 0.3)
        
        if combined_score > best_avg_score:
            best_avg_score = combined_score
            best_max_score = max_score
            best_user = user
    
    # Debug: Print all user scores for troubleshooting
    print(f"[DEBUG] All user scores:")
    for user, scores in user_scores.items():
        if scores:
            avg_score = np.mean(scores)
            max_score = np.max(scores)
            combined_score = (avg_score * 0.7) + (max_score * 0.3)
            print(f"  {user}: avg={avg_score:.3f}, max={max_score:.3f}, combined={combined_score:.3f}")
    
    print(f"[RESULT] Best match: {best_user} (avg: {best_avg_score:.3f}, max: {best_max_score:.3f})")
    return best_user, best_avg_score

# Get user's password from file
def get_user_password(user, users_dir=USERS_DIR):
    pw_path = os.path.join(users_dir, user, "pw.txt")
    if not os.path.isfile(pw_path):
        return None
    with open(pw_path, 'r') as f:
        return f.read().strip().lower()

# Process voice authentication
def process_voice_authentication(ip_address='unknown'):
    global buddy_state
    
    try:
        # Initial greeting with happy expression
        buddy_state['emotion'] = 'happy'
        speak("Hello! I'm your AI buddy. Please say your secret passcode after the beep.")
        time.sleep(2)
        
        # Set thinking state for voice recording
        buddy_state['is_processing'] = True
        buddy_state['emotion'] = 'thinking'
        speak("beep...")
        time.sleep(0.5)
        
        # Record audio - user says their password phrase
        record_audio("test.wav", seconds=RECORD_SECONDS)
        reduce_noise("test.wav")
        
        # Keep thinking while processing
        buddy_state['emotion'] = 'thinking'
        speak("Analyzing your voice and password...")
        time.sleep(2)
        
        # Step 1: Identify speaker using the same recording
        matched_user, best_score = identify_speaker("test.wav", users_dir=USERS_DIR)
        
        # Log identification attempt with confidence
        write_log("IDENTIFY", result=f"Attempted", detail=f"Best match: {matched_user}, Score: {best_score:.3f}, Threshold: {THRESHOLD}")
        
        if matched_user and best_score >= THRESHOLD:
            # User found - show surprise first
            buddy_state['current_user'] = matched_user
            buddy_state['emotion'] = 'surprised'
            speak(f"Speaker recognized as {matched_user}. Verifying password...")
            time.sleep(2)
            
            # Step 2: Transcribe and verify password using the SAME recording
            buddy_state['emotion'] = 'thinking'
            test_text = transcribe_with_whisper("test.wav")
            print(f"[Whisper Transcript] You said: '{test_text}'")
            correct_phrase = get_user_password(matched_user, users_dir=USERS_DIR)
            
            # Log transcription and phrase comparison
            phrase_ratio = difflib.SequenceMatcher(None, test_text, correct_phrase).ratio() if correct_phrase else 0
            write_log("TRANSCRIBE", user=matched_user, result=f"Transcript: '{test_text}'", detail=f"Expected: '{correct_phrase}', Similarity: {phrase_ratio:.3f}")
            
            if correct_phrase and is_phrase_close(test_text, correct_phrase):
                # Success - dancing!
                buddy_state['emotion'] = 'dancing'
                buddy_state['is_dancing'] = True
                speak(f"Perfect! Welcome home, {matched_user}! Door is opening!")
                
                # Log successful authentication (like gui.py)
                write_log("VERIFY", user=matched_user, result="Success")
                
                time.sleep(4)  # Let dancing animation play longer
                buddy_state['is_dancing'] = False
                buddy_state['emotion'] = 'happy'
                speak("Have a great day!")
                time.sleep(1)
            else:
                # Wrong password - sad
                buddy_state['emotion'] = 'sad'
                speak("Access denied. Incorrect password phrase.")
                
                # Log failed authentication (like gui.py)
                write_log("VERIFY", user=matched_user, result="Phrase mismatch")
                
                time.sleep(2)
                buddy_state['emotion'] = 'happy'
                speak("Please try again when you're ready.")
                time.sleep(1)
        else:
            # User not recognized - thinking then sad
            buddy_state['emotion'] = 'thinking'
            speak("Access denied. Speaker not recognized.")
            
            # Log failed authentication (like gui.py)
            write_log("VERIFY", result="No match", detail=f"You said: {test_text}")
            
            time.sleep(2)
            buddy_state['emotion'] = 'sad'
            speak("I'm sorry, I don't know who you are.")
            time.sleep(2)
            buddy_state['emotion'] = 'happy'
            speak("Please make sure you're registered first.")
            time.sleep(1)
            
    except Exception as e:
        print(f"Error in voice processing: {e}")
        buddy_state['emotion'] = 'sad'
        speak("Oh no! I encountered an error.")
        
        # Log error (like gui.py)
        write_log("VERIFY", result="Error", detail=f"System error: {str(e)}")
        
        time.sleep(2)
        buddy_state['emotion'] = 'happy'
        speak("Please try again.")
        time.sleep(1)
    finally:
        buddy_state['is_processing'] = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_authentication', methods=['POST'])
def start_authentication():
    global buddy_state
    
    # Capture IP address before starting background thread
    ip_address = request.remote_addr or 'unknown'
    
    # Log authentication request (like gui.py)
    write_log("AUTH", result="Started", detail=f"IP: {ip_address}")
    
    # Start voice processing in background
    thread = threading.Thread(target=process_voice_authentication, args=(ip_address,))
    thread.daemon = True
    thread.start()
    
    # Set initial state
    buddy_state['emotion'] = 'happy'
    
    return jsonify({'status': 'started', 'emotion': buddy_state['emotion']})

@app.route('/get_buddy_state')
def get_buddy_state():
    return jsonify(buddy_state)

@app.route('/set_emotion', methods=['POST'])
def set_emotion():
    data = request.get_json()
    emotion = data.get('emotion', 'happy')
    buddy_state['emotion'] = emotion
    return jsonify({'status': 'success', 'emotion': emotion})

@app.route('/register_user', methods=['POST'])
def register_user_web():
    try:
        username = request.form.get('username', '').strip()
        password_phrase = request.form.get('password_phrase', '').strip()
        
        if not username or not password_phrase:
            return jsonify({'success': False, 'message': 'Username and password phrase are required'})
        
        if len(username) < 3:
            return jsonify({'success': False, 'message': 'Username must be at least 3 characters long'})
        
        if len(password_phrase) < 5:
            return jsonify({'success': False, 'message': 'Password phrase must be at least 5 characters long'})
        
        # Check if user already exists
        user_dir = os.path.join(USERS_DIR, username)
        if os.path.exists(user_dir):
            return jsonify({'success': False, 'message': 'Username already exists'})
        
        # Create user directory
        os.makedirs(user_dir, exist_ok=True)
        
        # Save password phrase
        with open(os.path.join(user_dir, "pw.txt"), "w") as f:
            f.write(password_phrase.lower())
        
        # Process audio samples (matching register_user.py implementation)
        encoder = VoiceEncoder()
        audio_files = []
        
        for i in range(3):
            audio_key = f'audio_{i}'
            if audio_key not in request.files:
                return jsonify({'success': False, 'message': f'Missing audio sample {i+1}'})
            
            audio_file = request.files[audio_key]
            if audio_file.filename == '':
                return jsonify({'success': False, 'message': f'No audio file selected for sample {i+1}'})
            
            # Save audio file temporarily
            temp_filename = f"temp_{username}_{i}.wav"
            audio_file.save(temp_filename)
            
            try:
                # Process audio exactly like register_user.py
                reduce_noise(temp_filename)
                
                # Create embedding after denoise (matching register_user.py)
                wav = preprocess_wav(temp_filename)
                emb = encoder.embed_utterance(wav)
                
                # Save embedding
                np.save(os.path.join(user_dir, f"embedding_{i}.npy"), emb)
                
                # Save processed audio
                final_filename = os.path.join(user_dir, f"password_{i}.wav")
                os.rename(temp_filename, final_filename)
                audio_files.append(final_filename)
                
                print(f"Voice embedding {i+1} saved for user {username}")
                
            except Exception as e:
                # Clean up temp file
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
                return jsonify({'success': False, 'message': f'Error processing audio sample {i+1}: {str(e)}'})
        
        # Log successful registration (like gui.py)
        write_log("REGISTER", user=username, result="Success")
        
        return jsonify({
            'success': True, 
            'message': f'User {username} registered successfully with 3 voice samples',
            'username': username
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Registration failed: {str(e)}'})

@app.route('/get_users')
def get_users():
    try:
        if not os.path.exists(USERS_DIR):
            return jsonify([])
        
        users = []
        for user in os.listdir(USERS_DIR):
            user_dir = os.path.join(USERS_DIR, user)
            if os.path.isdir(user_dir):
                # Check if user has required files
                pw_file = os.path.join(user_dir, "pw.txt")
                emb_files = glob.glob(os.path.join(user_dir, "embedding_*.npy"))
                
                if os.path.exists(pw_file) and len(emb_files) >= 3:
                    users.append(user)
        
        return jsonify(users)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/delete_user', methods=['POST'])
def delete_user():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({'success': False, 'message': 'Username is required'})
        
        user_dir = os.path.join(USERS_DIR, username)
        
        if not os.path.exists(user_dir):
            return jsonify({'success': False, 'message': 'User not found'})
        
        # Remove user directory and all files
        import shutil
        shutil.rmtree(user_dir)
        
        return jsonify({'success': True, 'message': f'User {username} deleted successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to delete user: {str(e)}'})

@app.route('/test_voice', methods=['POST'])
def test_voice():
    """Test voice recognition without full authentication"""
    try:
        if 'audio' not in request.files:
            return jsonify({'success': False, 'message': 'No audio file provided'})
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'success': False, 'message': 'No audio file selected'})
        
        # Save temporary file
        temp_filename = f"test_voice_{uuid.uuid4().hex}.wav"
        audio_file.save(temp_filename)
        
        try:
            # Process audio
            reduce_noise(temp_filename)
            
            # Identify speaker
            matched_user, best_score = identify_speaker(temp_filename, users_dir=USERS_DIR)
            
            result = {
                'success': True,
                'matched_user': matched_user,
                'confidence': float(best_score) if best_score else 0.0,
                'threshold': THRESHOLD
            }
            
            if matched_user and best_score >= THRESHOLD:
                result['message'] = f'Voice recognized as {matched_user} (confidence: {best_score:.2f})'
            else:
                result['message'] = 'Voice not recognized'
            
            return jsonify(result)
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
                
    except Exception as e:
        return jsonify({'success': False, 'message': f'Voice test failed: {str(e)}'})

@app.route('/logs')
def logs_page():
    """Log details page"""
    return render_template('logs.html')

@app.route('/verify_admin', methods=['POST'])
def verify_admin():
    """Verify admin password for log access"""
    try:
        data = request.get_json()
        password = data.get('password', '').strip()
        
        if password == ADMIN_PASSWORD:
            return jsonify({'success': True, 'message': 'Access granted'})
        else:
            return jsonify({'success': False, 'message': 'Invalid password'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/get_logs')
def get_logs():
    """Get authentication logs (requires admin password)"""
    try:
        password = request.args.get('password', '')
        
        if password != ADMIN_PASSWORD:
            return jsonify({'success': False, 'message': 'Access denied'})
        
        # Read from text log file (like gui.py)
        logs = []
        try:
            with open(TEXT_LOG_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Parse log line: "2024-01-15 10:30:00 | AUTH | User: ananth | Result: Success | Detail: Confidence: 0.85"
                    parts = line.split(' | ')
                    if len(parts) >= 3:
                        timestamp = parts[0]
                        action = parts[1]
                        
                        # Parse user, result, and detail
                        user = None
                        result = None
                        detail = None
                        
                        for part in parts[2:]:
                            if part.startswith('User: '):
                                user = part[6:]
                            elif part.startswith('Result: '):
                                result = part[8:]
                            elif part.startswith('Detail: '):
                                detail = part[8:]
                        
                        # Determine success/failure
                        success = result == "Success" if result else False
                        
                        # Extract confidence from detail if available
                        confidence = None
                        if detail and "Confidence:" in detail:
                            try:
                                conf_str = detail.split("Confidence: ")[1].split()[0]
                                confidence = float(conf_str)
                            except:
                                pass
                        
                        log_entry = {
                            'id': f"log_{len(logs)}",
                            'timestamp': timestamp,
                            'username': user,
                            'success': success,
                            'confidence': confidence,
                            'error_message': detail if not success else None,
                            'ip_address': 'Unknown'
                        }
                        logs.append(log_entry)
        except FileNotFoundError:
            pass
        
        # Sort by timestamp (newest first)
        logs.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({'success': True, 'logs': logs})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error loading logs: {str(e)}'})

@app.route('/clear_logs', methods=['POST'])
def clear_logs():
    """Clear all logs (requires admin password)"""
    try:
        data = request.get_json()
        password = data.get('password', '')
        
        if password != ADMIN_PASSWORD:
            return jsonify({'success': False, 'message': 'Access denied'})
        
        # Clear text log file (like gui.py)
        with open(TEXT_LOG_FILE, 'w', encoding='utf-8') as f:
            f.write('')
        
        return jsonify({'success': True, 'message': 'Logs cleared successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error clearing logs: {str(e)}'})

if __name__ == '__main__':
    # Initialize buddy state
    buddy_state['emotion'] = 'happy'
    buddy_state['is_processing'] = False
    buddy_state['current_user'] = None
    buddy_state['is_dancing'] = False
    
    print("Starting AI Buddy Server...")
    print("Make sure you have registered users in the 'users' directory")
    print("🌐 Mobile Access:")
    print("   Local: http://localhost:5000")
    print("   Network: http://[YOUR_IP]:5000")
    print("   Mobile: Connect to same WiFi and use network IP")
    print("\n📱 To find your IP address:")
    print("   Windows: ipconfig")
    print("   Look for 'IPv4 Address' under your WiFi adapter")
    print("\n🚀 Starting server...")
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
