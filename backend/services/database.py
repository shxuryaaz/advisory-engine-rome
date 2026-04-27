from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

import asyncpg

from config import settings


class Database:
    """Small asyncpg wrapper used by services and route handlers."""

    def __init__(self) -> None:
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        if self._pool is None:
            if not settings.database_url:
                raise RuntimeError("DATABASE_URL is required for database operations")
            self._pool = await asyncpg.create_pool(dsn=settings.database_url, min_size=1, max_size=10)

    async def disconnect(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    @asynccontextmanager
    async def acquire(self) -> AsyncIterator[asyncpg.Connection]:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            yield connection

    async def fetch(self, query: str, *args: Any) -> list[asyncpg.Record]:
        async with self.acquire() as connection:
            return await connection.fetch(query, *args)

    async def fetchrow(self, query: str, *args: Any) -> asyncpg.Record | None:
        async with self.acquire() as connection:
            return await connection.fetchrow(query, *args)

    async def execute(self, query: str, *args: Any) -> str:
        async with self.acquire() as connection:
            return await connection.execute(query, *args)


database = Database()
