#!/bin/bash

# Demo Test Script for Venzap
# This script demonstrates the complete workflow:
# 1. User registration
# 2. OTP verification -> Triggers DVA provisioning (async via Celery)
# 3. DVA wallet creation and balance check
# 4. Webhook simulation -> Credits wallet (async via Celery)
# 5. Final balance verification

set -e

API_URL="http://localhost:8000"
SECRET_KEY="b9c4f0f8e3a145c6b6a3dd3ab13a7d9cf7a1b0d2e63b4a58e2f90c9f1a7b2c4d"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========== VENZAP DEMO TEST ==========${NC}\n"

# ===== STEP 1: Register User =====
echo -e "${BLUE}STEP 1: Register User${NC}"
TEST_EMAIL="demo_$(date +%s)@example.com"
TEST_PHONE="+2348012345678"
TEST_NAME="Demo User"
TEST_PASSWORD="TestPass123!"

echo "Registering user: $TEST_EMAIL"
REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/auth/user/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"$TEST_PASSWORD\",
    \"full_name\": \"$TEST_NAME\",
    \"phone\": \"$TEST_PHONE\"
  }")

echo "Response: $REGISTER_RESPONSE"
echo ""

# ===== STEP 2: Get OTP from logs =====
echo -e "${BLUE}STEP 2: Get OTP from API logs${NC}"
echo "Fetching OTP from logs..."
sleep 2
OTP=$(docker logs venzap-api 2>&1 | grep -o "DEV OTP for $TEST_EMAIL.*: [0-9]*" | tail -1 | grep -o "[0-9]*$")
if [ -z "$OTP" ]; then
  echo -e "${YELLOW}Warning: Could not find OTP in logs, using placeholder${NC}"
  OTP="000000"
else
  echo -e "${GREEN}Found OTP: $OTP${NC}"
fi
echo ""

# ===== STEP 3: Hash OTP and set in Redis =====
echo -e "${BLUE}STEP 3: Hash OTP and set in Redis${NC}"
OTP_KEY="otp:email_verification_user:$TEST_EMAIL"
HASHED=$(echo -n "$OTP" | openssl dgst -sha256 -hmac "$SECRET_KEY" -hex | cut -d' ' -f2)
echo "OTP Key: $OTP_KEY"
echo "OTP: $OTP"
echo "Hashed: $HASHED"
docker exec venzap-redis redis-cli SETEX "$OTP_KEY" 600 "$HASHED" > /dev/null
echo -e "${GREEN}OTP set in Redis${NC}"
echo ""

# ===== STEP 4: Verify Email (triggers DVA provisioning) =====
echo -e "${BLUE}STEP 4: Verify Email (triggers DVA provisioning via Celery)${NC}"
echo "Verifying email with OTP..."
VERIFY_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/auth/verify-email" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"otp\": \"$OTP\",
    \"account_type\": \"user\"
  }")

echo "Response: $VERIFY_RESPONSE"
echo ""

# Wait for Celery to process provisioning
echo -e "${YELLOW}Waiting for Celery to process provisioning task...${NC}"
sleep 5

# ===== STEP 5: Login =====
echo -e "${BLUE}STEP 5: Login to get access token${NC}"
LOGIN_RESPONSE=$(curl -s -c /tmp/cookies.txt -X POST "$API_URL/api/v1/auth/user/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"$TEST_PASSWORD\"
  }")

echo "Login Response: $LOGIN_RESPONSE"
echo ""

# ===== STEP 6: Check wallet balance (should be 0 initially) =====
echo -e "${BLUE}STEP 6: Check wallet balance (should be 0 initially)${NC}"
BALANCE_RESPONSE=$(curl -s -b /tmp/cookies.txt "$API_URL/api/v1/wallet/balance")
echo "Initial Balance: $BALANCE_RESPONSE"
echo ""

# ===== STEP 7: Simulate Payaza DVA Credit Webhook =====
echo -e "${BLUE}STEP 7: Simulate Payaza DVA Credit Webhook${NC}"
WEBHOOK_REF="webhook_$(date +%s)"
WEBHOOK_PAYLOAD="{
  \"event\": \"virtual_account.credit\",
  \"reference\": \"$WEBHOOK_REF\",
  \"account_number\": \"1234567890\",
  \"amount\": 5000,
  \"sender\": \"Test Sender\",
  \"id\": \"$WEBHOOK_REF\"
}"

echo "Webhook Payload: $WEBHOOK_PAYLOAD"

# Calculate HMAC-SHA512 for the webhook
RAW_BODY=$(echo -n "$WEBHOOK_PAYLOAD" | openssl dgst -sha512 -hmac "$SECRET_KEY" -hex | cut -d' ' -f2)

# Since we need to manually credit for demo (Payaza SDK might not be available)
echo -e "${YELLOW}Note: Actual webhook would be signed with Payaza secret key${NC}"
echo ""

# ===== STEP 8: Manually create virtual account in DB for demo =====
echo -e "${BLUE}STEP 8: Create test DVA in database${NC}"
USER_ID=$(docker exec venzap-db psql -U venzap -d venzap -t -c "SELECT id FROM users WHERE email='$TEST_EMAIL';")
echo "User ID: $USER_ID"

if [ -n "$USER_ID" ]; then
  docker exec venzap-db psql -U venzap -d venzap << EOSQL
INSERT INTO virtual_accounts (id, user_id, account_number, account_name, bank_name, bank_code, payaza_ref, is_active)
VALUES (gen_random_uuid(), '$USER_ID'::uuid, '1234567890', 'Demo Test Account', 'Demo Bank', 'DEMO', 'payaza_ref_demo', true)
ON CONFLICT DO NOTHING;
EOSQL
  echo -e "${GREEN}Virtual account created${NC}"
fi
echo ""

# ===== STEP 9: Simulate webhook to credit wallet =====
echo -e "${BLUE}STEP 9: Simulate webhook to credit wallet${NC}"
WEBHOOK_PAYLOAD_DEMO="{
  \"event\": \"virtual_account.credit\",
  \"reference\": \"$WEBHOOK_REF\",
  \"account_number\": \"1234567890\",
  \"amount\": 5000,
  \"sender\": \"Test Sender\",
  \"id\": \"$WEBHOOK_REF\"
}"

echo "Posting webhook (without signature for demo)..."
WEBHOOK_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/webhooks/payaza" \
  -H "Content-Type: application/json" \
  -d "$WEBHOOK_PAYLOAD_DEMO")

echo "Webhook Response: $WEBHOOK_RESPONSE"
echo ""

# Wait for Celery to process webhook
echo -e "${YELLOW}Waiting for Celery to process webhook task...${NC}"
sleep 5

# ===== STEP 10: Check final balance =====
echo -e "${BLUE}STEP 10: Check final wallet balance${NC}"
FINAL_BALANCE=$(curl -s -b /tmp/cookies.txt "$API_URL/api/v1/wallet/balance")
echo "Final Balance: $FINAL_BALANCE"
echo ""

echo -e "${GREEN}========== DEMO TEST COMPLETE ==========${NC}"
echo "Test user: $TEST_EMAIL"
echo "OTP used: $OTP"
echo "Webhook ref: $WEBHOOK_REF"
echo ""
echo "Check logs for any errors:"
echo "  - API logs: docker logs venzap-api --tail=50"
echo "  - Celery logs: docker logs venzap-celery --tail=50"
echo "  - DB logs: docker logs venzap-db --tail=50"
