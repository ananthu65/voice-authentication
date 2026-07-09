# AI Buddy - Python 3.10 Deployment Guide

## 🚀 Quick Setup for Python 3.10 Laptop

### Prerequisites
- Python 3.10.x installed on the laptop
- Windows 10/11 (recommended)
- At least 4GB RAM available
- Internet connection for initial setup

### Step 1: Install Python 3.10
1. Download Python 3.10.x from [python.org](https://www.python.org/downloads/release/python-31011/)
2. **IMPORTANT**: Check "Add Python to PATH" during installation
3. Verify installation: `python --version` should show 3.10.x

### Step 2: Install Dependencies
```bash
# Navigate to the project directory
cd D:\PIR3.0\pir

# Upgrade pip first
python -m pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

### Step 3: Test Installation
```bash
# Test if all imports work
python -c "import whisper, resemblyzer, flask, numpy, scipy; print('All dependencies installed successfully!')"

# Run the app
python app.py
```

### Step 4: First Run Setup
- The first run will download the Whisper medium model (~1.5GB)
- This may take 2-3 minutes depending on internet speed
- Subsequent runs will be much faster

## 🔧 Troubleshooting Python 3.10 Issues

### Common Issues and Solutions:

#### 1. "No module named 'whisper'"
```bash
pip install openai-whisper==20240930
```

#### 2. "No module named 'resemblyzer'"
```bash
pip install resemblyzer==0.1.4
```

#### 3. PyTorch CPU version issues
```bash
pip install torch==2.0.1+cpu torchaudio==2.0.2+cpu --index-url https://download.pytorch.org/whl/cpu
```

#### 4. Audio device issues
```bash
pip install sounddevice==0.4.6
# Make sure microphone permissions are enabled
```

#### 5. Memory issues (if any)
The app now uses the medium model by default, which is optimized for speed and memory usage.

## 📱 Mobile Access Setup

### Find Laptop's IP Address:
```bash
# Windows Command Prompt
ipconfig

# Look for "IPv4 Address" under your WiFi adapter
# Example: 192.168.1.100
```

### Access from Mobile:
- Connect mobile to same WiFi network
- Open browser and go to: `http://[LAPTOP_IP]:5000`
- Example: `http://192.168.1.100:5000`

## 🎯 Performance Optimization for Python 3.10

### For Lower-End Laptops:
1. **Already optimized**: Uses medium model by default for speed

2. **Reduce audio quality for faster processing** (optional):
   - Edit `app.py` line 30
   - Change `fs = 16000` to `fs = 8000`

3. **Disable debug mode** (optional):
   - Edit `app.py` line 738
   - Change `app.run(debug=True, ...)` to `app.run(debug=False, ...)`

## 🔒 Security Notes

### For Production Use:
1. Change the admin password in `app.py` line 45
2. Use a production WSGI server instead of Flask dev server
3. Enable HTTPS for secure communication
4. Regularly update dependencies

## 📋 System Requirements

### Minimum:
- Python 3.10.x
- 4GB RAM
- 2GB free disk space
- Windows 10/11

### Recommended:
- Python 3.10.x
- 6GB+ RAM
- 3GB+ free disk space
- Windows 11
- SSD storage

## 🆘 Support

If you encounter issues:
1. Check Python version: `python --version`
2. Check pip version: `pip --version`
3. Verify all dependencies: `pip list`
4. Check console output for specific error messages
5. Ensure microphone permissions are granted

## 📝 Notes

- The app will automatically create necessary directories
- User data is stored in the `users/` folder
- Logs are stored in `system_log.txt`
- First-time setup may take 3-5 minutes due to model downloads
