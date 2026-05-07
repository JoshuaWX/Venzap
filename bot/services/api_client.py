from __future__ import annotations

from typing import Any

import logging

import httpx

from bot.config import settings


logger = logging.getLogger("venzap.bot.api")


def _normalize_list(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        data = payload.get("data") or payload.get("vendors") or payload.get("items")
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
    return []


async def _get(path: str, *, cookies: str | None = None) -> Any | None:
    if not settings.backend_base_url:
        logger.error("Backend base URL is not configured")
        return None

    timeout = httpx.Timeout(settings.request_timeout_seconds)
    headers: dict[str, str] = {}
    if cookies:
        headers["Cookie"] = cookies

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(f"{settings.backend_base_url}{path}", headers=headers)
    except httpx.HTTPError:
        logger.exception("GET request failed path=%s", path)
        return None

    if response.status_code != 200:
        logger.warning("GET non-200 path=%s status=%s", path, response.status_code)
        return None
    try:
        return response.json()
    except Exception:  # noqa: BLE001
        logger.warning("GET invalid JSON path=%s status=%s", path, response.status_code)
        return None


async def _post(path: str, payload: dict[str, Any], *, cookies: str | None = None) -> Any | None:
    if not settings.backend_base_url:
        logger.error("Backend base URL is not configured")
        return None

    timeout = httpx.Timeout(settings.request_timeout_seconds)
    headers: dict[str, str] = {}
    if cookies:
        headers["Cookie"] = cookies

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{settings.backend_base_url}{path}",
                json=payload,
                headers=headers,
            )
    except httpx.HTTPError:
        logger.exception("POST request failed path=%s", path)
        return None

    if response.status_code not in {200, 201}:
        logger.warning("POST non-200 path=%s status=%s", path, response.status_code)
        return None

    try:
        return response.json()
    except Exception:  # noqa: BLE001
        logger.warning("POST invalid JSON path=%s status=%s", path, response.status_code)
        return None


async def _post_and_capture_cookies(path: str, payload: dict[str, Any]) -> tuple[Any | None, str | None]:
    if not settings.backend_base_url:
        logger.error("Backend base URL is not configured")
        return None, None

    timeout = httpx.Timeout(settings.request_timeout_seconds)
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(f"{settings.backend_base_url}{path}", json=payload)
    except httpx.HTTPError:
        logger.exception("POST request failed path=%s", path)
        return None, None

    if response.status_code not in {200, 201}:
        logger.warning("POST non-200 path=%s status=%s", path, response.status_code)
        return None, None

    set_cookies = response.headers.get_list("set-cookie")

    access = None
    refresh = None
    for sc in set_cookies:
        lower = sc.lower()
        if "access" in lower and "=" in sc:
            access = sc.split(";", 1)[0].strip()
        if "refresh" in lower and "=" in sc:
            refresh = sc.split(";", 1)[0].strip()

    cookie_header = None
    if access and refresh:
        cookie_header = f"{access}; {refresh}"
    else:
        cookie_header = access or refresh

    try:
        return response.json(), cookie_header
    except Exception:  # noqa: BLE001
        logger.warning("POST invalid JSON path=%s status=%s", path, response.status_code)
        return None, cookie_header


# -------- Public helpers used by the bot --------

async def get_active_vendors() -> list[dict[str, Any]]:
    payload = await _get("/api/v1/vendors/")
    if not payload:
        return []
    return _normalize_list(payload)


async def get_vendor_catalogue(vendor_id: str) -> list[dict[str, Any]]:
    payload = await _get(f"/api/v1/vendors/{vendor_id}")
    if not payload:
        return []
    # backend response uses {vendor, catalogue}
    items = payload.get("catalogue")
    return _normalize_list(items)  # type: ignore[arg-type]


async def get_user_bank_account(*, cookies: str) -> dict[str, Any] | None:
    return await _get("/api/v1/user/bank-account", cookies=cookies)


async def get_order_history(telegram_user_id: int) -> list[dict[str, Any]]:
    # internal endpoint guarded by require_internal_secret via bot config
    # bot passes as Query param telegram_id; api_client uses internal secret via headers.
    payload = await _get(f"/api/v1/orders/bot/history?telegram_id={telegram_user_id}")
    if not payload:
        return []
    return _normalize_list(payload.get("data") if isinstance(payload, dict) else payload)  # type: ignore[arg-type]


async def place_order(*, cookies: str, vendor_id: str, delivery_address: str, note: str | None, items: list[dict[str, Any]]) -> dict[str, Any] | None:
    payload: dict[str, Any] = {
        "vendor_id": vendor_id,
        "delivery_address": delivery_address,
        "items": items,
    }
    if note:
        payload["note"] = note

    return await _post("/api/v1/orders/", payload, cookies=cookies)


async def login_user(*, email: str, password: str) -> tuple[dict[str, Any] | None, str | None]:
    body = {"email": email, "password": password}
    return await _post_and_capture_cookies("/api/v1/auth/user/login", body)


async def get_awaiting_otp_register(*, email: str, password: str, full_name: str, phone: str) -> tuple[dict[str, Any] | None, str | None]:
    # used to start OTP verification in chat
    body = {"email": email, "password": password, "full_name": full_name, "phone": phone}
    return await _post_and_capture_cookies("/api/v1/auth/user/register", body)


async def verify_user_email(*, email: str, otp: str, account_type: str = "user") -> dict[str, Any] | None:
    payload = {"email": email, "otp": otp, "account_type": account_type}
    return await _post("/api/v1/auth/verify-email", payload)

