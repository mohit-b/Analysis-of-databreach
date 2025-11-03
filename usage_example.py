#!/usr/bin/env python3
"""
Usage example for the robust classify_activity.py script.
Demonstrates the exact CLI format and expected outputs.
"""

import subprocess
import sys

def run_example(description, csv_input):
    """Run a single example and display results."""
    print(f"\n{description}")
    print("-" * 50)
    print(f"Command: python classify_activity.py \"{csv_input}\"")
    print("\nOutput:")
    
    try:
        result = subprocess.run(
            [sys.executable, "classify_activity.py", csv_input],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        print(f"Exit code: {result.returncode}")
        
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Demonstrate various usage examples."""
    print("=" * 70)
    print("CLASSIFY_ACTIVITY.PY USAGE EXAMPLES")
    print("=" * 70)
    
    # Example 1: Valid malicious input
    run_example(
        "Example 1: Valid malicious input (suspicious backup access)",
        '2024-07-31T00:00:00,177.52.183.80,192.168.1.50,HTTPS,blocked,suspicious,ids,45164,"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",/login?backup.sql'
    )
    
    # Example 2: Valid benign input
    run_example(
        "Example 2: Valid benign input (routine login)",
        '2024-04-07T00:00:00,192.168.1.248,192.168.1.15,HTTP,allowed,benign,application,20652,"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",/login'
    )
    
    # Example 3: Path traversal attack
    run_example(
        "Example 3: Path traversal attack",
        '2024-12-05T00:00:00,141.26.13.167,192.168.1.141,TCP,allowed,suspicious,ids,26588,SQLMap/1.6-dev,/?..\\..\\etc\\passwd'
    )
    
    # Example 4: No input (error case)
    run_example(
        "Example 4: No input provided (error case)",
        ""
    )
    
    # Example 5: Invalid action (error case)
    run_example(
        "Example 5: Invalid action value (error case)",
        '2024-07-31T00:00:00,177.52.183.80,192.168.1.50,HTTPS,invalid_action,suspicious,ids,45164,Mozilla/5.0,/login'
    )
    
    print("\n" + "=" * 70)
    print("USAGE SUMMARY")
    print("=" * 70)
    print("""
The classify_activity.py script accepts exactly one argument: a CSV row string.

✅ SUCCESS CASES (exit code 0):
- Valid CSV with all required fields produces 3-line classification output
- Format: Activity status, Type of attack, Reason

❌ ERROR CASES (exit code 1):
- No input provided
- Invalid CSV format
- Missing required fields
- Invalid field values (action, threat_label, protocol, bytes_transferred)

REQUIRED CSV FORMAT:
timestamp,source_ip,dest_ip,protocol,action,threat_label,log_type,bytes_transferred,user_agent,request_path

VALID VALUES:
- action: allowed, blocked
- threat_label: benign, suspicious  
- protocol: HTTP, HTTPS, FTP, SSH, TCP, UDP, ICMP
- bytes_transferred: numeric value
    """)

if __name__ == "__main__":
    main()






