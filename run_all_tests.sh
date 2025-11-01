#!/bin/bash
# Master Test Script - Run all tests in sequence
# This demonstrates the complete trading bot functionality

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║         FALAH TRADING BOT V2 - TEST SUITE               ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Activate virtual environment
source venv/bin/activate

# Run all tests
echo "Running Test Suite..."
echo ""

python3 test_supertrend.py
read -p "Press Enter to continue to next test..."

python3 test_strategy.py
read -p "Press Enter to continue to next test..."

python3 test_enhanced.py
read -p "Press Enter to continue to next test..."

python3 test_parameters.py
read -p "Press Enter to continue to next test..."

python3 test_risk.py
read -p "Press Enter to continue to next test..."

python3 test_markets.py

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║              ✅ ALL TESTS COMPLETED!                     ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
