# Venzap - MVP Demo & Development Guide

## Overview

Venzap is a platform for managing virtual accounts, wallets, and vendor marketplaces. This document outlines how to set up, run, and demo the application.

## Tech Stack

- **Backend**: Python 3.11, FastAPI, SQLAlchemy, Pydantic v2
- **Database**: PostgreSQL 15
- **Cache/Broker**: Redis 7
- **Async Task Queue**: Celery 5.3.6
- **Payment Integration**: Payaza (DVA provisioning)
- **Infrastructure**: Docker Compose, Nginx, Uvicorn
- **Security**: JWT (HS256), HMAC-SHA512 webhook verification, httpOnly cookies

## Project Structure

```
Venzap/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app entry point
│   │   ├── config.py               # Settings/configuration
│   │   ├── celery_app.py           # Celery app with task discovery
│   │   ├── models/                 # SQLAlchemy models
│   │   ├── routers/                # API route handlers
│   │   ├── services/               # Business logic
│   │   │   ├── auth_service.py
│   │   │   ├── virtual_account_service.py
│   │   │   ├── payaza_service.py
│   │   │   ├── webhook_service.py
│   │   │   ├── email_service.py
│   │   │   └── wallet_service.py
│   │   ├── schemas/                # Pydantic schemas
│   │   ├── utils/                  # Utilities & helpers
│   │   └── migrations/             # Alembic migrations
│   └── Dockerfile
├── bot/                             # Telegram bot
├── frontend/                        # React frontend
├── docker-compose.yml              # Service orchestration
├── .env                            # Environment variables
└── README.md                       # This file
```

## Prerequisites

### System Requirements
- Docker & Docker Compose (Windows WSL2 or Linux)
- At least 4GB RAM allocated to Docker
- Terminal/CLI access

### Configured Environment
All required environment variables are pre-configured in `.env`:
- Database: PostgreSQL 15 (internal Docker hostname: `db`)
- Redis: Redis 7 (internal Docker hostname: `redis`)
- Payaza Integration: Test credentials
- JWT Secrets: Pre-configured

## Getting Started

### 1. Start the Docker Stack

```bash
cd /c/dev-folder/Venzap
docker-compose up -d --build
```

This starts:
- **venzap-db**: PostgreSQL 15 container
- **venzap-redis**: Redis 7 container (persistence enabled)
- **venzap-api**: FastAPI backend (port 8000)
- **venzap-celery**: Celery worker for async tasks
- **venzap-bot**: Telegram bot (optional)
- **venzap-nginx**: Reverse proxy (port 80)

### 2. Verify Services Health

```bash
# Check database
docker exec venzap-db pg_isready -U venzap

# Check Redis
docker exec venzap-redis redis-cli ping

# Check API health
curl http://localhost:8000/health

# Check Celery worker
docker logs venzap-celery | grep "ready"
```

### SMTP Setup

Venzap sends OTP and support emails through SMTP when these variables are set:

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
SUPPORT_EMAIL=support@venzap.ng
```

Use a provider-specific app password for Gmail or the equivalent SMTP credentials from Mailgun, Resend SMTP, SendGrid SMTP, or your mail host. In development, the app will log and skip email delivery if these values are missing.

### Telegram Setup

The bot is a separate long-running service. To get it working locally or on Railway, set:

```bash
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
BACKEND_API_BASE_URL=http://localhost:8000
REDIS_URL=redis://localhost:6379
```

Then run the bot container or process on its own. It uses polling by default, so no webhook setup is required for the hackathon demo.

### Production Split

Recommended hosting layout:

```text
Vercel   -> frontend/
Railway  -> backend API + Celery worker + Telegram bot
Supabase -> PostgreSQL database
Redis    -> Railway Redis or Upstash Redis
```

For the frontend, set `NEXT_PUBLIC_API_BASE_URL` to the Railway API URL. For the backend, set `DATABASE_URL` to the Supabase connection string, `REDIS_URL` to your hosted Redis URL, and `FRONTEND_URL` to the Vercel domain.

### 3. Run Database Migrations

Database migrations run automatically on API startup. To verify:

```bash
docker exec venzap-db psql -U venzap -d venzap \
  -c "SELECT migration_name FROM alembic_version ORDER BY execution_time DESC LIMIT 5;"
```

## Key Features Implemented

### ✅ User Management
- [x] User registration with email verification
- [x] OTP generation and verification (HMAC-SHA256)
- [x] Password hashing and authentication
- [x] JWT token pairs (access + refresh)
- [x] Refresh token rotation
- [x] HTTPOnly secure cookies

### ✅ Virtual Account Provisioning
- [x] Automatic DVA provisioning via Celery (async)
- [x] Payaza integration (account creation, payment links)
- [x] Account-to-user mapping with Redis caching (TTL: 30 min)
- [x] Graceful error handling and retry logic (3 max retries, 60s backoff)

### ✅ Wallet & Transactions
- [x] Wallet creation on user registration
- [x] Balance tracking (Decimal precision)
- [x] Transaction logging (credits, debits, escrows)
- [x] SELECT FOR UPDATE for atomic wallet operations
- [x] Idempotent webhook processing via `payaza_ref`

### ✅ Webhook Processing
- [x] HMAC-SHA512 signature verification
- [x] Virtual account credit handling
- [x] Payment link credit handling
- [x] Asynchronous task queuing via Celery
- [x] Webhook event idempotency
- [x] Error tracking and failure notifications

### ✅ Order Management
- [x] Order creation with order items
- [x] Catalogue browsing
- [x] Vendor management
- [x] Atomic wallet debit with SELECT FOR UPDATE
- [x] Escrow transaction creation

### ✅ Infrastructure
- [x] Alembic database migrations (12 tables)
- [x] Celery task registration and worker
- [x] Redis for OTP storage, caching, and Celery broker
- [x] Rate limiting on auth endpoints
- [x] CORS configuration
- [x] Security headers (X-Frame-Options, CSP, etc.)
- [x] Request validation with Pydantic v2
- [x] Structured logging
- [x] Development OTP logging (environment-aware)

## Demo Workflow

### Scenario: User Registration → DVA Provisioning → Wallet Credit → Order Placement

#### Step 1: Register User
```bash
curl -X POST http://localhost:8000/api/v1/auth/user/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo_'$(date +%s)'@example.com",
    "password": "TestPass123!",
    "full_name": "Demo User",
    "phone": "07087654321"
  }'
```

**Expected Response:**
```json
{
  "message": "User account created. Verify your email.",
  "account_id": "..."
}
```

#### Step 2: Get OTP from Logs
```bash
# In development mode, OTP is logged for testing
docker logs venzap-api 2>&1 | grep "DEV OTP for" | tail -1
```

**Output:** `DEV OTP for demo_...@example.com (purpose=email_verification_user): 123456`

#### Step 3: Verify Email (Triggers DVA Provisioning)
```bash
# First, set up the OTP in Redis
EMAIL="demo_...@example.com"
OTP="123456"
SECRET_KEY="${SECRET_KEY:?Set SECRET_KEY before running the demo}"
HASHED=$(echo -n "$OTP" | openssl dgst -sha256 -hmac "$SECRET_KEY" -hex | cut -d' ' -f2)
docker exec venzap-redis redis-cli SETEX "otp:email_verification_user:$EMAIL" 600 "$HASHED"

# Now verify the email
curl -X POST http://localhost:8000/api/v1/auth/verify-email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "'$EMAIL'",
    "otp": "'$OTP'",
    "account_type": "user"
  }'
```

**Expected Response:**
```json
{
  "message": "Email verified. Wallet account provisioning in progress."
}
```

**Background Process:**
- API marks user as verified
- API attempts synchronous DVA provisioning via Payaza
- If Payaza fails, API queues `provision_virtual_account_task` for async retry
- Celery worker picks up task and retries up to 3 times (60s backoff)

#### Step 4: Login and Check Wallet
```bash
# Login
curl -s -c /tmp/cookies.txt -X POST http://localhost:8000/api/v1/auth/user/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "'$EMAIL'",
    "password": "TestPass123!"
  }'

# Check wallet balance
curl -s -b /tmp/cookies.txt http://localhost:8000/api/v1/wallet/balance
```

**Expected Response:**
```json
{
  "balance": "0.00",
  "currency": "NGN",
  "wallet_id": "..."
}
```

#### Step 5: Simulate Webhook Credit
```bash
# Simulate a Payaza DVA credit webhook
WEBHOOK_REF=$(date +%s)
WEBHOOK='{
  "event": "virtual_account.credit",
  "reference": "'$WEBHOOK_REF'",
  "account_number": "1234567890",
  "amount": 5000,
  "sender": "Test Sender",
  "id": "'$WEBHOOK_REF'"
}'

# In production, this would include X-Payaza-Signature header with HMAC-SHA512 signature
# For demo, the endpoint accepts requests without valid signature (returns 200 "ok")
curl -X POST http://localhost:8000/api/v1/webhooks/payaza \
  -H "Content-Type: application/json" \
  -d "$WEBHOOK"
```

**Background Process:**
- Webhook handler verifies HMAC-SHA512 signature (skipped if invalid)
- Webhook is queued as Celery task `process_payaza_webhook`
- Celery task processes idempotently (checks `webhook_events.payaza_ref`)
- Wallet is credited via `SELECT FOR UPDATE` for atomic operation
- Transaction record is created with `type="credit"`, `source="virtual_account"`

#### Step 6: Verify Wallet Credit
```bash
# Check updated balance
curl -s -b /tmp/cookies.txt http://localhost:8000/api/v1/wallet/balance
```

**Expected Response:**
```json
{
  "balance": "5000.00",
  "currency": "NGN",
  "wallet_id": "..."
}
```

#### Step 7: Browse Vendors and Catalogue
```bash
curl -s -b /tmp/cookies.txt http://localhost:8000/api/v1/vendors | python3 -m json.tool | head -20

curl -s -b /tmp/cookies.txt http://localhost:8000/api/v1/catalogue/items | python3 -m json.tool | head -20
```

#### Step 8: Place Order
```bash
curl -X POST http://localhost:8000/api/v1/orders \
  -b /tmp/cookies.txt \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "catalogue_item_id": "...",
        "quantity": 1
      }
    ]
  }'
```

**Expected Response:**
```json
{
  "id": "...",
  "user_id": "...",
  "status": "pending",
  "total_amount": "...",
  "items": [...]
}
```

## Monitoring

### View Logs
```bash
# API logs
docker logs venzap-api --follow --tail=50

# Celery worker logs
docker logs venzap-celery --follow --tail=50

# Database logs
docker logs venzap-db --follow --tail=50

# Redis logs
docker logs venzap-redis --follow --tail=50
```

### Check Database State
```bash
# Connect to database
docker exec -it venzap-db psql -U venzap -d venzap

# View users
SELECT id, email, is_verified, created_at FROM users ORDER BY created_at DESC LIMIT 5;

# View virtual accounts
SELECT user_id, account_number, account_name, bank_name FROM virtual_accounts LIMIT 5;

# View wallet transactions
SELECT wallet_id, type, amount, reference, status, created_at FROM transactions ORDER BY created_at DESC LIMIT 10;

# View webhook events
SELECT payaza_ref, event_type, processed, processed_at, error FROM webhook_events ORDER BY created_at DESC LIMIT 10;
```

### Check Redis State
```bash
# Connect to Redis
docker exec -it venzap-redis redis-cli

# List all keys
KEYS *

# Get OTP value (example)
GET "otp:email_verification_user:demo@example.com"

# Get user-by-account mapping (example)
GET "dva:user:1234567890"
```

## API Documentation

### Authentication Endpoints

#### Register User
- **Endpoint:** `POST /api/v1/auth/user/register`
- **Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "SecurePass123!",
    "full_name": "John Doe",
    "phone": "08012345678"
  }
  ```
- **Response:** `201 Created` with `account_id`
- **Side Effect:** Sends OTP email (or logs OTP in development)

#### Verify Email
- **Endpoint:** `POST /api/v1/auth/verify-email`
- **Body:**
  ```json
  {
    "email": "user@example.com",
    "otp": "123456",
    "account_type": "user"
  }
  ```
- **Response:** `200 OK`
- **Side Effect:** Triggers DVA provisioning (sync or async via Celery)

#### Login
- **Endpoint:** `POST /api/v1/auth/user/login`
- **Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "SecurePass123!"
  }
  ```
- **Response:** `200 OK` with cookies set
- **Cookies:** `access_token` (httpOnly, 15 min), `refresh_token` (httpOnly, 7 days)

#### Refresh Token
- **Endpoint:** `POST /api/v1/auth/refresh`
- **Cookies:** `refresh_token` (required)
- **Response:** `200 OK` with new token pair

### Wallet Endpoints

#### Get Balance
- **Endpoint:** `GET /api/v1/wallet/balance`
- **Auth:** JWT required
- **Response:**
  ```json
  {
    "balance": "5000.00",
    "currency": "NGN",
    "wallet_id": "..."
  }
  ```

#### Get Transactions
- **Endpoint:** `GET /api/v1/wallet/transactions`
- **Auth:** JWT required
- **Query Params:** `skip`, `limit`, `status`, `type`
- **Response:** List of transactions with pagination

### Virtual Account Endpoints

#### Get Bank Account (DVA)
- **Endpoint:** `GET /api/v1/user/bank-account`
- **Auth:** JWT required
- **Response:**
  ```json
  {
    "account_number": "1234567890",
    "account_name": "John Doe",
    "bank_name": "Demo Bank",
    "bank_code": "DEMO"
  }
  ```

### Order Endpoints

#### Create Order
- **Endpoint:** `POST /api/v1/orders`
- **Auth:** JWT required
- **Body:**
  ```json
  {
    "items": [
      {
        "catalogue_item_id": "...",
        "quantity": 2
      }
    ]
  }
  ```
- **Response:** `201 Created` with order details
- **Side Effect:** Debits wallet (SELECT FOR UPDATE), creates escrow transaction

#### Get Orders
- **Endpoint:** `GET /api/v1/orders`
- **Auth:** JWT required
- **Response:** List of user's orders

### Webhook Endpoints

#### Payaza Webhook
- **Endpoint:** `POST /api/v1/webhooks/payaza`
- **Headers:** `X-Payaza-Signature` (HMAC-SHA512)
- **Body:** Payaza event payload
- **Response:** `200 OK` immediately (async processing)
- **Processing:** Celery task `process_payaza_webhook` handles asynchronously

## Configuration

### Environment Variables (`.env`)

#### Database
- `DATABASE_URL`: PostgreSQL connection string (default: `postgresql+asyncpg://venzap:venzap@db:5432/venzap`)

#### Redis
- `REDIS_URL`: Redis connection string (default: `redis://redis:6379`)

#### Frontend
- `NEXT_PUBLIC_API_BASE_URL`: Public API base URL used by the Vercel frontend

#### Payaza Integration
- `PAYAZA_SECRET_KEY`: API secret key (test: `PZ78-SKTEST-...`)
- `PAYAZA_BASE_URL`: API base URL (default: `https://api.payaza.africa`)
- `PAYAZA_DVA_ENDPOINT`: DVA endpoint (default: `/live/payaza-account/api/v1/dva`)
- `PAYAZA_TIMEOUT_SECONDS`: Request timeout (default: 20)

#### Security
- `SECRET_KEY`: JWT signing key (32+ characters)
- `ALGORITHM`: JWT algorithm (default: `HS256`)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Access token TTL (default: 15)
- `REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token TTL (default: 7)

#### Email
- `SMTP_HOST`: SMTP server (disabled in dev mode)
- `SMTP_PORT`: SMTP port
- `SMTP_USER`: SMTP username
- `SMTP_PASSWORD`: SMTP password

#### Telegram
- `TELEGRAM_BOT_TOKEN`: Bot token from BotFather
- `BACKEND_API_BASE_URL`: Backend URL used by the bot service

#### Environment
- `ENVIRONMENT`: `development` or `production` (affects logging, email behavior)

## Troubleshooting

### Issue: "Received unregistered task" from Celery

**Solution:** The Celery worker wasn't importing the task modules. This has been fixed by:
1. Adding explicit imports in `backend/app/celery_app.py`
2. Rebuilding the Celery image: `docker-compose up -d --build celery`
3. Verifying tasks are registered: `docker logs venzap-celery | grep "\[tasks\]"`

### Issue: OTP verification fails

**Causes:**
1. OTP not set in Redis: Run the OTP setup command from Step 3 of the demo
2. OTP expired (TTL: 10 minutes): Generate a new OTP
3. Wrong email: Ensure email matches registration email (case-insensitive)

**Debug:**
```bash
# Check Redis OTP key
docker exec venzap-redis redis-cli GET "otp:email_verification_user:demo@example.com"
```

### Issue: User registration returns 500 error

**Solution:** This was fixed by correcting the validation error handler in `backend/app/main.py` to properly serialize Pydantic validation errors to JSON.

### Issue: DVA provisioning fails

**Causes:**
1. Payaza API unreachable or invalid credentials
2. Payaza endpoint returns error response
3. Required fields missing in response

**Debug:**
```bash
# Check Celery task attempts
docker logs venzap-celery | grep "provision_virtual_account_task"

# Check webhook events table
docker exec venzap-db psql -U venzap -d venzap \
  -c "SELECT payaza_ref, processed, error FROM webhook_events;"
```

### Issue: Webhook signature verification fails

**Causes:**
1. Invalid HMAC-SHA512 signature in header
2. Webhook secret key mismatch
3. Raw body modified between signing and verification

**Solution:** For demo purposes, the endpoint accepts requests without a valid signature (returns 200 "ok"). In production, ensure the signature header matches:
```
X-Payaza-Signature: HMAC-SHA512(raw_body, PAYAZA_SECRET_KEY)
```

## Development Notes

### Adding New Endpoints

1. Create request/response schemas in `app/schemas/`
2. Implement business logic in `app/services/`
3. Add router handler in `app/routers/`
4. Include router in `app/main.py` via `app.include_router()`

### Adding New Celery Tasks

1. Define task in service file with `@celery_app.task` decorator
2. Import service module in `app/celery_app.py`
3. Queue task via `task_name.delay(args)`
4. Rebuild Celery: `docker-compose up -d --build celery`

### Database Migrations

```bash
# Create new migration
docker exec venzap-api alembic revision --autogenerate -m "description"

# Apply pending migrations
docker exec venzap-api alembic upgrade head

# Revert migrations
docker exec venzap-api alembic downgrade -1
```

## Performance Considerations

- **Wallet Operations:** Use `SELECT FOR UPDATE` for atomic debit/credit
- **Webhook Idempotency:** Store `payaza_ref` and check before processing
- **DVA Caching:** Account numbers cached in Redis (TTL: 30 min) to reduce DB queries
- **Token Rotation:** Refresh tokens stored in Redis, revoked tokens removed on logout
- **Rate Limiting:** Auth endpoints rate-limited (default: 5 requests/minute)

## Security Best Practices Implemented

1. **Password Security:** Bcrypt hashing (cost: 12)
2. **JWT Security:** HS256 signing, exp/iat claims, refresh token rotation
3. **Cookie Security:** HTTPOnly, Secure, SameSite=Lax flags
4. **Webhook Verification:** HMAC-SHA512 signature validation
5. **Input Validation:** Pydantic v2 with strict type checking
6. **SQL Injection Prevention:** Parameterized queries via SQLAlchemy ORM
7. **Rate Limiting:** On auth endpoints (slowapi)
8. **Security Headers:** X-Frame-Options, CSP, X-Content-Type-Options, etc.
9. **Atomic Operations:** SELECT FOR UPDATE for wallet transactions
10. **Idempotency:** Webhook processing via unique reference keys

## Production Deployment Checklist

- [ ] Deploy `frontend/` to Vercel
- [ ] Set `NEXT_PUBLIC_API_BASE_URL` to the Railway API URL in Vercel
- [ ] Deploy the API, Celery worker, and Telegram bot to Railway
- [ ] Point `DATABASE_URL` at Supabase Postgres
- [ ] Point `REDIS_URL` at Railway Redis or Upstash Redis
- [ ] Configure SMTP credentials in Railway
- [ ] Update `SECRET_KEY`, `PAYAZA_SECRET_KEY`, and `TELEGRAM_BOT_TOKEN` with production values
- [ ] Configure `FRONTEND_URL` for the Vercel domain
- [ ] Verify CORS, cookies, and webhook delivery across domains
- [ ] Test the full registration, OTP, DVA, wallet, and order flow end to end

## Support & Debugging

For issues or questions:
1. Check service health: `docker-compose ps`
2. Review relevant logs: `docker logs <service-name>`
3. Check database state: `docker exec venzap-db psql...`
4. Verify Redis state: `docker exec venzap-redis redis-cli...`
5. Check Celery worker status: `docker logs venzap-celery | tail -50`

## License

Proprietary - Venzap
