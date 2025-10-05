#!/usr/bin/env python3
"""
Unit tests for CSV and JSON parsing functionality.
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from classifier.core import ActivityClassifier

class TestParser(unittest.TestCase):
    """Test parsing functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.classifier = ActivityClassifier()
    
    def test_csv_parsing_valid(self):
        """Test valid CSV parsing."""
        csv_line = '2024-07-31T00:00:00,177.52.183.80,192.168.1.50,HTTPS,blocked,suspicious,ids,45164,"Mozilla/5.0",/login'
        success, record, error = self.classifier.parse_input(csv_line)
        
        self.assertTrue(success)
        self.assertEqual(record['timestamp'], '2024-07-31T00:00:00')
        self.assertEqual(record['source_ip'], '177.52.183.80')
        self.assertEqual(record['action'], 'blocked')
        self.assertEqual(record['threat_label'], 'suspicious')
    
    def test_csv_parsing_with_quotes(self):
        """Test CSV parsing with quoted fields."""
        csv_line = '"2024-07-31T00:00:00","177.52.183.80","192.168.1.50","HTTPS","blocked","suspicious","ids","45164","Mozilla/5.0","/login"'
        success, record, error = self.classifier.parse_input(csv_line)
        
        self.assertTrue(success)
        self.assertEqual(record['timestamp'], '2024-07-31T00:00:00')
        self.assertEqual(record['action'], 'blocked')
    
    def test_csv_parsing_extra_commas(self):
        """Test CSV parsing with extra commas."""
        csv_line = '2024-07-31T00:00:00,177.52.183.80,192.168.1.50,HTTPS,blocked,suspicious,ids,45164,"Mozilla,5.0",/login'
        success, record, error = self.classifier.parse_input(csv_line)
        
        self.assertTrue(success)
        self.assertEqual(record['user_agent'], 'Mozilla,5.0')
    
    def test_csv_parsing_whitespace(self):
        """Test CSV parsing with whitespace."""
        csv_line = '  2024-07-31T00:00:00  ,  177.52.183.80  ,  192.168.1.50  ,  HTTPS  ,  blocked  ,  suspicious  ,  ids  ,  45164  ,  "Mozilla/5.0"  ,  /login  '
        success, record, error = self.classifier.parse_input(csv_line)
        
        self.assertTrue(success)
        self.assertEqual(record['timestamp'], '2024-07-31T00:00:00')
        self.assertEqual(record['action'], 'blocked')
    
    def test_json_parsing_valid(self):
        """Test valid JSON parsing."""
        json_line = '{"timestamp": "2024-07-31T00:00:00", "source_ip": "177.52.183.80", "action": "blocked", "threat_label": "suspicious", "user_agent": "Mozilla/5.0", "request_path": "/login"}'
        success, record, error = self.classifier.parse_input(json_line)
        
        self.assertTrue(success)
        self.assertEqual(record['timestamp'], '2024-07-31T00:00:00')
        self.assertEqual(record['source_ip'], '177.52.183.80')
        self.assertEqual(record['action'], 'blocked')
    
    def test_json_parsing_with_label_alias(self):
        """Test JSON parsing with label field alias."""
        json_line = '{"timestamp": "2024-07-31T00:00:00", "source_ip": "177.52.183.80", "action": "blocked", "label": "suspicious", "user_agent": "Mozilla/5.0", "request_path": "/login"}'
        success, record, error = self.classifier.parse_input(json_line)
        
        self.assertTrue(success)
        self.assertEqual(record['threat_label'], 'suspicious')
    
    def test_json_parsing_with_file_name_alias(self):
        """Test JSON parsing with file_name field alias."""
        json_line = '{"timestamp": "2024-07-31T00:00:00", "source_ip": "177.52.183.80", "action": "blocked", "threat_label": "suspicious", "user_agent": "Mozilla/5.0", "file_name": "/login"}'
        success, record, error = self.classifier.parse_input(json_line)
        
        self.assertTrue(success)
        self.assertEqual(record['request_path'], '/login')
    
    def test_parsing_invalid_csv(self):
        """Test invalid CSV parsing."""
        csv_line = 'invalid,csv,format,with,malformed,data'
        success, record, error = self.classifier.parse_input(csv_line)
        
        # This might succeed as CSV but fail validation
        if success:
            # If parsing succeeds, validation should fail
            is_valid, validation_error = self.classifier.validate_record(record)
            self.assertFalse(is_valid)
        else:
            self.assertIn("Could not parse", error)
    
    def test_parsing_invalid_json(self):
        """Test invalid JSON parsing."""
        json_line = '{"invalid": json, format}'
        success, record, error = self.classifier.parse_input(json_line)
        
        # This might succeed as CSV but should fail validation
        if success:
            is_valid, validation_error = self.classifier.validate_record(record)
            self.assertFalse(is_valid)
        else:
            self.assertIn("Could not parse", error)
    
    def test_parsing_empty_input(self):
        """Test empty input parsing."""
        success, record, error = self.classifier.parse_input("")
        
        self.assertFalse(success)
        self.assertIn("Could not parse", error)
    
    def test_validation_valid_record(self):
        """Test validation of valid record."""
        record = {
            'timestamp': '2024-07-31T00:00:00',
            'source_ip': '177.52.183.80',
            'action': 'blocked',
            'threat_label': 'suspicious',
            'user_agent': 'Mozilla/5.0',
            'request_path': '/login'
        }
        is_valid, error = self.classifier.validate_record(record)
        
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
    
    def test_validation_missing_fields(self):
        """Test validation with missing fields."""
        record = {
            'timestamp': '2024-07-31T00:00:00',
            'source_ip': '177.52.183.80',
            'action': 'blocked'
            # Missing threat_label, user_agent, request_path
        }
        is_valid, error = self.classifier.validate_record(record)
        
        self.assertFalse(is_valid)
        self.assertIn("Missing required fields", error)
    
    def test_validation_invalid_action(self):
        """Test validation with invalid action."""
        record = {
            'timestamp': '2024-07-31T00:00:00',
            'source_ip': '177.52.183.80',
            'action': 'invalid_action',
            'threat_label': 'suspicious',
            'user_agent': 'Mozilla/5.0',
            'request_path': '/login'
        }
        is_valid, error = self.classifier.validate_record(record)
        
        self.assertFalse(is_valid)
        self.assertIn("Invalid action", error)
    
    def test_validation_invalid_threat_label(self):
        """Test validation with invalid threat_label."""
        record = {
            'timestamp': '2024-07-31T00:00:00',
            'source_ip': '177.52.183.80',
            'action': 'blocked',
            'threat_label': 'invalid_label',
            'user_agent': 'Mozilla/5.0',
            'request_path': '/login'
        }
        is_valid, error = self.classifier.validate_record(record)
        
        self.assertFalse(is_valid)
        self.assertIn("Invalid threat_label", error)

if __name__ == '__main__':
    unittest.main()
