from __future__ import annotations

import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://venzap:venzap@localhost:5432/venzap",
)


engine = create_async_engine(
    DATABASE_URL,
    future=True,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=0,
)


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all ORM models."""


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session for request-scoped usage."""
    async with AsyncSessionLocal() as session:
        yield session
