#!/bin/bash

# TidyGen - Complete Multi-Layer Test Suite
# Runs tests across all three architectural layers

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🧪 TidyGen - Complete Test Suite${NC}"
echo "===================================================="
echo ""

# Track results
FRONTEND_PASS=0
BACKEND_PASS=0
SUBSTRATE_PASS=0

# 1. Frontend Tests
echo -e "${YELLOW}📱 LAYER 1: Frontend Tests (Vitest + MSW)${NC}"
echo "----------------------------------------------------"
cd apps/frontend
if npm test -- --run --reporter=verbose; then
    echo -e "${GREEN}✅ Frontend tests passed${NC}"
    FRONTEND_PASS=1
else
    echo -e "${RED}❌ Frontend tests failed${NC}"
fi
echo ""
cd ../..

# 2. Backend Tests
echo -e "${YELLOW}🐍 LAYER 2: Backend Tests (Pytest)${NC}"
echo "----------------------------------------------------"
cd apps/backend
if [ -d "venv" ]; then
    source venv/bin/activate
    if pytest services/tests/test_substrate_integration.py -v --tb=short; then
        echo -e "${GREEN}✅ Backend tests passed${NC}"
        BACKEND_PASS=1
    else
        echo -e "${RED}❌ Backend tests failed${NC}"
    fi
    deactivate
else
    echo -e "${RED}❌ Virtual environment not found${NC}"
fi
echo ""
cd ../..

# 3. Substrate Tests
echo -e "${YELLOW}⚙️  LAYER 3: Substrate Tests (Cargo)${NC}"
echo "----------------------------------------------------"
cd apps/substrate
if [ -f "run_all_tests.sh" ]; then
    if ./run_all_tests.sh; then
        echo -e "${GREEN}✅ Substrate tests passed${NC}"
        SUBSTRATE_PASS=1
    else
        echo -e "${RED}❌ Substrate tests failed${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  run_all_tests.sh not found, running cargo test${NC}"
    if cargo test -p pallet-ledger && cargo test -p pallet-did && cargo test -p pallet-dao; then
        echo -e "${GREEN}✅ Substrate tests passed${NC}"
        SUBSTRATE_PASS=1
    else
        echo -e "${RED}❌ Substrate tests failed${NC}"
    fi
fi
echo ""
cd ../..

# Summary
echo "===================================================="
echo -e "${BLUE}📊 TEST SUMMARY${NC}"
echo "===================================================="
echo ""

TOTAL_PASS=$((FRONTEND_PASS + BACKEND_PASS + SUBSTRATE_PASS))

echo -e "Frontend (Vitest):  $([ $FRONTEND_PASS -eq 1 ] && echo -e '${GREEN}✅ PASS${NC}' || echo -e '${RED}❌ FAIL${NC}')"
echo -e "Backend (Pytest):   $([ $BACKEND_PASS -eq 1 ] && echo -e '${GREEN}✅ PASS${NC}' || echo -e '${RED}❌ FAIL${NC}')"
echo -e "Substrate (Cargo):  $([ $SUBSTRATE_PASS -eq 1 ] && echo -e '${GREEN}✅ PASS${NC}' || echo -e '${RED}❌ FAIL${NC}')"
echo ""

if [ $TOTAL_PASS -eq 3 ]; then
    echo -e "${GREEN}🎉 ALL LAYERS PASSED! Complete test suite successful.${NC}"
    echo ""
    echo "Test Coverage:"
    echo "  • Frontend: 15+ tests"
    echo "  • Backend: 16 tests"
    echo "  • Substrate: 51 tests"
    echo "  • TOTAL: 82+ tests"
    exit 0
else
    echo -e "${RED}⚠️  $((3 - TOTAL_PASS)) layer(s) failed${NC}"
    echo "Please review the errors above."
    exit 1
fi

