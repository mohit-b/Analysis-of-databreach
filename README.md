# Data-Breach Activity Classifier

An automated forensic assistant for data-breach analysis that determines whether activity records are malicious or non-malicious.

## Features

- **Deterministic Classification**: Analyzes single CSV rows to classify activities as Malicious or Non-malicious
- **Multiple Attack Type Detection**: Identifies various attack patterns including:
  - Unauthorized backup access
  - Path traversal attempts
  - Privilege escalation attempts
  - Suspicious login attempts
  - Malware upload attempts
  - SQL injection attempts
  - Network reconnaissance
- **Exact Output Format**: Produces standardized 3-line incident summaries
- **Rule-Based Detection**: Uses comprehensive rules based on threat labels, blocked actions, suspicious user agents, and path patterns

## Files

- `data_breach_classifier.py` - Main classifier implementation
- `classify_activity.py` - Simple wrapper for chatbot integration
- `test_classifier.py` - Test script with various examples
- `cybersecurity_dataset(1).csv` - Sample dataset with 10,000+ records

## Usage

### Command Line Interface

```bash
# Classify a single CSV row
python classify_activity.py "timestamp,source_ip,dest_ip,protocol,action,threat_label,log_type,bytes_transferred,user_agent,request_path"

# Example with suspicious backup access
python classify_activity.py "2024-07-31T00:00:00,177.52.183.80,192.168.1.50,HTTPS,blocked,suspicious,ids,45164,\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36\",/login?backup.sql"
```

### Programmatic Usage

```python
from data_breach_classifier import process_csv_row

# Process a CSV row and get classification
csv_line = "2024-07-31T00:00:00,177.52.183.80,192.168.1.50,HTTPS,blocked,suspicious,ids,45164,\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36\",/login?backup.sql"
result = process_csv_row(csv_line)
print(result)
```

### Test Examples

Run the test script to see various attack types in action:

```bash
python test_classifier.py
```

## Output Format

The classifier produces exactly 3 lines of output:

```
Activity status: Malicious
Type of attack: Unauthorized backup access
Reason: Event labeled as 'suspicious' with indicators: unauthorized backup access
```

## Classification Rules

The classifier uses the following priority-based rules:

1. **Explicit Suspicious Label**: Events labeled as "suspicious" are classified as malicious
2. **Blocked Actions**: Blocked events with suspicious indicators (backup files, path traversal, admin access, etc.)
3. **High-Risk Patterns**: Allowed events that exhibit high-risk patterns (FTP backup access, SSH with system files, etc.)
4. **Suspicious User Agents**: Events using tools like Nmap, SQLMap, or curl accessing sensitive paths
5. **Default**: Events without suspicious indicators are classified as non-malicious

## Attack Type Detection

The classifier detects the following attack types:

- **Unauthorized backup access**: Backup file access patterns
- **Path traversal attempt**: Directory traversal patterns (../etc/passwd)
- **Privilege escalation attempt**: Admin access patterns
- **Suspicious login attempt**: Login-related suspicious activity
- **Malware upload attempt**: Upload patterns with suspicious files
- **SQL injection attempt**: SQLMap tool usage
- **Network reconnaissance**: Nmap tool usage
- **None**: For non-malicious activities

## CSV Format

Expected CSV format:
```
timestamp,source_ip,dest_ip,protocol,action,threat_label,log_type,bytes_transferred,user_agent,request_path
```

Where:
- `action`: "allowed" or "blocked"
- `threat_label`: "benign" or "suspicious"
- `protocol`: HTTP, HTTPS, FTP, SSH, TCP, UDP, ICMP
- `user_agent`: Browser or tool identification
- `request_path`: URL path or file access pattern

## Requirements

- Python 3.6+
- No external dependencies (uses only standard library)

## Integration

This classifier is designed to be integrated into a chatbot system where it can process individual activity records and provide immediate threat assessment in the standardized 3-line format.



![alt text][CyberGuard-Data-Breach-Activity-Classifier-11-03-2025_02_25_AM.png]


