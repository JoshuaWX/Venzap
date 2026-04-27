from __future__ import annotations

import os
from dataclasses import dataclass


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default)


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str = _env("TELEGRAM_BOT_TOKEN", "")
    backend_base_url: str = _env("BACKEND_API_BASE_URL", "http://localhost:8000")
    internal_ai_secret: str = _env("INTERNAL_AI_SECRET", "")
    redis_url: str = _env("REDIS_URL", "redis://localhost:6379")
    request_timeout_seconds: int = int(_env("BOT_HTTP_TIMEOUT_SECONDS", "10"))


settings = Settings()
