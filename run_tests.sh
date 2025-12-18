#!/bin/bash

# Test script for OnlineBanking Chat API
# Usage: ./run_tests.sh [base_url]
# Default: http://localhost:8000

# Local
# ./run_tests.sh

# Production
# ./run_tests.sh http://157.245.115.120:8000

BASE_URL="${1:-http://localhost:8000}"
ENDPOINT="${BASE_URL}/chat"

echo "============================================"
echo "OnlineBanking Chat API Test Suite"
echo "Testing endpoint: $ENDPOINT"
echo "============================================"
echo ""

# Helper function to run a test
run_test() {
    local test_name="$1"
    local message="$2"
    local check_field="$3"
    local expected="$4"
    
    echo "TEST: $test_name"
    echo "Query: \"$message\""
    
    response=$(curl -s -X POST "$ENDPOINT" \
        -H "Content-Type: application/json" \
        -d "{\"accountId\":\"A123\",\"message\":\"$message\"}")
    
    if [ -z "$response" ]; then
        echo "❌ FAILED - No response"
        echo ""
        return 1
    fi
    
    if echo "$response" | python3 -c "import sys, json; d=json.load(sys.stdin); print('Intent:', d['query']['intent']); print('Time Range:', d['query'].get('time_range', {}).get('preset') or d['query'].get('time_range', {}).get('mode')); print('Message:', d['ui']['messages'][0]['content'][:80]); print('Components:', len(d['ui'].get('components', []))); print('Chart count:', len([c for c in d['ui'].get('components', []) if c.get('type')=='chart']))" 2>&1; then
        echo "✅ PASSED"
    else
        echo "❌ FAILED - Parse error"
        echo "$response" | python3 -m json.tool | head -20
    fi
    echo ""
}

# 1. COUNT-BASED QUERIES
echo "=========================================="
echo "1. COUNT-BASED QUERIES"
echo "=========================================="
run_test "Last 5 transactions" "show me my last 5 transactions"
run_test "Last 10 transactions" "last 10 transactions"
run_test "Most recent 3" "3 most recent transactions"

# 2. TIME-BASED QUERIES
echo "=========================================="
echo "2. TIME-BASED QUERIES"
echo "=========================================="
run_test "This month" "transactions this month"
run_test "Last month" "transactions last month"
run_test "Last week" "show me last week transactions"
run_test "Year to date" "transactions year to date"
run_test "Last 30 days" "transactions from last 30 days"

# 3. TOP SPENDING QUERIES
echo "=========================================="
echo "3. TOP SPENDING QUERIES"
echo "=========================================="
run_test "Top spendings" "what are my top spendings?"
run_test "Where money goes" "where does my money go?"
run_test "Spending categories" "show me my spending categories"
run_test "What I spend most on" "what do I spend the most on?"
run_test "Biggest spending" "what's my biggest spending?"

# 4. SUBSCRIPTION QUERIES
echo "=========================================="
echo "4. SUBSCRIPTION QUERIES"
echo "=========================================="
run_test "Subscriptions" "what are my subscriptions?"
run_test "Recurring payments" "show me my recurring payments"
run_test "Monthly charges" "monthly charges"
run_test "What am I paying monthly" "what am I paying for every month?"

# 5. UNRECOGNIZED TRANSACTION
echo "=========================================="
echo "5. UNRECOGNIZED TRANSACTION"
echo "=========================================="
echo "TEST: Unrecognized transaction (two-step process)"
echo "Step 1: Get transaction list"
txn_response=$(curl -s -X POST "$ENDPOINT" \
    -H "Content-Type: application/json" \
    -d '{"accountId":"A123","message":"show me my last 3 transactions"}')

echo "$txn_response" | python3 -c "import sys, json; d=json.load(sys.stdin); print('Transactions retrieved:', len(d['ui']['components'][0]['rows']) if d['ui'].get('components') else 0)"

echo ""
echo "Step 2: Query unrecognized transaction with context"
# Simulate selecting transaction t001
unrecognized_response=$(curl -s -X POST "$ENDPOINT" \
    -H "Content-Type: application/json" \
    -d '{"accountId":"A123","message":"what is this?","context":{"selectedTransactionId":"t001"}}')

if echo "$unrecognized_response" | python3 -c "import sys, json; d=json.load(sys.stdin); print('Intent:', d['query']['intent']); print('Message:', d['ui']['messages'][0]['content'][:100])" 2>&1; then
    echo "✅ PASSED - Unrecognized transaction handling"
else
    echo "❌ FAILED - Unrecognized transaction"
fi
echo ""

# 6. EDGE CASES
echo "=========================================="
echo "6. EDGE CASES & VARIATIONS"
echo "=========================================="
run_test "This year" "show me transactions this year"
run_test "YTD" "transactions ytd"
run_test "Last 7 days" "last 7 days"
run_test "Recent transactions" "recent transactions"

echo "============================================"
echo "Test Suite Complete"
echo "============================================"
