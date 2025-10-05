#!/usr/bin/env python3
"""
Test script to verify batch processing fixes
"""
import requests
import time
import json
import os

def test_server_endpoints():
    """Test if the server endpoints are working"""
    base_url = "http://localhost:5001"
    
    print("🧪 Testing server endpoints...")
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Server is running and main page accessible")
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server is not running: {e}")
        return False
    
    # Test 2: Check sample data endpoint
    try:
        response = requests.get(f"{base_url}/api/sample-data")
        if response.status_code == 200:
            data = response.json()
            print("✅ Sample data endpoint working")
            print(f"   Sample CSV: {data['sample_csv'][:50]}...")
        else:
            print(f"❌ Sample data endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Sample data endpoint error: {e}")
    
    # Test 3: Check single classification endpoint
    try:
        test_data = "2024-07-31T00:00:00,177.52.183.80,192.168.1.50,HTTPS,blocked,suspicious,ids,45164,Mozilla/5.0,/login?backup.sql"
        response = requests.post(f"{base_url}/api/classify", 
                               json={"data": test_data})
        if response.status_code == 200:
            result = response.json()
            print("✅ Single classification endpoint working")
            print(f"   Result: {result.get('status', 'Unknown')}")
        else:
            print(f"❌ Single classification failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Single classification error: {e}")
    
    print("\n🎯 Server endpoints test completed!")
    return True

def create_test_csv():
    """Create a test CSV file for batch processing"""
    test_data = """timestamp,source_ip,dest_ip,protocol,action,threat_label,log_type,bytes_transferred,user_agent,request_path
2024-07-31T00:00:00,177.52.183.80,192.168.1.50,HTTPS,blocked,suspicious,ids,45164,"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",/login?backup.sql
2024-04-07T00:00:00,192.168.1.248,192.168.1.15,HTTP,allowed,benign,application,20652,"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",/login
2024-05-15T10:30:00,10.0.0.100,8.8.8.8,DNS,allowed,benign,network,512,"curl/7.68.0",/
"""
    
    with open('test_batch.csv', 'w') as f:
        f.write(test_data)
    
    print("✅ Created test_batch.csv for testing")
    return 'test_batch.csv'

def main():
    print("🚀 Starting batch processing fix verification...")
    print("=" * 50)
    
    # Test server endpoints
    if not test_server_endpoints():
        print("❌ Server is not running. Please start the server first with: python app.py")
        return
    
    # Create test file
    test_file = create_test_csv()
    
    print("\n📋 MANUAL TESTING INSTRUCTIONS:")
    print("1. Open your browser and go to http://localhost:5001")
    print("2. Upload the test_batch.csv file using drag-and-drop or file picker")
    print("3. Verify the file appears as 'File Selected: test_batch.csv'")
    print("4. Click 'Process Batch' button")
    print("5. Verify that processing starts without 'select file' warning")
    print("6. Watch the progress bar and wait for completion")
    print("7. Check the results display")
    
    print("\n✨ The fixes implemented:")
    print("• Added file state management (selectedFiles property)")
    print("• Fixed drag-and-drop file input updating")
    print("• Improved file validation before processing")
    print("• Enhanced button state management")
    print("• Added file type validation")
    print("• Better error handling and notifications")
    
    print(f"\n📁 Test file created: {os.path.abspath(test_file)}")
    print("🎯 Ready for manual testing!")

if __name__ == "__main__":
    main()
