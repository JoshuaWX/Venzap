#!/bin/bash

# Simplified Demo Test - Focus on Order Workflow
# This tests the most critical end-to-end flow

set -e

API_URL="http://localhost:8000"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========== VENZAP ORDER WORKFLOW TEST ==========${NC}\n"

# ===== Use existing test user =====
echo -e "${BLUE}STEP 1: Login with existing test user${NC}"
TEST_EMAIL="testuser2024@example.com"
TEST_PASSWORD="TestPassword123!"

echo "Logging in as: $TEST_EMAIL"
curl -s -c /tmp/cookies.txt -X POST "$API_URL/api/v1/auth/user/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$TEST_EMAIL\", \"password\": \"$TEST_PASSWORD\"}" | python3 -m json.tool 2>/dev/null || echo "Login initiated"

sleep 2
echo ""

# ===== Check wallet balance =====
echo -e "${BLUE}STEP 2: Check current wallet balance${NC}"
WALLET=$(curl -s -b /tmp/cookies.txt "$API_URL/api/v1/wallet/balance")
echo "Wallet: $WALLET"
echo ""

# ===== Get vendors =====
echo -e "${BLUE}STEP 3: Get list of vendors${NC}"
VENDORS=$(curl -s -b /tmp/cookies.txt "$API_URL/api/v1/vendors")
echo "Vendors Response (first 200 chars): $(echo $VENDORS | cut -c1-200)..."
echo ""

# ===== Get catalogue items =====
echo -e "${BLUE}STEP 4: Get catalogue items${NC}"
CATALOGUE=$(curl -s -b /tmp/cookies.txt "$API_URL/api/v1/catalogue/items")
echo "Catalogue Response (first 200 chars): $(echo $CATALOGUE | cut -c1-200)..."
echo ""

# ===== Create an order =====
echo -e "${BLUE}STEP 5: Create test order${NC}"
ORDER_PAYLOAD="{
  \"items\": [
    {
      \"catalogue_item_id\": \"550e8400-e29b-41d4-a716-446655440000\",
      \"quantity\": 1
    }
  ]
}"
echo "Order Payload: $ORDER_PAYLOAD"
ORDER=$(curl -s -b /tmp/cookies.txt -X POST "$API_URL/api/v1/orders" \
  -H "Content-Type: application/json" \
  -d "$ORDER_PAYLOAD")
echo "Order Response: $ORDER"
echo ""

echo -e "${GREEN}========== TEST COMPLETE ==========${NC}"
echo ""
echo "Check logs for details:"
echo "  - API: docker logs venzap-api --tail=100"
echo "  - Celery: docker logs venzap-celery --tail=100"
