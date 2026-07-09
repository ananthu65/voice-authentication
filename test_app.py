#!/usr/bin/env python3
"""
Test script for AI Buddy Home Security System
This script tests the basic functionality of the Flask app
"""

import requests
import json
import time
import os

def test_flask_app():
    """Test the Flask application endpoints"""
    base_url = "http://localhost:5000"
    
    print("🤖 Testing AI Buddy Home Security System")
    print("=" * 50)
    
    try:
        # Test 1: Home page
        print("1. Testing home page...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("   ✅ Home page loads successfully")
        else:
            print(f"   ❌ Home page failed: {response.status_code}")
            return False
        
        # Test 2: Get users
        print("2. Testing get users endpoint...")
        response = requests.get(f"{base_url}/get_users")
        if response.status_code == 200:
            users = response.json()
            print(f"   ✅ Users endpoint works: {len(users)} users found")
        else:
            print(f"   ❌ Get users failed: {response.status_code}")
        
        # Test 3: Get buddy state
        print("3. Testing buddy state endpoint...")
        response = requests.get(f"{base_url}/get_buddy_state")
        if response.status_code == 200:
            state = response.json()
            print(f"   ✅ Buddy state endpoint works: {state}")
        else:
            print(f"   ❌ Get buddy state failed: {response.status_code}")
        
        # Test 4: Set emotion
        print("4. Testing set emotion endpoint...")
        test_emotion = "happy"
        response = requests.post(f"{base_url}/set_emotion", 
                               json={"emotion": test_emotion})
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Set emotion works: {result}")
        else:
            print(f"   ❌ Set emotion failed: {response.status_code}")
        
        print("\n🎉 All basic tests passed!")
        print("\nTo test the full functionality:")
        print("1. Open http://localhost:5000 in your browser")
        print("2. Register a new user with voice samples")
        print("3. Test authentication with the AI Buddy")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app. Make sure it's running:")
        print("   python app.py")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'flask', 'numpy', 'resemblyzer', 'sounddevice', 
        'scipy', 'noisereduce', 'pyttsx3', 'whisper'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All dependencies are installed!")
        return True

def check_file_structure():
    """Check if all required files exist"""
    print("📁 Checking file structure...")
    
    required_files = [
        'app.py',
        'templates/index.html',
        'static/style.css',
        'static/script.js',
        'requirements.txt'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("\n✅ All required files are present!")
        return True

if __name__ == "__main__":
    print("🚀 AI Buddy Home Security System - Test Suite")
    print("=" * 60)
    
    # Check file structure
    if not check_file_structure():
        print("\n❌ File structure check failed. Please ensure all files are present.")
        exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependencies check failed. Please install missing packages.")
        exit(1)
    
    print("\n" + "=" * 60)
    print("🧪 Running Flask app tests...")
    print("Make sure the Flask app is running: python app.py")
    print("=" * 60)
    
    # Test Flask app
    if test_flask_app():
        print("\n🎉 All tests passed! Your AI Buddy system is ready to use!")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        exit(1)
