#!/bin/bash
# POSIX-compliant runner script for Data-Breach Activity Classifier
# Demonstrates single-row CLI and batch processing

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Determine Python executable
if [ -d "venv" ] && [ -f "venv/bin/python" ]; then
    PYTHON="venv/bin/python"
    print_status "Using virtual environment Python"
else
    PYTHON="python3"
    print_warning "Using system Python (consider running 'make venv' first)"
fi

# Test Python availability
if ! command -v "$PYTHON" >/dev/null 2>&1; then
    print_error "Python not found. Please install Python 3.6+ and try again."
    exit 1
fi

print_status "Data-Breach Activity Classifier Demo"
echo "=================================================="

# Test 1: Single-row CLI - Malicious activity
print_status "Test 1: Single-row CLI - Malicious activity (suspicious backup access)"
echo "Command: $PYTHON classify_activity.py \"2024-07-31T00:00:00,177.52.183.80,192.168.1.50,HTTPS,blocked,suspicious,ids,45164,\\\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\\\",/login?backup.sql\""
echo "Output:"
$PYTHON classify_activity.py "2024-07-31T00:00:00,177.52.183.80,192.168.1.50,HTTPS,blocked,suspicious,ids,45164,\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\",/login?backup.sql"
echo ""

# Test 2: Single-row CLI - Benign activity
print_status "Test 2: Single-row CLI - Benign activity (routine login)"
echo "Command: $PYTHON classify_activity.py \"2024-04-07T00:00:00,192.168.1.248,192.168.1.15,HTTP,allowed,benign,application,20652,\\\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\\\",/login\""
echo "Output:"
$PYTHON classify_activity.py "2024-04-07T00:00:00,192.168.1.248,192.168.1.15,HTTP,allowed,benign,application,20652,\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\",/login"
echo ""

# Test 3: Error handling - Invalid input
print_status "Test 3: Error handling - Invalid input (missing fields)"
echo "Command: $PYTHON classify_activity.py \"invalid,input,format\""
echo "Output:"
$PYTHON classify_activity.py "invalid,input,format" || true
echo ""

# Test 4: Batch processing (first 5 rows only for demo)
print_status "Test 4: Batch processing - First 5 rows of uploaded CSV"
echo "Command: $PYTHON run_events.py --csv \"./cybersecurity_dataset(1).csv\" --header | head -20"
echo "Output:"

# Create a temporary file with first 5 rows for demo
head -6 "./cybersecurity_dataset(1).csv" > "/tmp/demo_sample.csv"

$PYTHON run_events.py --csv "/tmp/demo_sample.csv" --header | head -20
echo ""

# Cleanup
rm -f "/tmp/demo_sample.csv"

print_status "Demo completed successfully!"
echo ""
echo "Usage examples:"
echo "  Single row: $PYTHON classify_activity.py \"<CSV_row>\""
echo "  Batch mode: $PYTHON run_events.py --csv <file.csv> --header"
echo "  JSON mode:  $PYTHON run_events.py --json <file.jsonl>"
echo ""
echo "Setup commands:"
echo "  make install && make test"






