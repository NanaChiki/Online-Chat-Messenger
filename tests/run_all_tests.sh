# tests/run_all_tests.sh - Script to run all tests
#!/bin/bash

echo "🚀 Running Stage 1 Test Suite"
echo "=============================="

echo ""
echo "1️⃣ Running Protocol Unit Tests..."
python3 tests/test_protocol.py

echo ""
echo "2️⃣ Running Integration Tests..."
python3 tests/integration_tests.py

echo ""
echo "3️⃣ Manual Test Options Available:"
echo "   python3 tests/manual_test_scenarios.py"

echo ""
echo "✅ Automated tests completed!"
echo "🎯 Run manual tests to verify full functionality."

