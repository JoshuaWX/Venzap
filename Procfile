web: cd backend && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
worker: cd backend && celery -A app.celery_app:celery_app worker --loglevel=INFO
bot: cd bot && python main.py
