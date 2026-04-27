from __future__ import annotations

import os
from dataclasses import dataclass


def _env(name: str, default: str) -> str:
    return os.getenv(name, default)


def _env_list(name: str, default: str) -> list[str]:
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    app_name: str = "Venzap"
    environment: str = _env("ENVIRONMENT", "development")
    frontend_urls: list[str] = _env_list("FRONTEND_URL", "http://localhost:3000")

    secret_key: str = _env("SECRET_KEY", "")
    algorithm: str = _env("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(_env("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    refresh_token_expire_days: int = int(_env("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    otp_ttl_seconds: int = int(_env("OTP_TTL_SECONDS", "600"))

    payaza_secret_key: str = _env("PAYAZA_SECRET_KEY", "")
    payaza_base_url: str = _env("PAYAZA_BASE_URL", "https://api.payaza.africa")
    payaza_dva_endpoint: str = _env("PAYAZA_DVA_ENDPOINT", "/live/payaza-account/api/v1/dva")
    payaza_payment_link_endpoint: str = _env("PAYAZA_PAYMENT_LINK_ENDPOINT", "")
    payaza_timeout_seconds: int = int(_env("PAYAZA_TIMEOUT_SECONDS", "20"))

    rate_limit_general: str = _env("RATE_LIMIT_GENERAL", "60/minute")
    rate_limit_auth: str = _env("RATE_LIMIT_AUTH", "5/minute")
    rate_limit_wallet_fund_link: str = _env("RATE_LIMIT_WALLET_FUND_LINK", "3/minute")
    rate_limit_orders: str = _env("RATE_LIMIT_ORDERS", "10/minute")
    rate_limit_ai_parse: str = _env("RATE_LIMIT_AI_PARSE", "20/minute")

    internal_ai_secret: str = _env("INTERNAL_AI_SECRET", "")

    openai_api_key: str = _env("OPENAI_API_KEY", "")
    openai_model: str = _env("OPENAI_MODEL", "gpt-4o-mini")
    ai_max_response_tokens: int = int(_env("AI_MAX_RESPONSE_TOKENS", "300"))
    ai_max_context_tokens: int = int(_env("AI_MAX_CONTEXT_TOKENS", "2000"))
    ai_confidence_threshold: float = float(_env("AI_CONFIDENCE_THRESHOLD", "0.6"))
    ai_request_timeout_seconds: int = int(_env("AI_REQUEST_TIMEOUT_SECONDS", "5"))
    ai_cache_ttl_seconds: int = int(_env("AI_CACHE_TTL_SECONDS", "60"))
    ai_daily_token_budget: int = int(_env("AI_DAILY_TOKEN_BUDGET", "33333"))

    smtp_host: str = _env("SMTP_HOST", "")
    smtp_port: int = int(_env("SMTP_PORT", "587"))
    smtp_user: str = _env("SMTP_USER", "")
    smtp_password: str = _env("SMTP_PASSWORD", "")
    support_email: str = _env("SUPPORT_EMAIL", "support@venzap.ng")

    @property
    def cookie_secure(self) -> bool:
        return self.environment.lower() != "development"


settings = Settings()
