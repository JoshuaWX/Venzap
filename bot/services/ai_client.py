from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from bot.config import settings


@dataclass(frozen=True)
class AiParseResult:
    is_valid: bool
    data: dict[str, Any] | None
    failure_reason: str | None = None
    raw_output: str | None = None


async def parse_intent(
    message: str,
    telegram_id: int | None,
    current_step: str | None = None,
    selected_vendor_name: str | None = None,
    cart_items: list[dict[str, Any]] | None = None,
) -> AiParseResult:
    if not settings.backend_base_url or not settings.internal_ai_secret:
        return AiParseResult(is_valid=False, data=None, failure_reason="AI_CLIENT_NOT_CONFIGURED")

    payload = {
        "message": message,
        "telegram_id": telegram_id,
        "current_step": current_step,
        "selected_vendor_name": selected_vendor_name,
        "cart_items": cart_items,
    }
    headers = {"X-Internal-Secret": settings.internal_ai_secret}

    timeout = httpx.Timeout(settings.request_timeout_seconds)
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{settings.backend_base_url}/api/v1/ai/parse",
                json=payload,
                headers=headers,
            )
    except httpx.HTTPError as exc:
        return AiParseResult(is_valid=False, data=None, failure_reason=f"AI_HTTP_ERROR:{exc.__class__.__name__}")

    if response.status_code != 200:
        return AiParseResult(is_valid=False, data=None, failure_reason=f"AI_HTTP_{response.status_code}")

    body = response.json()
    return AiParseResult(
        is_valid=bool(body.get("is_valid")),
        data=body.get("data"),
        failure_reason=body.get("failure_reason"),
        raw_output=body.get("raw_output"),
    )
