#!/usr/bin/env python3
"""
AI Buddy - Python 3.10 Installation Script
This script helps install and verify all dependencies for Python 3.10
"""

import sys
import subprocess
import platform
import os

def check_python_version():
    """Check if Python 3.10 is being used"""
    version = sys.version_info
    if version.major == 3 and version.minor == 10:
        print(f"✅ Python 3.10.{version.micro} detected - Perfect!")
        return True
    elif version.major == 3 and version.minor >= 10:
        print(f"⚠️  Python 3.{version.minor}.{version.micro} detected - Should work but 3.10 is recommended")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} detected - Python 3.10 required!")
        print("Please install Python 3.10 from https://www.python.org/downloads/")
        return False

def install_requirements():
    """Install all requirements from requirements.txt"""
    print("\n📦 Installing dependencies...")
    
    try:
        # Upgrade pip first
        print("Upgrading pip...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        
        # Install requirements
        print("Installing requirements from requirements.txt...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        
        print("✅ All dependencies installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def test_imports():
    """Test if all critical imports work"""
    print("\n🧪 Testing imports...")
    
    critical_modules = [
        "flask",
        "numpy", 
        "scipy",
        "whisper",
        "resemblyzer",
        "sounddevice",
        "noisereduce",
        "pyttsx3"
    ]
    
    failed_imports = []
    
    for module in critical_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        return False
    else:
        print("\n✅ All critical modules imported successfully!")
        return True

def test_whisper_model():
    """Test if Whisper can load a model"""
    print("\n🤖 Testing Whisper model loading...")
    
    try:
        import whisper
        print("Loading medium model (faster test)...")
        model = whisper.load_model("medium")
        print("✅ Whisper model loaded successfully!")
        return True
    except Exception as e:
        print(f"❌ Whisper model test failed: {e}")
        return False

def main():
    """Main installation process"""
    print("🚀 AI Buddy - Python 3.10 Installation Script")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check if requirements.txt exists
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found in current directory!")
        return False
    
    # Install requirements
    if not install_requirements():
        return False
    
    # Test imports
    if not test_imports():
        return False
    
    # Test Whisper
    if not test_whisper_model():
        print("⚠️  Whisper test failed, but app may still work with fallback")
    
    print("\n🎉 Installation completed successfully!")
    print("\n📋 Next steps:")
    print("1. Run: python app.py")
    print("2. Open browser to: http://localhost:5000")
    print("3. Register a user and test voice authentication")
    print("\n📱 For mobile access:")
    print("1. Find your IP address: ipconfig")
    print("2. Access from mobile: http://[YOUR_IP]:5000")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)