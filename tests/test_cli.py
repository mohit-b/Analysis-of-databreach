#!/usr/bin/env python3
"""
Unit tests for CLI functionality and exit codes.
"""

import unittest
import subprocess
import sys
import os
from pathlib import Path

class TestCLI(unittest.TestCase):
    """Test CLI functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.script_path = Path(__file__).parent.parent / "classify_activity.py"
        self.python_cmd = [sys.executable, str(self.script_path)]
    
    def test_no_arguments(self):
        """Test behavior with no arguments."""
        result = subprocess.run(self.python_cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Error: No input provided", result.stdout)
    
    def test_empty_input(self):
        """Test behavior with empty input."""
        result = subprocess.run(self.python_cmd + [""], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Error: No input provided", result.stdout)
    
    def test_whitespace_only_input(self):
        """Test behavior with whitespace-only input."""
        result = subprocess.run(self.python_cmd + ["   "], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Error: No input provided", result.stdout)
    
    def test_too_many_arguments(self):
        """Test behavior with too many arguments."""
        result = subprocess.run(
            self.python_cmd + ["arg1", "arg2"], 
            capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Error: Too many arguments", result.stdout)
    
    def test_valid_malicious_input(self):
        """Test valid malicious input produces correct output."""
        input_line = '2024-07-31T00:00:00,177.52.183.80,192.168.1.50,HTTPS,blocked,suspicious,ids,45164,"Mozilla/5.0",/login?backup.sql'
        result = subprocess.run(
            self.python_cmd + [input_line], 
            capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0)
        lines = result.stdout.strip().split('\n')
        self.assertEqual(len(lines), 3)
        self.assertTrue(lines[0].startswith("Activity status: Malicious"))
        self.assertTrue(lines[1].startswith("Type of attack:"))
        self.assertTrue(lines[2].startswith("Reason:"))
    
    def test_valid_benign_input(self):
        """Test valid benign input produces correct output."""
        input_line = '2024-04-07T00:00:00,192.168.1.248,192.168.1.15,HTTP,allowed,benign,application,20652,"Mozilla/5.0",/login'
        result = subprocess.run(
            self.python_cmd + [input_line], 
            capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0)
        lines = result.stdout.strip().split('\n')
        self.assertEqual(len(lines), 3)
        self.assertTrue(lines[0].startswith("Activity status: Non-malicious"))
        self.assertTrue(lines[1].startswith("Type of attack: None"))
        self.assertTrue(lines[2].startswith("Reason:"))
    
    def test_invalid_csv_format(self):
        """Test invalid CSV format produces error."""
        input_line = "invalid,csv,format"
        result = subprocess.run(
            self.python_cmd + [input_line], 
            capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Error:", result.stdout)
    
    def test_invalid_action_value(self):
        """Test invalid action value produces error."""
        input_line = '2024-07-31T00:00:00,177.52.183.80,192.168.1.50,HTTPS,invalid_action,suspicious,ids,45164,"Mozilla/5.0",/login'
        result = subprocess.run(
            self.python_cmd + [input_line], 
            capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Error:", result.stdout)
    
    def test_invalid_threat_label(self):
        """Test invalid threat_label value produces error."""
        input_line = '2024-07-31T00:00:00,177.52.183.80,192.168.1.50,HTTPS,blocked,invalid_label,ids,45164,"Mozilla/5.0",/login'
        result = subprocess.run(
            self.python_cmd + [input_line], 
            capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Error:", result.stdout)
    
    def test_json_fallback(self):
        """Test JSON input fallback works."""
        json_input = '{"timestamp": "2024-07-31T00:00:00", "source_ip": "177.52.183.80", "action": "blocked", "threat_label": "suspicious", "user_agent": "Mozilla/5.0", "request_path": "/login?backup.sql"}'
        result = subprocess.run(
            self.python_cmd + [json_input], 
            capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0)
        lines = result.stdout.strip().split('\n')
        self.assertEqual(len(lines), 3)

if __name__ == '__main__':
    unittest.main()








