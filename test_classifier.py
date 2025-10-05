#!/usr/bin/env python3
"""
Test script for the data-breach activity classifier.
Demonstrates various attack types and classifications.
"""

from data_breach_classifier import process_csv_row

def test_classifier():
    """Test the classifier with various examples."""
    
    test_cases = [
        {
            "name": "Suspicious backup access (blocked)",
            "csv": "2024-07-31T00:00:00,177.52.183.80,192.168.1.50,HTTPS,blocked,suspicious,ids,45164,\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36\",/login?backup.sql"
        },
        {
            "name": "Routine login (benign)",
            "csv": "2024-04-07T00:00:00,192.168.1.248,192.168.1.15,HTTP,allowed,benign,application,20652,\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36\",/login"
        },
        {
            "name": "FTP backup download (suspicious)",
            "csv": "2024-06-02T00:00:00,104.187.87.205,192.168.1.182,FTP,allowed,suspicious,ids,13271,\"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36\",/download?backup.sql"
        },
        {
            "name": "Path traversal attempt",
            "csv": "2024-12-05T00:00:00,141.26.13.167,192.168.1.141,TCP,allowed,suspicious,ids,26588,SQLMap/1.6-dev,/?..\\..\\etc\\passwd"
        },
        {
            "name": "Admin privilege escalation",
            "csv": "2024-06-01T00:00:00,185.225.185.68,192.168.1.79,HTTP,allowed,suspicious,application,13717,\"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36\",/dashboard?admin"
        },
        {
            "name": "Malware upload attempt",
            "csv": "2024-03-06T00:00:00,137.197.33.33,192.168.1.7,FTP,allowed,suspicious,firewall,30357,\"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36\",/upload?phpmyadmin"
        },
        {
            "name": "Blocked network scan",
            "csv": "2024-05-01T00:00:00,192.168.1.125,192.168.1.124,TCP,blocked,benign,firewall,10889,Nmap Scripting Engine,/"
        },
        {
            "name": "SSH with system files",
            "csv": "2024-02-28T00:00:00,95.91.54.172,192.168.1.152,SSH,allowed,suspicious,application,47758,Nmap Scripting Engine,/etc/passwd?backup.sql"
        }
    ]
    
    print("=" * 80)
    print("DATA-BREACH ACTIVITY CLASSIFIER TEST RESULTS")
    print("=" * 80)
    print()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['name']}")
        print("-" * 60)
        result = process_csv_row(test_case['csv'])
        print(result)
        print()

if __name__ == "__main__":
    test_classifier()
