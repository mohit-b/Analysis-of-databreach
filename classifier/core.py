#!/usr/bin/env python3
"""
Core classification logic shared between CLI and batch processing.
Handles parsing, validation, and classification of activity records.
"""

import csv
import json
import io
import re
from typing import Dict, Any, Tuple, Optional

class ActivityClassifier:
    """Core activity classifier with robust parsing and validation."""
    
    def __init__(self):
        # Required fields for validation
        self.required_fields = [
            'timestamp', 'source_ip', 'action', 'threat_label', 
            'user_agent', 'request_path'
        ]
        
        # Valid field values
        self.valid_actions = {'allowed', 'blocked', 'failed'}
        self.valid_threat_labels = {'benign', 'suspicious'}
        
        # Attack patterns based on observed data and policy rules
        self.attack_patterns = {
            'backup_access': [
                r'backup\.sql', r'/backup', r'download\?backup', 
                r'\?backup\.sql', r'backup\.zip', r'backup\.db'
            ],
            'path_traversal': [
                r'\.\.\\\.\.\\etc\\passwd', r'/etc/passwd', 
                r'\?\.\.\\\.\.\\etc\\passwd', r'\.\./\.\./etc/passwd'
            ],
            'admin_privilege': [
                r'/admin', r'\?admin', r'/admin/config', 
                r'/dashboard\?admin', r'/wp-admin'
            ],
            'login_brute_force': [
                r'/login', r'/api/login', r'/wp-login\.php', 
                r'\?login', r'/auth'
            ],
            'malware_upload': [
                r'/upload\?phpmyadmin', r'/upload', r'phpmyadmin',
                r'\.php', r'\.exe', r'\.bat'
            ],
            'sql_injection': [
                r'SQLMap/1\.6-dev', r'union.*select', r'drop.*table'
            ],
            'network_scanning': [
                r'Nmap Scripting Engine', r'nikto', r'nessus'
            ]
        }
        
        # Suspicious user agents
        self.suspicious_user_agents = [
            'Nmap Scripting Engine', 'SQLMap/1.6-dev', 'curl/7.64.1',
            'nikto', 'nessus', 'masscan', 'zmap'
        ]

    def parse_input(self, input_string: str) -> Tuple[bool, Dict[str, str], str]:
        """
        Parse input as JSON first, then CSV fallback.
        
        Args:
            input_string: Raw input string
            
        Returns:
            Tuple of (success, parsed_record, error_message)
        """
        # Try JSON parsing first (more specific)
        json_success, json_record, json_error = self._parse_json(input_string)
        if json_success:
            return True, json_record, ""
        
        # Try CSV parsing as fallback
        csv_success, csv_record, csv_error = self._parse_csv(input_string)
        if csv_success:
            return True, csv_record, ""
        
        # Both failed
        return False, {}, "Could not parse activity input—ensure input is a valid single CSV row or JSON object."

    def _parse_csv(self, csv_line: str) -> Tuple[bool, Dict[str, str], str]:
        """Parse CSV input safely."""
        try:
            # Clean input
            csv_line = csv_line.strip()
            if not csv_line:
                return False, {}, "Empty input"
            
            # Create CSV reader with flexible field handling
            csv_reader = csv.DictReader(
                io.StringIO(csv_line),
                fieldnames=[
                    'timestamp', 'source_ip', 'dest_ip', 'protocol', 
                    'action', 'threat_label', 'log_type', 'bytes_transferred', 
                    'user_agent', 'request_path'
                ],
                quoting=csv.QUOTE_ALL
            )
            
            # Read the single row
            record = next(csv_reader)
            
            # Clean up values and handle missing fields
            record = {
                key: (value.strip() if value else "") 
                for key, value in record.items()
            }
            
            return True, record, ""
            
        except (csv.Error, StopIteration, ValueError) as e:
            return False, {}, f"CSV parsing failed: {str(e)}"
        except Exception as e:
            return False, {}, f"Unexpected CSV error: {str(e)}"

    def _parse_json(self, json_line: str) -> Tuple[bool, Dict[str, str], str]:
        """Parse JSON input as fallback."""
        try:
            json_line = json_line.strip()
            if not json_line:
                return False, {}, "Empty JSON input"
            
            # Parse JSON
            data = json.loads(json_line)
            
            # Convert to string values and handle missing fields
            record = {
                'timestamp': str(data.get('timestamp', '')),
                'source_ip': str(data.get('source_ip', '')),
                'dest_ip': str(data.get('dest_ip', '')),
                'protocol': str(data.get('protocol', '')),
                'action': str(data.get('action', '')),
                'threat_label': str(data.get('threat_label', data.get('label', ''))),
                'log_type': str(data.get('log_type', '')),
                'bytes_transferred': str(data.get('bytes_transferred', '')),
                'user_agent': str(data.get('user_agent', '')),
                'request_path': str(data.get('request_path', data.get('file_name', '')))
            }
            
            return True, record, ""
            
        except (json.JSONDecodeError, ValueError) as e:
            return False, {}, f"JSON parsing failed: {str(e)}"
        except Exception as e:
            return False, {}, f"Unexpected JSON error: {str(e)}"

    def validate_record(self, record: Dict[str, str]) -> Tuple[bool, str]:
        """
        Validate that record has all required fields with valid values.
        
        Args:
            record: Parsed record dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required fields
        missing_fields = []
        for field in self.required_fields:
            if field not in record or not record[field]:
                missing_fields.append(field)
        
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        # Validate field values
        action = record['action'].lower()
        if action not in self.valid_actions:
            return False, f"Invalid action: {record['action']}"
        
        threat_label = record['threat_label'].lower()
        if threat_label not in self.valid_threat_labels:
            return False, f"Invalid threat_label: {record['threat_label']}"
        
        return True, ""

    def classify_activity(self, record: Dict[str, str]) -> Tuple[str, str, str]:
        """
        Classify activity as malicious or non-malicious.
        
        Args:
            record: Validated record dictionary
            
        Returns:
            Tuple of (status, attack_type, reason)
        """
        # Extract key fields
        action = record.get('action', '').lower()
        threat_label = record.get('threat_label', '').lower()
        user_agent = record.get('user_agent', '')
        request_path = record.get('request_path', '')
        
        # Rule 1: Explicit suspicious label
        if threat_label == 'suspicious':
            attack_type = self._determine_attack_type(request_path, user_agent, action)
            reason = f"Event labeled as 'suspicious' with indicators: {attack_type.lower()}"
            return "Malicious", attack_type, reason
        
        # Rule 2: Blocked/failed actions with suspicious indicators
        if action in ['blocked', 'failed']:
            if self._has_suspicious_indicators(request_path, user_agent):
                attack_type = self._determine_attack_type(request_path, user_agent, action)
                reason = f"Event was {action} and contains suspicious indicators: {attack_type.lower()}"
                return "Malicious", attack_type, reason
        
        # Rule 3: Allowed actions with high-risk patterns
        if action == 'allowed':
            if self._is_high_risk_pattern(request_path, user_agent):
                attack_type = self._determine_attack_type(request_path, user_agent, action)
                reason = f"Allowed event contains high-risk patterns: {attack_type.lower()}"
                return "Malicious", attack_type, reason
        
        # Rule 4: Suspicious user agents with sensitive paths
        if user_agent in self.suspicious_user_agents:
            if self._has_sensitive_path(request_path):
                attack_type = self._determine_attack_type(request_path, user_agent, action)
                reason = f"Suspicious user agent '{user_agent}' accessing sensitive path: {attack_type.lower()}"
                return "Malicious", attack_type, reason
        
        # Rule 5: Blocked actions with suspicious user agents (network scanning)
        if action == 'blocked' and user_agent in self.suspicious_user_agents:
            attack_type = self._determine_attack_type(request_path, user_agent, action)
            reason = f"Event was {action} with suspicious user agent '{user_agent}': {attack_type.lower()}"
            return "Malicious", attack_type, reason
        
        # Default: Non-malicious
        return "Non-malicious", "None", "No indicators of threat in log fields—event is routine or allowed."

    def _has_suspicious_indicators(self, request_path: str, user_agent: str) -> bool:
        """Check if request has suspicious indicators."""
        # Check for backup file access
        if any(pattern in request_path.lower() for pattern in ['backup.sql', '/backup', 'backup']):
            return True
        
        # Check for path traversal attempts
        if any(pattern in request_path for pattern in ['../etc/passwd', '..\\..\\etc\\passwd', '/etc/passwd']):
            return True
        
        # Check for admin access attempts
        if any(pattern in request_path.lower() for pattern in ['/admin', '?admin', '/wp-admin']):
            return True
        
        # Check for malicious upload attempts
        if any(pattern in request_path.lower() for pattern in ['phpmyadmin', '/upload', '.php', '.exe']):
            return True
        
        return False

    def _is_high_risk_pattern(self, request_path: str, user_agent: str) -> bool:
        """Check if this is a high-risk pattern even if allowed."""
        # Any protocol with backup files
        if 'backup' in request_path.lower():
            return True
        
        # Any protocol with path traversal
        if any(pattern in request_path for pattern in ['../etc/passwd', '..\\..\\etc\\passwd']):
            return True
        
        # Any protocol with admin access
        if '/admin' in request_path.lower():
            return True
        
        return False

    def _has_sensitive_path(self, request_path: str) -> bool:
        """Check if path is sensitive."""
        sensitive_patterns = [
            '/admin', '/backup', '/etc/passwd', 'backup.sql', 
            'phpmyadmin', '/upload', '/download', '/config'
        ]
        return any(pattern in request_path.lower() for pattern in sensitive_patterns)

    def _determine_attack_type(self, request_path: str, user_agent: str, action: str) -> str:
        """Determine the specific attack type based on indicators."""
        # Check for backup access
        if any(re.search(pattern, request_path, re.IGNORECASE) for pattern in self.attack_patterns['backup_access']):
            return "Unauthorized backup access"
        
        # Check for path traversal
        if any(re.search(pattern, request_path) for pattern in self.attack_patterns['path_traversal']):
            return "Path traversal attempt"
        
        # Check for admin privilege escalation
        if any(re.search(pattern, request_path, re.IGNORECASE) for pattern in self.attack_patterns['admin_privilege']):
            return "Privilege escalation attempt"
        
        # Check for login brute force
        if any(re.search(pattern, request_path, re.IGNORECASE) for pattern in self.attack_patterns['login_brute_force']):
            return "Suspicious login attempt"
        
        # Check for malware upload
        if any(re.search(pattern, request_path, re.IGNORECASE) for pattern in self.attack_patterns['malware_upload']):
            return "Malware upload attempt"
        
        # Check for SQL injection tools
        if user_agent in ['SQLMap/1.6-dev']:
            return "SQL injection attempt"
        
        # Check for network scanning
        if user_agent in ['Nmap Scripting Engine']:
            return "Network reconnaissance"
        
        # Default suspicious activity
        return "Suspicious activity"

    def process_activity(self, input_string: str) -> Tuple[bool, str]:
        """
        Complete processing pipeline for a single activity.
        
        Args:
            input_string: Raw input string (CSV or JSON)
            
        Returns:
            Tuple of (success, result_message)
        """
        try:
            # Parse input
            parse_success, record, parse_error = self.parse_input(input_string)
            if not parse_success:
                return False, f"Error: {parse_error}"
            
            # Validate record
            is_valid, validation_error = self.validate_record(record)
            if not is_valid:
                return False, "Error: Missing or invalid required fields in activity input—check column names and value formats."
            
            # Classify activity
            status, attack_type, reason = self.classify_activity(record)
            
            # Format output
            result = f"Activity status: {status}\nType of attack: {attack_type}\nReason: {reason}"
            return True, result
            
        except Exception as e:
            return False, f"Error: Processing failed: {str(e)}"
