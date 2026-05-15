"""Shared pytest fixtures.

We use an in-memory SQLite DB for unit tests of services. Phase 1 schema
doesn't use Postgres-specific types, so this is safe. When we add things
like `text[]` columns (Phase 3 exercises), we'll switch to testcontainers
or split into integration tests.
"""

from __future__ import annotations

import os

# Settings reads these from env at import time. Stub them so any accidental
# import of `repcal.config` in tests doesn't crash.
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("DISCORD_BOT_TOKEN", "test-token")

from collections.abc import AsyncIterator

import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from repcal.models import metadata


@pytest_asyncio.fixture
async def session() -> AsyncIterator[AsyncSession]:
    """Fresh in-memory SQLite with Phase 1 schema."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with factory() as s:
        yield s

    await engine.dispose()
