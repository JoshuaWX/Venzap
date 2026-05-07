# Production Fixes Applied - May 7, 2026

## Critical Issues Identified & Fixed

### 1. **[FIXED] asyncpg sslmode Parameter Error** ⚠️ ROOT CAUSE
**Error:** `TypeError: connect() got an unexpected keyword argument 'sslmode'`
**Root Cause:** Database URL had `?sslmode=require` which asyncpg doesn't accept as a URL parameter.
**Solution:** 
- Removed `?sslmode=require` from DATABASE_URL in `.env`
- Updated `backend/app/database.py` to detect Supabase URLs and pass `ssl=True` via `connect_args` instead

**Files Modified:**
- `backend/app/database.py`: Added SSL parameter handling for asyncpg
- `.env`: Removed `?sslmode=require` from DATABASE_URL

**Status:** ✅ Ready to deploy

---

### 2. **[FIXED] CORS Headers Missing** ⚠️
**Error:** `Access to fetch...blocked by CORS policy: No 'Access-Control-Allow-Origin'`
**Root Cause:** Frontend URL not configured in Render environment variables
**Solution:**
- Added `FRONTEND_URL=https://venzap.vercel.app,http://localhost:3000` to `.env`
- This is read by `backend/app/config.py` and passed to FastAPI CORSMiddleware

**Files Modified:**
- `.env`: Added FRONTEND_URL environment variable

**Status:** ✅ Ready to deploy

---

### 3. **[FIXED] Multiple Bot Instances Running** ⚠️
**Error:** `telegram.error.Conflict: terminated by other getUpdates request`
**Root Cause:** Bot doesn't gracefully shutdown when Render restarts services
**Solution:**
- Added signal handlers (SIGTERM/SIGINT) in `bot/main.py`
- Added proper shutdown logic to stop polling when receiving shutdown signals

**Files Modified:**
- `bot/main.py`: Added graceful shutdown signal handling

**Status:** ✅ Ready to deploy

---

### 4. **[SEMI-FIXED] Celery Using Memory Broker Instead of Redis** ⚠️
**Status:** In production on Render, Celery falls back to memory:// because Redis isn't configured
**Current Behavior:** 
- Celery uses memory:// broker in production (seen in logs)
- Tasks are processed but lost on restart
- This works for now but is not production-safe

**Solution Applied:**
- Added logging warning when memory broker is used in production
- Updated `backend/app/celery_app.py` to warn loudly about this issue

**What's Needed:** 
- Set up Redis on Render (Render Redis add-on or external service like Upstash)
- Update `REDIS_URL` environment variable on Render with actual Redis instance

**Files Modified:**
- `backend/app/celery_app.py`: Added production warning for memory broker

**Status:** ⚠️ Needs manual Redis setup on Render

---

## Deployment Steps

### Step 1: Push Local Changes to GitHub
```bash
cd c:\dev-folder\Venzap
git add backend/app/database.py backend/app/celery_app.py bot/main.py .env
git commit -m "Fix: asyncpg SSL, CORS headers, bot shutdown, Celery logging"
git push
```

### Step 2: Update Render Environment Variables (Manual via Dashboard)
Go to https://dashboard.render.com and for each service (**venzap-api**, **venzap-worker**, **venzap-bot**):

1. **venzap-api** service:
   - Environment → Add/Update these variables:
     - `DATABASE_URL=postgresql+asyncpg://postgres:N4NB%2CF5%2Fr%3F%2APhLG@db.wcnnhnmaijuudnpgeocw.supabase.co:5432/postgres`
     - `FRONTEND_URL=https://venzap.vercel.app,http://localhost:3000`

2. **venzap-worker** (Celery) service:
   - Environment → Add/Update:
     - `DATABASE_URL=postgresql+asyncpg://postgres:N4NB%2CF5%2Fr%3F%2APhLG@db.wcnnhnmaijuudnpgeocw.supabase.co:5432/postgres`

3. **venzap-bot** service:
   - No changes needed (inherits from git)

### Step 3: Redeploy Services
After pushing code and updating env vars:
- Render will auto-detect the push and redeploy
- Or manually trigger "Manual Deploy" from Render dashboard

### Step 4: Monitor Logs
```bash
# API logs
https://dashboard.render.com → venzap-api → Logs

# Worker logs  
https://dashboard.render.com → venzap-worker → Logs

# Bot logs
https://dashboard.render.com → venzap-bot → Logs
```

---

## Expected Results After Deployment

✅ **Vendor/User signup should work** (no more asyncpg SSL errors)
✅ **Frontend can reach API** (CORS headers fixed)
✅ **Bot won't conflict** (graceful shutdown)
⚠️ **Celery tasks will work but restart-unsafe** (needs Redis for production)

---

## Next Steps (Optional but Recommended)

1. **Set up Redis on Render:**
   - Go to Render Dashboard → venzap-worker service
   - Click "Add Service" → Select "Redis"
   - Use the generated REDIS_URL in environment variables

2. **Test the fixes:**
   ```bash
   # Test signup
   curl -X POST https://venzap-api.onrender.com/api/v1/auth/vendor/register \
     -H "Content-Type: application/json" \
     -d '{"business_name":"Test","email":"test@example.com","phone":"08012345678","password":"Pass123!","address":"Test Addr","delivery_fee":0}'
   
   # Should get success or validation error (not 500)
   ```

---

## Summary of Changes

| File | Change | Impact |
|------|--------|--------|
| `backend/app/database.py` | Add asyncpg SSL via connect_args | Fixes DB connection errors |
| `.env` | Remove sslmode from URL, add FRONTEND_URL | Fixes SSL and CORS |
| `backend/app/celery_app.py` | Add production warning | Alerts on memory broker usage |
| `bot/main.py` | Add signal handlers | Graceful bot shutdown |

