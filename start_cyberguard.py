#!/usr/bin/env python3
"""
CyberGuard Startup Script
Starts the beautiful web interface for the Data-Breach Activity Classifier.
"""

import webbrowser
import time
import threading
from app import app

def open_browser():
    """Open browser after a short delay."""
    time.sleep(2)
    webbrowser.open('http://localhost:5001')

def main():
    """Start the CyberGuard web interface."""
    print("🛡️  Starting CyberGuard - Beautiful Data Breach Activity Classifier")
    print("=" * 70)
    print("✨ Features:")
    print("   💖 Beautiful girly pink interface")
    print("   🔍 Single activity classification")
    print("   📊 Batch processing with drag & drop")
    print("   🎯 Real-time threat detection")
    print("   📱 Responsive design")
    print("=" * 70)
    print("🌐 Opening http://localhost:5001 in your browser...")
    print("💡 Press Ctrl+C to stop the server")
    print("=" * 70)
    
    # Open browser in a separate thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start the Flask server
    try:
        app.run(debug=False, host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        print("\n👋 CyberGuard stopped. Thank you for using our beautiful interface! 💖")

if __name__ == "__main__":
    main()
