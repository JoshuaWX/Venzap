from __future__ import annotations

import json
from typing import Any, Optional

import redis.asyncio as redis

from bot.config import settings


_STATE_TTL_SECONDS = 86400
_redis_client: Optional[redis.Redis] = None


def _get_client() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis_client


def _key(user_id: int, name: str) -> str:
    return f"bot:{user_id}:{name}"


async def get_state(user_id: int) -> str | None:
    redis_client = _get_client()
    return await redis_client.get(_key(user_id, "state"))


async def set_state(user_id: int, state: str) -> None:
    redis_client = _get_client()
    await redis_client.setex(_key(user_id, "state"), _STATE_TTL_SECONDS, state)


async def clear_state(user_id: int) -> None:
    redis_client = _get_client()
    await redis_client.delete(_key(user_id, "state"))


async def get_selected_vendor(user_id: int) -> str | None:
    redis_client = _get_client()
    return await redis_client.get(_key(user_id, "selected_vendor"))


async def set_selected_vendor(user_id: int, vendor_name: str) -> None:
    redis_client = _get_client()
    await redis_client.setex(_key(user_id, "selected_vendor"), _STATE_TTL_SECONDS, vendor_name)


async def clear_selected_vendor(user_id: int) -> None:
    redis_client = _get_client()
    await redis_client.delete(_key(user_id, "selected_vendor"))


async def get_delivery_address(user_id: int) -> str | None:
    redis_client = _get_client()
    return await redis_client.get(_key(user_id, "delivery_address"))


async def set_delivery_address(user_id: int, address: str) -> None:
    redis_client = _get_client()
    await redis_client.setex(_key(user_id, "delivery_address"), _STATE_TTL_SECONDS, address)


async def clear_delivery_address(user_id: int) -> None:
    redis_client = _get_client()
    await redis_client.delete(_key(user_id, "delivery_address"))


async def get_cart(user_id: int) -> list[dict[str, Any]]:
    redis_client = _get_client()
    raw = await redis_client.get(_key(user_id, "cart"))
    if not raw:
        return []
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return [item for item in payload if isinstance(item, dict)]


async def set_cart(user_id: int, items: list[dict[str, Any]]) -> None:
    redis_client = _get_client()
    await redis_client.setex(_key(user_id, "cart"), _STATE_TTL_SECONDS, json.dumps(items))


async def clear_cart(user_id: int) -> None:
    redis_client = _get_client()
    await redis_client.delete(_key(user_id, "cart"))


def _map_key(user_id: int, vendor_id: str, name: str) -> str:
    return f"bot:{user_id}:catalogue_map:{vendor_id}:{name}"


async def set_catalogue_item_id(user_id: int, vendor_id: str, item_name: str, catalogue_item_id: str) -> None:
    redis_client = _get_client()
    await redis_client.setex(_map_key(user_id, vendor_id, item_name), _STATE_TTL_SECONDS, catalogue_item_id)


async def get_catalogue_item_id(user_id: int, vendor_id: str, item_name: str) -> str | None:
    redis_client = _get_client()
    return await redis_client.get(_map_key(user_id, vendor_id, item_name))


async def set_auth_cookies(user_id: int, cookie_header: str) -> None:
    redis_client = _get_client()
    await redis_client.setex(_key(user_id, "auth_cookies"), _STATE_TTL_SECONDS, cookie_header)


async def get_auth_cookies(user_id: int) -> str | None:
    redis_client = _get_client()
    return await redis_client.get(_key(user_id, "auth_cookies"))


async def clear_auth_cookies(user_id: int) -> None:
    redis_client = _get_client()
    await redis_client.delete(_key(user_id, "auth_cookies"))


async def set_registration_field(user_id: int, field: str, value: str) -> None:
    redis_client = _get_client()
    await redis_client.setex(_key(user_id, f"reg:{field}"), _STATE_TTL_SECONDS, value)


async def get_registration_field(user_id: int, field: str) -> str | None:
    redis_client = _get_client()
    return await redis_client.get(_key(user_id, f"reg:{field}"))


async def clear_registration(user_id: int) -> None:
    redis_client = _get_client()
    keys = [
        _key(user_id, "reg:full_name"),
        _key(user_id, "reg:email"),
        _key(user_id, "reg:phone"),
        _key(user_id, "reg:password"),
    ]
    for k in keys:
        await redis_client.delete(k)

