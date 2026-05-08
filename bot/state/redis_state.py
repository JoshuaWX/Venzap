from __future__ import annotations

import json
import logging
import time
import socket
from typing import Any, Optional

import redis.asyncio as redis

from bot.config import settings


logger = logging.getLogger("venzap.bot.redis")


_STATE_TTL_SECONDS = 86400


class _MemoryRedis:
    def __init__(self) -> None:
        self._store: dict[str, tuple[str, float | None]] = {}

    def _purge(self, key: str) -> None:
        record = self._store.get(key)
        if record and record[1] is not None and record[1] <= time.time():
            self._store.pop(key, None)

    async def ping(self) -> bool:
        return True

    async def get(self, key: str) -> str | None:
        self._purge(key)
        record = self._store.get(key)
        return record[0] if record else None

    async def setex(self, key: str, ttl: int, value: Any) -> bool:
        self._store[key] = (str(value), time.time() + max(1, ttl))
        return True

    async def delete(self, key: str) -> int:
        return int(self._store.pop(key, None) is not None)


class _RedisProxy:
    def __init__(self) -> None:
        self._backend: Optional[Any] = None
        self._memory_backend = _MemoryRedis()

    async def _backend_client(self) -> Any:
        if self._backend is not None:
            return self._backend

        redis_url = settings.redis_url
        if not redis_url:
            logger.warning("Redis URL missing; using in-memory store")
            self._backend = self._memory_backend
            return self._memory_backend

        if "://" not in redis_url:
            redis_url = f"redis://{redis_url}"
        if redis_url.startswith("https://"):
            redis_url = "rediss://" + redis_url[len("https://"):]
        elif redis_url.startswith("http://"):
            redis_url = "redis://" + redis_url[len("http://"):]

        try:
            client = redis.from_url(redis_url, decode_responses=True)
        except Exception:
            logger.exception("Invalid Redis URL; using in-memory store")
            self._backend = self._memory_backend
            return self._memory_backend
        try:
            hostname = client.connection_pool.connection_kwargs.get("host")
            if hostname:
                socket.gethostbyname(str(hostname))
            await client.ping()
            self._backend = client
            return client
        except Exception:
            self._backend = self._memory_backend
            return self._memory_backend

    async def get(self, key: str) -> str | None:
        return await (await self._backend_client()).get(key)

    async def setex(self, key: str, ttl: int, value: Any) -> bool:
        return await (await self._backend_client()).setex(key, ttl, value)

    async def delete(self, key: str) -> int:
        return await (await self._backend_client()).delete(key)


_redis_client: Optional[_RedisProxy] = None


def _get_client() -> _RedisProxy:
    global _redis_client
    if _redis_client is None:
        _redis_client = _RedisProxy()
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

