from __future__ import annotations

from typing import Any

import httpx

from bot.config import settings


def _normalize_list(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        data = payload.get("data") or payload.get("vendors") or payload.get("items")
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
    return []


async def _get(path: str) -> Any | None:
    if not settings.backend_base_url:
        return None

    timeout = httpx.Timeout(settings.request_timeout_seconds)
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(f"{settings.backend_base_url}{path}")
    except httpx.HTTPError:
        return None

    if response.status_code != 200:
        return None
    return response.json()


async def _get_internal(path: str, params: dict[str, Any] | None = None) -> Any | None:
    if not settings.backend_base_url or not settings.internal_ai_secret:
        return None

    timeout = httpx.Timeout(settings.request_timeout_seconds)
    headers = {"X-Internal-Secret": settings.internal_ai_secret}
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(
                f"{settings.backend_base_url}{path}",
                headers=headers,
                params=params,
            )
    except httpx.HTTPError:
        return None

    if response.status_code != 200:
        return None
    return response.json()


async def get_active_vendors() -> list[dict[str, Any]]:
    payload = await _get("/api/v1/vendors")
    return _normalize_list(payload)


async def get_vendor_catalogue(vendor_id: str) -> list[dict[str, Any]]:
    if not vendor_id:
        return []
    payload = await _get(f"/api/v1/catalogue/vendor/{vendor_id}")
    return _normalize_list(payload)


async def get_order_history(telegram_id: int, page_size: int = 5) -> list[dict[str, Any]]:
    payload = await _get_internal(
        "/api/v1/orders/bot/history",
        params={"telegram_id": telegram_id, "page": 1, "page_size": page_size},
    )
    return _normalize_list(payload)
