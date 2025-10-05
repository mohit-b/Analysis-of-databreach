#!/usr/bin/env python3
"""
Unit tests for classification rules and attack detection.
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from classifier.core import ActivityClassifier

class TestRules(unittest.TestCase):
    """Test classification rules."""
    
    def setUp(self):
        """Set up test environment."""
        self.classifier = ActivityClassifier()
    
    def test_suspicious_label_malicious(self):
        """Test that suspicious label results in malicious classification."""
        record = {
            'timestamp': '2024-07-31T00:00:00',
            'source_ip': '177.52.183.80',
            'action': 'allowed',
            'threat_label': 'suspicious',
            'user_agent': 'Mozilla/5.0',
            'request_path': '/login'
        }
        status, attack_type, reason = self.classifier.classify_activity(record)
        
        self.assertEqual(status, "Malicious")
        self.assertNotEqual(attack_type, "None")
        self.assertIn("suspicious", reason.lower())
    
    def test_backup_access_detection(self):
        """Test backup access attack detection."""
        record = {
            'timestamp': '2024-07-31T00:00:00',
            'source_ip': '177.52.183.80',
            'action': 'blocked',
            'threat_label': 'suspicious',
            'user_agent': 'Mozilla/5.0',
            'request_path': '/login?backup.sql'
        }
        status, attack_type, reason = self.classifier.classify_activity(record)
        
        self.assertEqual(status, "Malicious")
        self.assertEqual(attack_type, "Unauthorized backup access")
        self.assertIn("backup", reason.lower())
    
    def test_path_traversal_detection(self):
        """Test path traversal attack detection."""
        record = {
            'timestamp': '2024-12-05T00:00:00',
            'source_ip': '141.26.13.167',
            'action': 'allowed',
            'threat_label': 'suspicious',
            'user_agent': 'SQLMap/1.6-dev',
            'request_path': '/?..\\..\\etc\\passwd'
        }
        status, attack_type, reason = self.classifier.classify_activity(record)
        
        self.assertEqual(status, "Malicious")
        self.assertEqual(attack_type, "Path traversal attempt")
        self.assertIn("traversal", reason.lower())
    
    def test_admin_privilege_escalation(self):
        """Test admin privilege escalation detection."""
        record = {
            'timestamp': '2024-06-01T00:00:00',
            'source_ip': '185.225.185.68',
            'action': 'allowed',
            'threat_label': 'suspicious',
            'user_agent': 'Mozilla/5.0',
            'request_path': '/dashboard?admin'
        }
        status, attack_type, reason = self.classifier.classify_activity(record)
        
        self.assertEqual(status, "Malicious")
        self.assertEqual(attack_type, "Privilege escalation attempt")
        self.assertIn("escalation", reason.lower())
    
    def test_malware_upload_detection(self):
        """Test malware upload detection."""
        record = {
            'timestamp': '2024-03-06T00:00:00',
            'source_ip': '137.197.33.33',
            'action': 'allowed',
            'threat_label': 'suspicious',
            'user_agent': 'Mozilla/5.0',
            'request_path': '/upload?phpmyadmin'
        }
        status, attack_type, reason = self.classifier.classify_activity(record)
        
        self.assertEqual(status, "Malicious")
        self.assertEqual(attack_type, "Malware upload attempt")
        self.assertIn("upload", reason.lower())
    
    def test_sql_injection_tool_detection(self):
        """Test SQL injection tool detection."""
        record = {
            'timestamp': '2024-12-05T00:00:00',
            'source_ip': '141.26.13.167',
            'action': 'allowed',
            'threat_label': 'suspicious',
            'user_agent': 'SQLMap/1.6-dev',
            'request_path': '/api/test'
        }
        status, attack_type, reason = self.classifier.classify_activity(record)
        
        self.assertEqual(status, "Malicious")
        self.assertEqual(attack_type, "SQL injection attempt")
        self.assertIn("injection", reason.lower())
    
    def test_network_scanning_detection(self):
        """Test network scanning detection."""
        record = {
            'timestamp': '2024-05-01T00:00:00',
            'source_ip': '192.168.1.125',
            'action': 'blocked',
            'threat_label': 'benign',
            'user_agent': 'Nmap Scripting Engine',
            'request_path': '/'
        }
        status, attack_type, reason = self.classifier.classify_activity(record)
        
        # Blocked action with suspicious user agent should be malicious
        self.assertEqual(status, "Malicious")
        self.assertEqual(attack_type, "Network reconnaissance")
        self.assertIn("blocked", reason.lower())
    
    def test_blocked_action_with_backup(self):
        """Test blocked action with backup file access."""
        record = {
            'timestamp': '2024-07-31T00:00:00',
            'source_ip': '177.52.183.80',
            'action': 'blocked',
            'threat_label': 'benign',
            'user_agent': 'Mozilla/5.0',
            'request_path': '/download?backup.sql'
        }
        status, attack_type, reason = self.classifier.classify_activity(record)
        
        self.assertEqual(status, "Malicious")
        self.assertEqual(attack_type, "Unauthorized backup access")
        self.assertIn("blocked", reason.lower())
    
    def test_benign_activity(self):
        """Test benign activity classification."""
        record = {
            'timestamp': '2024-04-07T00:00:00',
            'source_ip': '192.168.1.248',
            'action': 'allowed',
            'threat_label': 'benign',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'request_path': '/login'
        }
        status, attack_type, reason = self.classifier.classify_activity(record)
        
        self.assertEqual(status, "Non-malicious")
        self.assertEqual(attack_type, "None")
        self.assertIn("routine", reason.lower())
    
    def test_failed_action_with_suspicious_path(self):
        """Test failed action with suspicious path."""
        record = {
            'timestamp': '2024-07-31T00:00:00',
            'source_ip': '177.52.183.80',
            'action': 'failed',
            'threat_label': 'benign',
            'user_agent': 'Mozilla/5.0',
            'request_path': '/admin/config'
        }
        status, attack_type, reason = self.classifier.classify_activity(record)
        
        self.assertEqual(status, "Malicious")
        self.assertEqual(attack_type, "Privilege escalation attempt")
        self.assertIn("failed", reason.lower())
    
    def test_suspicious_user_agent_with_sensitive_path(self):
        """Test suspicious user agent with sensitive path."""
        record = {
            'timestamp': '2024-07-31T00:00:00',
            'source_ip': '177.52.183.80',
            'action': 'allowed',
            'threat_label': 'benign',
            'user_agent': 'Nmap Scripting Engine',
            'request_path': '/admin'
        }
        status, attack_type, reason = self.classifier.classify_activity(record)
        
        # Allowed action with admin path should be detected as high-risk
        self.assertEqual(status, "Malicious")
        self.assertIn("high-risk", reason.lower())
    
    def test_edge_case_empty_fields(self):
        """Test edge case with empty fields."""
        record = {
            'timestamp': '2024-07-31T00:00:00',
            'source_ip': '177.52.183.80',
            'action': 'allowed',
            'threat_label': 'benign',
            'user_agent': '',
            'request_path': ''
        }
        status, attack_type, reason = self.classifier.classify_activity(record)
        
        self.assertEqual(status, "Non-malicious")
        self.assertEqual(attack_type, "None")

if __name__ == '__main__':
    unittest.main()
