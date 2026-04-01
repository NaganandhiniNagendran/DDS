#!/usr/bin/env python3
"""
Driver Drowsiness Detection System - Startup Script
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_files = [
        'app.py',
        'drowsiness_detection.py',
        'requirements.txt',
        'templates/',
        'static/'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    # Check for dlib model
    if not Path('shape_predictor_68_face_landmarks.dat').exists():
        print("⚠️  Warning: Dlib facial landmark model not found!")
        print("   Please download shape_predictor_68_face_landmarks.dat")
        print("   from: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2")
        print("   and extract it to this directory.")
        print()
        return False
    
    return True

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def start_server():
    """Start the Flask server"""
    print("🚀 Starting Driver Drowsiness Detection System...")
    print("📡 Server starting on http://localhost:5000")
    print("🎥 Make sure your webcam is connected")
    print("🔊 Ensure your speakers are working for alerts")
    print()
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Open browser after a short delay
        def open_browser():
            time.sleep(2)
            webbrowser.open('http://localhost:5000')
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Start Flask app
        from app import app
        app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

def main():
    """Main entry point"""
    print("=" * 60)
    print("🛡️  Driver Drowsiness Detection System")
    print("=" * 60)
    print()
    
    # Check if we're in the right directory
    if not Path('app.py').exists():
        print("❌ Please run this script from the project directory")
        print("   (where app.py is located)")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please resolve the missing files before continuing")
        sys.exit(1)
    
    # Ask user if they want to install/update dependencies
    install_deps = input("📦 Check/install dependencies? (y/n): ").lower().strip()
    if install_deps in ['y', 'yes']:
        if not install_dependencies():
            sys.exit(1)
    
    # Start the server
    start_server()

if __name__ == '__main__':
    main()
