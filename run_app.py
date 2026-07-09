#!/usr/bin/env python3
"""
AI Buddy Home Security System - Application Runner
This script starts the Flask application with proper configuration
"""

import os
import sys
import webbrowser
import time
import threading
from app import app

def open_browser():
    """Open browser after a short delay"""
    time.sleep(2)
    webbrowser.open('http://localhost:5000')

def main():
    """Main application runner"""
    print("🤖 AI Buddy Home Security System")
    print("=" * 40)
    print("Starting Flask application...")
    print("Web interface will open at: http://localhost:5000")
    print("Press Ctrl+C to stop the application")
    print("=" * 40)
    
    # Check if users directory exists
    if not os.path.exists('users'):
        os.makedirs('users')
        print("📁 Created users directory")
    
    # Start browser in a separate thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        # Start Flask app
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=False  # Disable reloader to prevent double startup
        )
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down AI Buddy...")
        print("Thank you for using AI Buddy Home Security System!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
