#!/usr/bin/env python3
"""
Comprehensive test suite for the robust classify_activity.py script.
Tests all error conditions and edge cases.
"""

import subprocess
import sys
import os

def run_classifier_test(input_string, expected_exit_code=0, description=""):
    """
    Run the classifier with given input and check exit code.
    
    Args:
        input_string: Input to pass to the classifier
        expected_exit_code: Expected exit code (0 for success, 1 for error)
        description: Description of the test case
    """
    print(f"\n{'='*60}")
    print(f"TEST: {description}")
    print(f"{'='*60}")
    print(f"Input: {input_string}")
    print(f"Expected exit code: {expected_exit_code}")
    print("-" * 60)
    
    try:
        # Run the classifier
        result = subprocess.run(
            [sys.executable, "classify_activity.py", input_string],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        print(f"Actual exit code: {result.returncode}")
        print(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            print(f"STDERR:\n{result.stderr}")
        
        # Check if exit code matches expectation
        if result.returncode == expected_exit_code:
            print("✅ TEST PASSED")
        else:
            print("❌ TEST FAILED - Exit code mismatch")
            
    except subprocess.TimeoutExpired:
        print("❌ TEST FAILED - Timeout")
    except Exception as e:
        print(f"❌ TEST FAILED - Exception: {e}")

def main():
    """Run comprehensive test suite."""
    print("ROBUST CLASSIFIER TEST SUITE")
    print("=" * 80)
    
    # Test 1: No arguments
    run_classifier_test(
        "", 
        expected_exit_code=1,
        description="No input provided"
    )
    
    # Test 2: Valid malicious input
    run_classifier_test(
        '2024-07-31T00:00:00,177.52.183.80,192.168.1.50,HTTPS,blocked,suspicious,ids,45164,"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",/login?backup.sql',
        expected_exit_code=0,
        description="Valid malicious input (suspicious backup access)"
    )
    
    # Test 3: Valid benign input
    run_classifier_test(
        '2024-04-07T00:00:00,192.168.1.248,192.168.1.15,HTTP,allowed,benign,application,20652,"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",/login',
        expected_exit_code=0,
        description="Valid benign input (routine login)"
    )
    
    # Test 4: Invalid CSV format (too few fields)
    run_classifier_test(
        '2024-07-31T00:00:00,177.52.183.80,192.168.1.50,HTTPS,blocked,suspicious',
        expected_exit_code=1,
        description="Invalid CSV format (too few fields)"
    )
    
    # Test 5: Invalid action value
    run_classifier_test(
        '2024-07-31T00:00:00,177.52.183.80,192.168.1.50,HTTPS,invalid_action,suspicious,ids,45164,"Mozilla/5.0",/login',
        expected_exit_code=1,
        description="Invalid action value"
    )
    
    # Test 6: Invalid threat_label value
    run_classifier_test(
        '2024-07-31T00:00:00,177.52.183.80,192.168.1.50,HTTPS,blocked,invalid_label,ids,45164,"Mozilla/5.0",/login',
        expected_exit_code=1,
        description="Invalid threat_label value"
    )
    
    # Test 7: Invalid protocol value
    run_classifier_test(
        '2024-07-31T00:00:00,177.52.183.80,192.168.1.50,INVALID_PROTOCOL,blocked,suspicious,ids,45164,"Mozilla/5.0",/login',
        expected_exit_code=1,
        description="Invalid protocol value"
    )
    
    # Test 8: Invalid bytes_transferred (non-numeric)
    run_classifier_test(
        '2024-07-31T00:00:00,177.52.183.80,192.168.1.50,HTTPS,blocked,suspicious,ids,invalid_bytes,"Mozilla/5.0",/login',
        expected_exit_code=1,
        description="Invalid bytes_transferred (non-numeric)"
    )
    
    # Test 9: CSV with extra commas and quotes
    run_classifier_test(
        '"2024-07-31T00:00:00","177.52.183.80","192.168.1.50","HTTPS","blocked","suspicious","ids","45164","Mozilla/5.0","/login"',
        expected_exit_code=0,
        description="CSV with extra quotes (should handle gracefully)"
    )
    
    # Test 10: Empty string input
    run_classifier_test(
        "",
        expected_exit_code=1,
        description="Empty string input"
    )
    
    # Test 11: Whitespace-only input
    run_classifier_test(
        "   ",
        expected_exit_code=1,
        description="Whitespace-only input"
    )
    
    # Test 12: CSV with special characters in user_agent
    run_classifier_test(
        '2024-07-31T00:00:00,177.52.183.80,192.168.1.50,HTTPS,blocked,suspicious,ids,45164,"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",/login',
        expected_exit_code=0,
        description="CSV with special characters in user_agent"
    )
    
    # Test 13: Path traversal attack
    run_classifier_test(
        '2024-12-05T00:00:00,141.26.13.167,192.168.1.141,TCP,allowed,suspicious,ids,26588,SQLMap/1.6-dev,/?..\\..\\etc\\passwd',
        expected_exit_code=0,
        description="Path traversal attack detection"
    )
    
    print("\n" + "="*80)
    print("TEST SUITE COMPLETED")
    print("="*80)

if __name__ == "__main__":
    main()






