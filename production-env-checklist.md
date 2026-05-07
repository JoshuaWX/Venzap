# Production Environment Checklist

Use this checklist when deploying Venzap to Render + Supabase + Vercel.

## 1) Vercel Frontend

Set these in Vercel Project Settings > Environment Variables:

- `NEXT_PUBLIC_API_BASE_URL` = `https://<your-render-api>.onrender.com`
- `NEXT_PUBLIC_FRONTEND_URL` = `https://<your-vercel-project>.vercel.app`

If you later add Supabase client-side features, also set:

- `NEXT_PUBLIC_SUPABASE_URL` = `https://<your-project-ref>.supabase.co`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` = `<supabase anon key>`

## 2) Render API service

Set these in the Render dashboard for `venzap-api`:

- `DATABASE_URL` = `postgresql+asyncpg://postgres:<password>@db.<project-ref>.supabase.co:5432/postgres`
- `REDIS_URL` = `rediss://default:<password>@<upstash-host>:<port>`
- `SECRET_KEY` = `<32+ char random secret>`
- `ALGORITHM` = `HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES` = `15`
- `REFRESH_TOKEN_EXPIRE_DAYS` = `7`
- `PAYAZA_SECRET_KEY` = `<payaza secret>`
- `PAYAZA_BASE_URL` = `https://api.payaza.africa`
- `PAYAZA_DVA_ENDPOINT` = `/live/payaza-account/api/v1/dva`
- `PAYAZA_PAYMENT_LINK_ENDPOINT` = `<payaza payment link endpoint if used>`
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

## 3) Render worker service for Celery

Set the same backend env vars on `venzap-celery`:

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

## 4) Render worker service for Telegram bot

Set these on `venzap-bot`:

- `TELEGRAM_BOT_TOKEN` = `<telegram bot token>`
- `BACKEND_API_BASE_URL` = `https://<your-render-api>.onrender.com`
- `REDIS_URL` = `rediss://default:<password>@<upstash-host>:<port>`
- `DATABASE_URL` = `postgresql+asyncpg://postgres:<password>@db.<project-ref>.supabase.co:5432/postgres`
- `OPENAI_API_KEY` = `<openai key>`
- `INTERNAL_AI_SECRET` = `<long random secret>`

## 5) Supabase Postgres

Use the Supabase connection string as `DATABASE_URL`.

Copy it from Supabase:

- Project Settings
- Database
- Connection string
- URI

Then run migrations once:

```bash
alembic upgrade head
```

## 6) Upstash Redis

Use the Upstash Redis REST/connection URL as `REDIS_URL`.

Copy it from Upstash:

- Redis Database
- Details
- Connection details

## 7) Security checks before launch

- Rotate any leaked `SECRET_KEY` or `TELEGRAM_BOT_TOKEN`.
- Keep `.env` out of git history.
- Verify Render CORS allows the exact Vercel domain.
- Verify production cookies are secure and cross-site safe.
