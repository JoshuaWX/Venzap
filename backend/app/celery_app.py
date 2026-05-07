from __future__ import annotations

import logging
import os
import socket
from urllib.parse import urlparse

from celery import Celery

from app.config import settings


logger = logging.getLogger("venzap.celery")

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
if redis_url.startswith("https://"):
    # Upstash REST URL provided; convert to TLS Redis scheme for Celery.
    redis_url = "rediss://" + redis_url[len("https://"):]
elif redis_url.startswith("http://"):
    redis_url = "redis://" + redis_url[len("http://"):]


def _uses_placeholder_redis(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except Exception:
        return True

    return parsed.hostname in {"localhost", "127.0.0.1", "redis", "db"} or not parsed.hostname


def _can_resolve_redis_host(url: str) -> bool:
    parsed = urlparse(url)
    if not parsed.hostname:
        return False
    try:
        socket.gethostbyname(parsed.hostname)
    except OSError:
        return False
    return True


# In production, warn if Redis is not available (but don't silently use memory backend)
use_memory_fallback = (
    not _can_resolve_redis_host(redis_url) or 
    (_uses_placeholder_redis(redis_url) and settings.environment.lower() == "production")
)

if use_memory_fallback and settings.environment.lower() == "production":
    logger.warning(
        f"Redis not available in production! Using memory backend (NOT FOR PRODUCTION). "
        f"REDIS_URL: {redis_url}. Please set up a Redis service."
    )

broker_url = "memory://" if use_memory_fallback else redis_url
result_backend = "cache+memory://" if use_memory_fallback else redis_url

celery_app = Celery("venzap", broker=broker_url, backend=result_backend)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_always_eager=use_memory_fallback,
    task_eager_propagates=use_memory_fallback,
    broker_connection_retry_on_startup=False,
)

# Task auto-discovery
celery_app.autodiscover_tasks(["app"])

# Auto-discover tasks from app.services module
celery_app.autodiscover_tasks(["app.services"])

# Explicitly import task modules to ensure they are registered
try:
    from app.services import virtual_account_service  # noqa: F401
except ImportError:
    pass

try:
    from app.services import webhook_service  # noqa: F401
except ImportError:
    pass
