#!/usr/bin/env python3
"""
Test script for batch processing functionality.
Creates sample files and tests the batch processing API.
"""

import requests
import json
import time
import os

def create_sample_files():
    """Create sample CSV and JSON files for testing."""
    
    # Sample CSV data
    csv_data = """timestamp,source_ip,dest_ip,protocol,action,threat_label,log_type,bytes_transferred,user_agent,request_path
2024-07-31T00:00:00,177.52.183.80,192.168.1.50,HTTPS,blocked,suspicious,ids,45164,"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",/login?backup.sql
2024-07-31T00:01:00,192.168.1.100,192.168.1.1,HTTP,allowed,normal,firewall,1024,"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",/api/users
2024-07-31T00:02:00,10.0.0.50,192.168.1.200,HTTPS,blocked,malicious,ids,2048,"Nmap Scripting Engine",/admin/config"""
    
    # Sample JSON data
    json_data = [
        {
            "timestamp": "2024-07-31T00:03:00",
            "source_ip": "203.0.113.1",
            "dest_ip": "192.168.1.50",
            "protocol": "HTTPS",
            "action": "blocked",
            "threat_label": "suspicious",
            "log_type": "ids",
            "bytes_transferred": 8192,
            "user_agent": "curl/7.68.0",
            "request_path": "/backup/database.sql"
        },
        {
            "timestamp": "2024-07-31T00:04:00",
            "source_ip": "192.168.1.150",
            "dest_ip": "192.168.1.1",
            "protocol": "HTTP",
            "action": "allowed",
            "threat_label": "normal",
            "log_type": "firewall",
            "bytes_transferred": 512,
            "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "request_path": "/api/status"
        }
    ]
    
    # Create test files
    with open('test_events.csv', 'w') as f:
        f.write(csv_data)
    
    with open('test_events.jsonl', 'w') as f:
        for item in json_data:
            f.write(json.dumps(item) + '\n')
    
    print("✅ Created sample files:")
    print("   - test_events.csv (3 activities)")
    print("   - test_events.jsonl (2 activities)")

def test_batch_processing():
    """Test the batch processing API."""
    base_url = "http://localhost:5001"
    
    print("\n🧪 Testing batch processing API...")
    
    # Check if server is running
    try:
        response = requests.get(f"{base_url}/api/sample-data", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding properly")
            return False
    except requests.exceptions.RequestException:
        print("❌ Server not running. Please start with: make run-frontend")
        return False
    
    print("✅ Server is running")
    
    # Test batch processing
    files = {
        'files': [
            ('files', open('test_events.csv', 'rb')),
            ('files', open('test_events.jsonl', 'rb'))
        ]
    }
    data = {'has_header': 'true'}
    
    try:
        print("\n📤 Starting batch processing...")
        response = requests.post(f"{base_url}/api/classify/batch", files=files, data=data)
        
        if response.status_code != 200:
            print(f"❌ Batch start failed: {response.status_code}")
            print(response.text)
            return False
        
        result = response.json()
        if not result['success']:
            print(f"❌ Batch start failed: {result['error']}")
            return False
        
        task_id = result['task_id']
        print(f"✅ Batch processing started with task ID: {task_id}")
        print(f"   Processing {result['total_files']} files")
        
        # Monitor progress
        print("\n📊 Monitoring progress...")
        while True:
            time.sleep(1)
            status_response = requests.get(f"{base_url}/api/batch/status/{task_id}")
            
            if status_response.status_code != 200:
                print(f"❌ Status check failed: {status_response.status_code}")
                return False
            
            status_result = status_response.json()
            if not status_result['success']:
                print(f"❌ Status check failed: {status_result['error']}")
                return False
            
            task = status_result['task']
            print(f"   Progress: {task['progress']}% ({task['processed_files']}/{task['total_files']} files)")
            
            if task['current_file']:
                print(f"   Current file: {task['current_file']}")
            
            if task['status'] == 'completed':
                print("✅ Processing completed!")
                break
            elif task['status'] == 'error':
                print(f"❌ Processing failed: {task.get('error', 'Unknown error')}")
                return False
        
        # Get results
        print("\n📋 Getting results...")
        results_response = requests.get(f"{base_url}/api/batch/results/{task_id}")
        
        if results_response.status_code != 200:
            print(f"❌ Results retrieval failed: {results_response.status_code}")
            return False
        
        results = results_response.json()
        if not results['success']:
            print(f"❌ Results retrieval failed: {results['error']}")
            return False
        
        print("✅ Results retrieved successfully!")
        print(f"   Total activities: {results['total_count']}")
        print(f"   Malicious: {results['malicious_count']}")
        print(f"   Non-malicious: {results['total_count'] - results['malicious_count'] - results['error_count']}")
        print(f"   Errors: {results['error_count']}")
        print(f"   Files processed: {results['files_processed']}")
        
        # Show sample results
        print("\n📄 Sample results:")
        for i, item in enumerate(results['results'][:3]):  # Show first 3 results
            if item['success']:
                print(f"   {i+1}. {item['filename']} - {item['status']} - {item.get('attack_type', 'N/A')}")
            else:
                print(f"   {i+1}. {item['filename']} - ERROR - {item['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False
    finally:
        # Close files
        for file_tuple in files['files']:
            file_tuple[1].close()

def cleanup():
    """Clean up test files."""
    for filename in ['test_events.csv', 'test_events.jsonl']:
        if os.path.exists(filename):
            os.remove(filename)
            print(f"🗑️  Removed {filename}")

def main():
    """Main test function."""
    print("🚀 Batch Processing Test Suite")
    print("=" * 40)
    
    try:
        create_sample_files()
        success = test_batch_processing()
        
        if success:
            print("\n🎉 All tests passed! Batch processing is working correctly.")
        else:
            print("\n❌ Tests failed. Please check the server and try again.")
            
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    finally:
        cleanup()

if __name__ == "__main__":
    main()


