from __future__ import annotations

import os
import logging
from collections.abc import AsyncGenerator
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger("venzap.db")


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://venzap:venzap@localhost:5432/venzap",
)


# asyncpg doesn't accept sslmode as a URL query parameter.
# Supabase may include sslmode in the query string in different positions.
# Parse and remove sslmode robustly, then rely on connect_args for SSL.
db_url = DATABASE_URL

split = urlsplit(db_url)
query_params = parse_qsl(split.query, keep_blank_values=True)
query_params = [(k, v) for (k, v) in query_params if k.lower() != "sslmode"]

clean_query = urlencode(query_params, doseq=True)
db_url = urlunsplit((split.scheme, split.netloc, split.path, clean_query, split.fragment))

# Use SSL for Supabase (remote connections require SSL)
connect_args: dict = {}
if "supabase" in DATABASE_URL:
    connect_args["ssl"] = True

try:
    logger.info("DB connect target=%s ssl=%s", urlsplit(db_url).hostname, bool(connect_args))
except Exception:
    logger.info("DB connect target unknown ssl=%s", bool(connect_args))

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
