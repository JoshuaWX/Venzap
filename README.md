# Venzap

Venzap is a chat-first commerce platform for Telegram users and vendor web dashboards.

For the full product and demo workflow, see [README_DEMO.md](README_DEMO.md).

## Production Deployment: Render + Supabase + Vercel

Use this stack for production:

- Frontend: Vercel
- API: Render Web Service
- Celery: Render Background Worker
- Telegram bot: Render Background Worker
- Database: Supabase Postgres
- Redis: Upstash Redis or Render Redis

### Exact values to set

#### Vercel

- `NEXT_PUBLIC_API_BASE_URL` = `https://<your-render-api>.onrender.com`
- `NEXT_PUBLIC_FRONTEND_URL` = `https://<your-vercel-project>.vercel.app`

#### Render API service

- `DATABASE_URL` = `postgresql+asyncpg://postgres:<password>@db.<project-ref>.supabase.co:5432/postgres`
- `REDIS_URL` = `rediss://default:<password>@<upstash-host>:<port>`
- `SECRET_KEY` = `<32+ char random secret>`
- `ALGORITHM` = `HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES` = `15`
- `REFRESH_TOKEN_EXPIRE_DAYS` = `7`
- `PAYAZA_SECRET_KEY` = `<payaza secret>`
- `PAYAZA_BASE_URL` = `https://api.payaza.africa`
- `PAYAZA_DVA_ENDPOINT` = `/live/payaza-account/api/v1/dva`
- `SMTP_HOST` = `<smtp host>`
- `SMTP_PORT` = `587`
- `SMTP_USER` = `<smtp username>`
- `SMTP_PASSWORD` = `<smtp password or app password>`
- `SUPPORT_EMAIL` = `support@venzap.ng`
- `FRONTEND_URL` = `https://<your-vercel-project>.vercel.app`
- `ENVIRONMENT` = `production`
- `OPENAI_API_KEY` = `<openai key>`
- `OPENAI_MODEL` = `gpt-4o-mini`
- `AI_MAX_RESPONSE_TOKENS` = `300`
- `AI_MAX_CONTEXT_TOKENS` = `2000`
- `AI_CONFIDENCE_THRESHOLD` = `0.6`
- `AI_REQUEST_TIMEOUT_SECONDS` = `5`
- `AI_CACHE_TTL_SECONDS` = `60`
- `AI_DAILY_TOKEN_BUDGET` = `33333`
- `INTERNAL_AI_SECRET` = `<long random secret>`
- `TELEGRAM_BOT_TOKEN` = `<telegram bot token>`

#### Render Celery worker

Set the same backend env vars as the API service, especially:

- `DATABASE_URL`
- `REDIS_URL`
- `SECRET_KEY`
- `PAYAZA_SECRET_KEY`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASSWORD`
- `OPENAI_API_KEY`
- `INTERNAL_AI_SECRET`

#### Render Telegram bot worker

- `TELEGRAM_BOT_TOKEN` = `<telegram bot token>`
- `BACKEND_API_BASE_URL` = `https://<your-render-api>.onrender.com`
- `REDIS_URL` = `rediss://default:<password>@<upstash-host>:<port>`
- `DATABASE_URL` = `postgresql+asyncpg://postgres:<password>@db.<project-ref>.supabase.co:5432/postgres`
- `OPENAI_API_KEY` = `<openai key>`
- `INTERNAL_AI_SECRET` = `<long random secret>`

### Render service commands

Use these commands if you deploy without the blueprint:

```bash
# API
cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT

# Celery
cd backend && celery -A app.celery_app:celery_app worker --loglevel=INFO

# Bot
cd bot && python main.py
```

### Migrations

After the API and database are connected, run:

```bash
alembic upgrade head
```
