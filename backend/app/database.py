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


# asyncpg doesn't accept sslmode as a URL query parameter
# Strip it if present and use connect_args instead
db_url = DATABASE_URL
if "?sslmode=" in db_url:
    db_url = db_url.split("?")[0]

# Use SSL for Supabase (remote connections require SSL)
connect_args = {}
if "supabase" in DATABASE_URL:
    connect_args["ssl"] = True

engine = create_async_engine(
    db_url,
    future=True,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=0,
    connect_args=connect_args if connect_args else None,
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
