#!/bin/bash
# Integration test runner for TidyGen Community

set -e

echo "🧪 Running TidyGen Integration Tests"
echo "===================================="

# Check if pytest is available
if ! command -v pytest >/dev/null 2>&1; then
    echo "❌ pytest is not installed. Installing..."
    pip install pytest
fi

# Run integration tests
echo "📋 Running Substrate POC Quickstart Integration Test..."
echo ""

# Run the specific integration test
pytest tests/integration/test_substrate_poc_quickstart.py -v

echo ""
echo "✅ Integration tests completed!"
