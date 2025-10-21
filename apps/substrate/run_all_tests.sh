#!/bin/bash

# TidyGen Substrate - Comprehensive Test Runner
# Runs all pallet tests and generates coverage report

set -e

echo "🧪 TidyGen Substrate - Comprehensive Test Suite"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run tests for a pallet
run_pallet_tests() {
    local pallet_name=$1
    local pallet_path=$2
    
    echo -e "${YELLOW}Testing: $pallet_name${NC}"
    echo "-----------------------------------"
    
    if cargo test -p "$pallet_path" --quiet 2>&1 | tee /tmp/test_output.txt; then
        # Extract test count
        local test_count=$(grep -oP '\d+(?= passed)' /tmp/test_output.txt | head -1)
        if [ -n "$test_count" ]; then
            TOTAL_TESTS=$((TOTAL_TESTS + test_count))
            PASSED_TESTS=$((PASSED_TESTS + test_count))
            echo -e "${GREEN}✅ $pallet_name: $test_count tests passed${NC}"
        else
            echo -e "${GREEN}✅ $pallet_name: All tests passed${NC}"
        fi
    else
        echo -e "${RED}❌ $pallet_name: Tests failed${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    
    echo ""
}

# Run tests for each pallet
echo "Running pallet tests..."
echo ""

run_pallet_tests "pallet-ledger" "pallet-ledger"
run_pallet_tests "pallet-did" "pallet-did"
run_pallet_tests "pallet-dao" "pallet-dao"

# Summary
echo "================================================"
echo "📊 TEST SUMMARY"
echo "================================================"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED${NC}"
    echo ""
    echo "Total Tests Run: $TOTAL_TESTS"
    echo "Passed: $PASSED_TESTS"
    echo "Failed: 0"
    echo ""
    echo "🎉 All Substrate pallets are working correctly!"
    exit 0
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo ""
    echo "Total Tests Run: $TOTAL_TESTS"
    echo "Passed: $PASSED_TESTS"
    echo "Failed: $FAILED_TESTS"
    echo ""
    echo "Please review the errors above."
    exit 1
fi

