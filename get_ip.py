#!/usr/bin/env python3
"""
Get IP Address for Mobile Access
This script helps you find your computer's IP address for mobile access.
"""

import socket
import subprocess
import platform
import sys

def get_local_ip():
    """Get the local IP address of this machine"""
    try:
        # Connect to a remote server to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def get_network_info():
    """Get network information based on OS"""
    system = platform.system().lower()
    
    if system == "windows":
        try:
            result = subprocess.run(['ipconfig'], capture_output=True, text=True, shell=True)
            return result.stdout
        except Exception:
            return "Could not get network info"
    elif system in ["linux", "darwin"]:  # Linux or macOS
        try:
            result = subprocess.run(['ifconfig'], capture_output=True, text=True)
            return result.stdout
        except Exception:
            return "Could not get network info"
    else:
        return "Unsupported operating system"

def main():
    print("🌐 AI Buddy - Mobile Access Setup")
    print("=" * 50)
    
    # Get local IP
    local_ip = get_local_ip()
    
    print(f"📱 Mobile Access URL:")
    print(f"   http://{local_ip}:5000")
    print()
    
    print("📋 Setup Instructions:")
    print("1. Make sure your phone is connected to the same WiFi network")
    print("2. Open your phone's browser")
    print(f"3. Go to: http://{local_ip}:5000")
    print("4. Allow microphone access when prompted")
    print()
    
    print("🔧 Troubleshooting:")
    print("- If the URL doesn't work, check your firewall settings")
    print("- Make sure both devices are on the same network")
    print("- Try restarting the AI Buddy server")
    print()
    
    print("📊 Network Information:")
    print("-" * 30)
    network_info = get_network_info()
    print(network_info)
    
    print("\n🚀 To start the server, run:")
    print("   python app.py")

if __name__ == "__main__":
    main()
