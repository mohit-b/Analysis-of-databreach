#!/usr/bin/env python3
"""
Batch runner for processing multiple activity records.
Supports CSV and JSON input formats with header detection.
"""

import sys
import csv
import json
import argparse
from pathlib import Path
from classifier.core import ActivityClassifier

def process_csv_file(file_path: str, has_header: bool = False) -> int:
    """
    Process a CSV file with activity records.
    
    Args:
        file_path: Path to CSV file
        has_header: Whether first row is a header
        
    Returns:
        Exit code (0 for success, 1 for file errors)
    """
    try:
        classifier = ActivityClassifier()
        
        with open(file_path, 'r', encoding='utf-8') as file:
            if has_header:
                # Skip header row
                next(file)
            
            line_count = 0
            for line in file:
                line_count += 1
                line = line.strip()
                if not line:
                    continue
                
                # Process each line
                success, result = classifier.process_activity(line)
                
                if success:
                    print(result)
                    print()  # Blank line separator
                else:
                    print(result)
                    print()  # Blank line separator
        
        if line_count == 0:
            print("Error: No data rows found in file")
            return 1
            
        return 0
        
    except FileNotFoundError:
        print("Error: File not found")
        return 1
    except PermissionError:
        print("Error: Permission denied reading file")
        return 1
    except Exception as e:
        print(f"Error: Failed to process CSV file: {str(e)}")
        return 1

def process_json_file(file_path: str) -> int:
    """
    Process a JSON Lines file with activity records.
    
    Args:
        file_path: Path to JSON Lines file
        
    Returns:
        Exit code (0 for success, 1 for file errors)
    """
    try:
        classifier = ActivityClassifier()
        
        with open(file_path, 'r', encoding='utf-8') as file:
            line_count = 0
            for line in file:
                line_count += 1
                line = line.strip()
                if not line:
                    continue
                
                # Process each line as JSON
                success, result = classifier.process_activity(line)
                
                if success:
                    print(result)
                    print()  # Blank line separator
                else:
                    print(result)
                    print()  # Blank line separator
        
        if line_count == 0:
            print("Error: No data rows found in file")
            return 1
            
        return 0
        
    except FileNotFoundError:
        print("Error: File not found")
        return 1
    except PermissionError:
        print("Error: Permission denied reading file")
        return 1
    except Exception as e:
        print(f"Error: Failed to process JSON file: {str(e)}")
        return 1

def main():
    """Main entry point for batch processing."""
    parser = argparse.ArgumentParser(
        description="Batch process activity records from CSV or JSON files"
    )
    
    # Input file options
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--csv', type=str, help='Path to CSV file')
    group.add_argument('--json', type=str, help='Path to JSON Lines file')
    
    # CSV options
    parser.add_argument('--header', action='store_true', 
                       help='Treat first row as header (CSV only)')
    
    args = parser.parse_args()
    
    # Validate file exists
    if args.csv:
        if not Path(args.csv).exists():
            print(f"Error: CSV file not found: {args.csv}")
            sys.exit(1)
        return process_csv_file(args.csv, args.header)
    
    elif args.json:
        if not Path(args.json).exists():
            print(f"Error: JSON file not found: {args.json}")
            sys.exit(1)
        return process_json_file(args.json)

if __name__ == "__main__":
    sys.exit(main())






