#!/usr/bin/env python3
"""
Status check script for CyberGuard
"""

import requests
import sys

def check_server_status():
    """Check if the server is running and responding."""
    try:
        response = requests.get('http://localhost:5001/api/sample-data', timeout=3)
        if response.status_code == 200:
            print("✅ CyberGuard server is running successfully!")
            print("🌐 Web interface available at: http://localhost:5001")
            return True
        else:
            print(f"❌ Server responded with status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running or not accessible")
        print("💡 Start the server with: make run-frontend")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

def main():
    """Main status check."""
    print("🛡️  CyberGuard Status Check")
    print("=" * 40)
    
    if check_server_status():
        print("\n🎉 Everything is working perfectly!")
        print("💖 Your beautiful girly interface is ready to use!")
    else:
        print("\n🔧 Please start the server first:")
        print("   make run-frontend")
        sys.exit(1)

if __name__ == "__main__":
    main()






