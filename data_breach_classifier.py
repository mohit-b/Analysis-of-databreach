#!/usr/bin/env python3
"""
Data-Breach Activity Classifier
Automated forensic assistant for data-breach analysis chatbot.
Determines whether an activity record is malicious or non-malicious.
"""

import csv
import sys
import re
from typing import Dict, Any, Tuple

class DataBreachClassifier:
    def __init__(self):
        # Define attack type patterns based on observed data
        self.attack_patterns = {
            'backup_access': [
                r'backup\.sql', r'/backup', r'download\?backup', r'\?backup\.sql'
            ],
            'path_traversal': [
                r'\.\.\\\.\.\\etc\\passwd', r'/etc/passwd', r'\?\.\.\\\.\.\\etc\\passwd'
            ],
            'admin_privilege': [
                r'/admin', r'\?admin', r'/admin/config', r'/dashboard\?admin'
            ],
            'login_brute_force': [
                r'/login', r'/api/login', r'/wp-login\.php', r'\?login'
            ],
            'malware_upload': [
                r'/upload\?phpmyadmin', r'/upload', r'phpmyadmin'
            ],
            'sql_injection': [
                r'SQLMap/1\.6-dev'
            ],
            'network_scanning': [
                r'Nmap Scripting Engine'
            ]
        }
        
        # Suspicious user agents
        self.suspicious_user_agents = [
            'Nmap Scripting Engine',
            'SQLMap/1.6-dev',
            'curl/7.64.1'
        ]

    def classify_activity(self, record: Dict[str, str]) -> Tuple[str, str, str]:
        """
        Classify a single activity record.
        
        Args:
            record: Dictionary containing the CSV row data
            
        Returns:
            Tuple of (status, attack_type, reason)
        """
        # Extract key fields
        action = record.get('action', '').lower()
        threat_label = record.get('threat_label', '').lower()
        user_agent = record.get('user_agent', '')
        request_path = record.get('request_path', '')
        protocol = record.get('protocol', '').upper()
        
        # Rule 1: Explicit suspicious label
        if threat_label == 'suspicious':
            attack_type = self._determine_attack_type(request_path, user_agent, action)
            reason = f"Event labeled as 'suspicious' with indicators: {attack_type.lower()}"
            return "Malicious", attack_type, reason
        
        # Rule 2: Blocked actions with suspicious indicators
        if action == 'blocked':
            if self._has_suspicious_indicators(request_path, user_agent) or user_agent in self.suspicious_user_agents:
                attack_type = self._determine_attack_type(request_path, user_agent, action)
                reason = f"Event was blocked and contains suspicious indicators: {attack_type.lower()}"
                return "Malicious", attack_type, reason
        
        # Rule 3: Allowed actions with high-risk patterns
        if action == 'allowed':
            if self._is_high_risk_pattern(request_path, user_agent, protocol):
                attack_type = self._determine_attack_type(request_path, user_agent, action)
                reason = f"Allowed event contains high-risk patterns: {attack_type.lower()}"
                return "Malicious", attack_type, reason
        
        # Rule 4: Suspicious user agents with sensitive paths
        if user_agent in self.suspicious_user_agents:
            if self._has_sensitive_path(request_path):
                attack_type = self._determine_attack_type(request_path, user_agent, action)
                reason = f"Suspicious user agent '{user_agent}' accessing sensitive path: {attack_type.lower()}"
                return "Malicious", attack_type, reason
        
        # Default: Non-malicious
        return "Non-malicious", "None", "No indicators of threat in log fields—event is routine or allowed."

    def _has_suspicious_indicators(self, request_path: str, user_agent: str) -> bool:
        """Check if request has suspicious indicators."""
        # Check for backup file access
        if any(pattern in request_path for pattern in ['backup.sql', '/backup', 'backup']):
            return True
        
        # Check for path traversal attempts
        if '..\\..\\etc\\passwd' in request_path or '/etc/passwd' in request_path:
            return True
        
        # Check for admin access attempts
        if '/admin' in request_path or '?admin' in request_path:
            return True
        
        # Check for malicious upload attempts
        if 'phpmyadmin' in request_path or '/upload' in request_path:
            return True
        
        return False

    def _is_high_risk_pattern(self, request_path: str, user_agent: str, protocol: str) -> bool:
        """Check if this is a high-risk pattern even if allowed."""
        # FTP with backup files
        if protocol == 'FTP' and 'backup' in request_path:
            return True
        
        # SSH with system files
        if protocol == 'SSH' and ('/etc/passwd' in request_path or 'backup.sql' in request_path):
            return True
        
        # Any protocol with path traversal
        if '..\\..\\etc\\passwd' in request_path:
            return True
        
        return False

    def _has_sensitive_path(self, request_path: str) -> bool:
        """Check if path is sensitive."""
        sensitive_patterns = [
            '/admin', '/backup', '/etc/passwd', 'backup.sql', 
            'phpmyadmin', '/upload', '/download'
        ]
        return any(pattern in request_path for pattern in sensitive_patterns)

    def _determine_attack_type(self, request_path: str, user_agent: str, action: str) -> str:
        """Determine the specific attack type based on indicators."""
        # Check for backup access
        if any(re.search(pattern, request_path) for pattern in self.attack_patterns['backup_access']):
            return "Unauthorized backup access"
        
        # Check for path traversal
        if any(re.search(pattern, request_path) for pattern in self.attack_patterns['path_traversal']):
            return "Path traversal attempt"
        
        # Check for admin privilege escalation
        if any(re.search(pattern, request_path) for pattern in self.attack_patterns['admin_privilege']):
            return "Privilege escalation attempt"
        
        # Check for login brute force
        if any(re.search(pattern, request_path) for pattern in self.attack_patterns['login_brute_force']):
            return "Suspicious login attempt"
        
        # Check for malware upload
        if any(re.search(pattern, request_path) for pattern in self.attack_patterns['malware_upload']):
            return "Malware upload attempt"
        
        # Check for SQL injection tools
        if user_agent in ['SQLMap/1.6-dev']:
            return "SQL injection attempt"
        
        # Check for network scanning
        if user_agent in ['Nmap Scripting Engine']:
            return "Network reconnaissance"
        
        # Default suspicious activity
        return "Suspicious activity"

def process_csv_row(csv_line: str) -> str:
    """Process a single CSV row and return the 3-line classification."""
    # Add header to the CSV line for parsing
    header = "timestamp,source_ip,dest_ip,protocol,action,threat_label,log_type,bytes_transferred,user_agent,request_path"
    csv_data = header + "\n" + csv_line
    
    # Parse CSV line
    reader = csv.DictReader(csv_data.split('\n'))
    record = next(reader)
    
    # Classify the activity
    classifier = DataBreachClassifier()
    status, attack_type, reason = classifier.classify_activity(record)
    
    # Return in exact required format
    return f"Activity status: {status}\nType of attack: {attack_type}\nReason: {reason}"

def main():
    """Main function for command-line usage."""
    if len(sys.argv) != 2:
        print("Usage: python data_breach_classifier.py <csv_line>")
        print("Example: python data_breach_classifier.py '2024-07-31T00:00:00,177.52.183.80,192.168.1.50,HTTPS,blocked,suspicious,ids,45164,\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36\",/login?backup.sql'")
        sys.exit(1)
    
    csv_line = sys.argv[1]
    result = process_csv_row(csv_line)
    print(result)

if __name__ == "__main__":
    main()
