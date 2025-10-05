#!/usr/bin/env python3
"""
Robust CLI interface for the data-breach activity classifier.
Handles CSV parsing, validation, and error handling for chatbot integration.
"""

import sys
from classifier.core import ActivityClassifier

def main():
    """Main CLI entry point with robust error handling."""
    # Check argument count
    if len(sys.argv) == 1:
        print("Error: No input provided—please pass a single CSV row string.")
        sys.exit(1)
    elif len(sys.argv) > 2:
        print("Error: Too many arguments—please pass exactly one CSV row string.")
        sys.exit(1)
    
    # Get and validate input
    input_line = sys.argv[1].strip()
    if not input_line:
        print("Error: No input provided—please pass a single CSV row string.")
        sys.exit(1)
    
    # Process the activity
    classifier = ActivityClassifier()
    success, result = classifier.process_activity(input_line)
    
    if success:
        # Print the 3-line classification result
        print(result)
        sys.exit(0)
    else:
        # Print error message
        print(result)
        sys.exit(1)

if __name__ == "__main__":
    main()
