# Makefile for Data-Breach Activity Classifier
# Provides convenient targets for setup, testing, and execution

.PHONY: help venv install test run-sample run-batch run-frontend test-batch clean

# Default target
help:
	@echo "Data-Breach Activity Classifier - Available targets:"
	@echo "  venv         - Create/upgrade virtual environment"
	@echo "  install      - Install dependencies"
	@echo "  test         - Run unit tests"
	@echo "  run-sample   - Execute sample CSV row and benign row"
	@echo "  run-batch    - Run batch processing on uploaded CSV"
	@echo "  run-frontend - Start the beautiful web interface"
	@echo "  test-batch   - Test batch processing functionality"
	@echo "  clean        - Clean up generated files"
	@echo ""
	@echo "Quick start: make install && make test"
	@echo "Web interface: make run-frontend"

# Create or upgrade virtual environment
venv:
	@echo "Creating/upgrading virtual environment..."
	python3 -m venv venv
	@echo "Virtual environment created in ./venv"

# Install dependencies
install: venv
	@echo "Installing dependencies..."
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt
	@echo "Dependencies installed"

# Run unit tests
test:
	@echo "Running unit tests..."
	@if [ -d "venv" ]; then \
		./venv/bin/python -m pytest tests/ -v; \
	else \
		python3 -m pytest tests/ -v 2>/dev/null || python3 -m unittest discover tests/ -v; \
	fi
	@echo "Tests completed"

# Run sample single-row tests
run-sample:
	@echo "Running sample tests..."
	@echo "=== Test 1: Malicious activity (suspicious backup access) ==="
	@if [ -d "venv" ]; then \
		./venv/bin/python classify_activity.py "2024-07-31T00:00:00,177.52.183.80,192.168.1.50,HTTPS,blocked,suspicious,ids,45164,\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\",/login?backup.sql"; \
	else \
		python3 classify_activity.py "2024-07-31T00:00:00,177.52.183.80,192.168.1.50,HTTPS,blocked,suspicious,ids,45164,\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\",/login?backup.sql"; \
	fi
	@echo ""
	@echo "=== Test 2: Benign activity (routine login) ==="
	@if [ -d "venv" ]; then \
		./venv/bin/python classify_activity.py "2024-04-07T00:00:00,192.168.1.248,192.168.1.15,HTTP,allowed,benign,application,20652,\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\",/login"; \
	else \
		python3 classify_activity.py "2024-04-07T00:00:00,192.168.1.248,192.168.1.15,HTTP,allowed,benign,application,20652,\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\",/login"; \
	fi
	@echo ""
	@echo "Sample tests completed"

# Run batch processing on uploaded CSV
run-batch:
	@echo "Running batch processing on uploaded CSV..."
	@if [ -d "venv" ]; then \
		./venv/bin/python run_events.py --csv "./cybersecurity_dataset(1).csv" --header; \
	else \
		python3 run_events.py --csv "./cybersecurity_dataset(1).csv" --header; \
	fi
	@echo "Batch processing completed"

# Start the beautiful web interface
run-frontend:
	@echo "Starting CyberGuard Web Interface..."
	@if [ -d "venv" ]; then \
		./venv/bin/python start_cyberguard.py; \
	else \
		echo "Virtual environment not found. Please run 'make install' first."; \
		exit 1; \
	fi

# Test batch processing functionality
test-batch:
	@echo "Testing batch processing..."
	@if [ -d "venv" ]; then \
		./venv/bin/python test_batch_processing.py; \
	else \
		python3 test_batch_processing.py; \
	fi

# Clean up generated files
clean:
	@echo "Cleaning up..."
	rm -rf venv/
	rm -rf __pycache__/
	rm -rf classifier/__pycache__/
	rm -rf tests/__pycache__/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	@echo "Cleanup completed"
