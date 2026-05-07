from __future__ import annotations

import os
import time
import socket
from dataclasses import dataclass
from typing import Any, Optional

import redis.asyncio as redis

from app.config import settings


@dataclass
class _RedisRecord:
    value: str
    expires_at: float | None = None


class _MemoryRedis:
    def __init__(self) -> None:
        self._store: dict[str, _RedisRecord] = {}

    def _purge(self, key: str) -> None:
        record = self._store.get(key)
        if record and record.expires_at is not None and record.expires_at <= time.time():
            self._store.pop(key, None)

    async def ping(self) -> bool:
        return True

    async def get(self, key: str) -> str | None:
        self._purge(key)
        record = self._store.get(key)
        return record.value if record else None

    async def set(self, key: str, value: Any) -> bool:
        self._store[key] = _RedisRecord(str(value))
        return True

    async def setex(self, key: str, ttl: int, value: Any) -> bool:
        self._store[key] = _RedisRecord(str(value), time.time() + max(1, ttl))
        return True

    async def delete(self, key: str) -> int:
        return int(self._store.pop(key, None) is not None)

    async def incrby(self, key: str, amount: int) -> int:
        current = await self.get(key)
        new_value = int(current or 0) + amount
        record = self._store.get(key)
        expires_at = record.expires_at if record else None
        self._store[key] = _RedisRecord(str(new_value), expires_at)
        return new_value

    async def expire(self, key: str, seconds: int) -> bool:
        self._purge(key)
        record = self._store.get(key)
        if not record:
            return False
        self._store[key] = _RedisRecord(record.value, time.time() + max(1, seconds))
        return True

    async def ttl(self, key: str) -> int:
        self._purge(key)
        record = self._store.get(key)
        if not record:
            return -2
        if record.expires_at is None:
            return -1
        return max(0, int(record.expires_at - time.time()))


class _RedisProxy:
    def __init__(self) -> None:
        self._backend: Any | None = None
        self._memory_backend = _MemoryRedis()

    def _make_real_client(self) -> redis.Redis:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        return redis.from_url(redis_url, decode_responses=True)

    async def _backend_client(self) -> Any:
        if self._backend is not None:
            return self._backend

        client = self._make_real_client()
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

    async def set(self, key: str, value: Any) -> bool:
        return await (await self._backend_client()).set(key, value)

    async def setex(self, key: str, ttl: int, value: Any) -> bool:
        return await (await self._backend_client()).setex(key, ttl, value)

    async def delete(self, key: str) -> int:
        return await (await self._backend_client()).delete(key)

    async def incrby(self, key: str, amount: int) -> int:
        return await (await self._backend_client()).incrby(key, amount)

    async def expire(self, key: str, seconds: int) -> bool:
        return await (await self._backend_client()).expire(key, seconds)

    async def ttl(self, key: str) -> int:
        return await (await self._backend_client()).ttl(key)


_redis_client: Optional[_RedisProxy] = None


def get_redis_client() -> _RedisProxy:
    global _redis_client
    if _redis_client is None:
        _redis_client = _RedisProxy()
    return _redis_client
