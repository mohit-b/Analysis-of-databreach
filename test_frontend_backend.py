#!/usr/bin/env python3
"""
Test script to verify frontend-backend integration.
"""

import requests
import json
import time
import subprocess
import sys
from pathlib import Path

def test_api_endpoints():
    """Test all API endpoints."""
    base_url = "http://localhost:5001"
    
    print("🧪 Testing CyberGuard Frontend-Backend Integration")
    print("=" * 60)
    
    # Test 1: Sample data endpoint
    print("\n1️⃣ Testing sample data endpoint...")
    try:
        response = requests.get(f"{base_url}/api/sample-data", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Sample data endpoint working")
            print(f"   Sample CSV: {data['sample_csv'][:50]}...")
        else:
            print(f"❌ Sample data endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Sample data endpoint error: {e}")
        return False
    
    # Test 2: Single classification
    print("\n2️⃣ Testing single classification...")
    try:
        test_data = {
            'data': '2024-07-31T00:00:00,177.52.183.80,192.168.1.50,HTTPS,blocked,suspicious,ids,45164,"Mozilla/5.0",/login?backup.sql'
        }
        response = requests.post(f"{base_url}/api/classify", 
                               json=test_data, timeout=5)
        if response.status_code == 200:
            result = response.json()
            print("✅ Single classification working")
            print(f"   Status: {result['status']}")
            print(f"   Attack Type: {result['attack_type']}")
            print(f"   Reason: {result['reason'][:50]}...")
        else:
            print(f"❌ Single classification failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Single classification error: {e}")
        return False
    
    # Test 3: JSON classification
    print("\n3️⃣ Testing JSON classification...")
    try:
        json_data = {
            'data': '{"timestamp": "2024-04-07T00:00:00", "source_ip": "192.168.1.248", "dest_ip": "192.168.1.15", "protocol": "HTTP", "action": "allowed", "threat_label": "benign", "log_type": "application", "bytes_transferred": "20652", "user_agent": "Mozilla/5.0", "request_path": "/login"}'
        }
        response = requests.post(f"{base_url}/api/classify", 
                               json=json_data, timeout=5)
        if response.status_code == 200:
            result = response.json()
            print("✅ JSON classification working")
            print(f"   Status: {result['status']}")
            print(f"   Attack Type: {result['attack_type']}")
        else:
            print(f"❌ JSON classification failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ JSON classification error: {e}")
        return False
    
    # Test 4: Error handling
    print("\n4️⃣ Testing error handling...")
    try:
        invalid_data = {'data': 'invalid,input,format'}
        response = requests.post(f"{base_url}/api/classify", 
                               json=invalid_data, timeout=5)
        if response.status_code == 400:
            result = response.json()
            print("✅ Error handling working")
            print(f"   Error: {result['reason'][:50]}...")
        else:
            print(f"❌ Error handling failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error handling error: {e}")
        return False
    
    # Test 5: Main page
    print("\n5️⃣ Testing main page...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Main page accessible")
            if "CyberGuard" in response.text:
                print("✅ Frontend content loaded")
            else:
                print("⚠️ Frontend content may not be loading properly")
        else:
            print(f"❌ Main page failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Main page error: {e}")
        return False
    
    print("\n🎉 All tests passed! Frontend-Backend integration is working!")
    return True

def main():
    """Main test function."""
    print("Starting CyberGuard integration test...")
    
    # Wait a moment for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(2)
    
    # Test the API
    success = test_api_endpoints()
    
    if success:
        print("\n✨ Integration test completed successfully!")
        print("🌐 You can now access the web interface at: http://localhost:5001")
        print("💖 The beautiful girly interface is ready to use!")
    else:
        print("\n❌ Integration test failed!")
        print("🔧 Please check the server logs and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
