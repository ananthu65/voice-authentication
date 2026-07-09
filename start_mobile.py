#!/usr/bin/env python3
"""
AI Buddy Mobile Server Starter
This script starts the AI Buddy server optimized for mobile access.
"""

import subprocess
import sys
import os
import socket
import time
import webbrowser
from threading import Timer

def get_local_ip():
    """Get the local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def open_browser(url):
    """Open browser after a delay"""
    time.sleep(2)
    try:
        webbrowser.open(url)
    except Exception:
        pass

def main():
    print("🤖 AI Buddy - Mobile Server")
    print("=" * 40)
    
    # Get IP address
    local_ip = get_local_ip()
    mobile_url = f"http://{local_ip}:5000"
    local_url = "http://localhost:5000"
    
    print(f"🌐 Server will be available at:")
    print(f"   Local:  {local_url}")
    print(f"   Mobile: {mobile_url}")
    print()
    
    print("📱 Mobile Setup:")
    print("1. Connect your phone to the same WiFi network")
    print("2. Open your phone's browser")
    print(f"3. Go to: {mobile_url}")
    print("4. Allow microphone access when prompted")
    print()
    
    # Open browser after delay
    Timer(3.0, open_browser, [local_url]).start()
    
    print("🚀 Starting server...")
    print("   Press Ctrl+C to stop the server")
    print("-" * 40)
    
    try:
        # Start the Flask app
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("\n🔧 Troubleshooting:")
        print("- Make sure all dependencies are installed: pip install -r requirements.txt")
        print("- Check if port 5000 is available")
        print("- Try running: python app.py")

if __name__ == "__main__":
    main()
