#!/bin/bash
# Quick testing script for threat fingerprinting project

echo "Threat Fingerprinting - Testing Script"
echo "======================================="
echo ""

# Activate venv
source venv/Scripts/activate

# Check if pytest is installed
if ! python -m pytest --version > /dev/null 2>&1; then
    echo "Installing pytest..."
    pip install pytest pytest-cov
fi

echo ""
echo "Running all tests..."
echo ""

# Run tests with summary
python -m pytest tests/ -v --tb=short

echo ""
echo "Test Summary:"
python -m pytest tests/ --co -q | wc -l

echo ""
echo "To run specific tests:"
echo "  pytest tests/test_data_validation.py -v"
echo "  pytest tests/test_execution.py -v"
echo "  pytest tests/test_search_functionality.py -v"
echo ""
echo "For coverage report:"
echo "  pytest tests/ --cov=scripts --cov-report=html"
