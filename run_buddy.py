#!/usr/bin/env python3
"""
AI Buddy - Home Security Assistant
A voice-activated door security system with an expressive AI buddy interface.

This script runs the complete AI Buddy web application.
Make sure you have registered users before running this application.
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible (3.10 or 3.11)"""
    version = sys.version_info
    if version.major != 3 or version.minor < 10:
        print("❌ Error: This application requires Python 3.10 or 3.11")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask', 'numpy', 'resemblyzer', 'sounddevice', 
        'scipy', 'noisereduce', 'pyttsx3', 'whisper'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            print("✅ All packages installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing packages: {e}")
            return False
    
    return True

def check_users_directory():
    """Check if users directory exists and has registered users"""
    users_dir = Path('users')
    if not users_dir.exists():
        print("❌ Users directory not found!")
        print("   Please run register_user.py first to register users")
        return False
    
    user_dirs = [d for d in users_dir.iterdir() if d.is_dir()]
    if not user_dirs:
        print("❌ No registered users found!")
        print("   Please run register_user.py first to register users")
        return False
    
    print(f"✅ Found {len(user_dirs)} registered users:")
    for user_dir in user_dirs:
        print(f"   - {user_dir.name}")
    
    return True

def start_application():
    """Start the Flask application"""
    print("\n🚀 Starting AI Buddy Application...")
    print("   The web interface will open in your browser")
    print("   Press Ctrl+C to stop the application")
    print("\n" + "="*50)
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(2)
        webbrowser.open('http://localhost:5000')
    
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start Flask app
    try:
        from app import app
        app.run(debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\n👋 AI Buddy application stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        return False
    
    return True

def main():
    """Main function to run the AI Buddy application"""
    print("🤖 AI Buddy - Home Security Assistant")
    print("="*50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Check users directory
    if not check_users_directory():
        return False
    
    # Start application
    return start_application()

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
