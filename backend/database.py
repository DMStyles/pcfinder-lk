"""
SQLite-backed cache layer for PCFinder LK search results.
Uses aiosqlite for async I/O.  TTL is 1 hour by default.
"""

from __future__ import annotations

import json
import os
import time
from typing import Optional

import aiosqlite

DB_PATH = os.environ.get("DB_PATH", "pcfinder_cache.db")
CACHE_TTL_SECONDS = int(os.environ.get("CACHE_TTL_HOURS", "1")) * 3600


async def init_db() -> None:
    """Create the cache table if it does not already exist."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS search_cache (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                query_hash  TEXT    NOT NULL UNIQUE,
                results_json TEXT   NOT NULL,
                created_at  REAL    NOT NULL
            )
            """
        )
        await db.commit()


async def get_cached(query_hash: str) -> Optional[str]:
    """
    Return the cached JSON string for *query_hash* if it exists and is
    still within the TTL window.  Returns ``None`` on a miss or expiry.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT results_json, created_at FROM search_cache WHERE query_hash = ?",
            (query_hash,),
        ) as cursor:
            row = await cursor.fetchone()

    if row is None:
        return None

    results_json, created_at = row
    if time.time() - created_at > CACHE_TTL_SECONDS:
        # Expired — treat as a miss (stale row will be overwritten on next set)
        return None

    return results_json


async def set_cache(query_hash: str, results_json: str) -> None:
    """Upsert the JSON payload for *query_hash* with the current timestamp."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO search_cache (query_hash, results_json, created_at)
            VALUES (?, ?, ?)
            ON CONFLICT(query_hash) DO UPDATE SET
                results_json = excluded.results_json,
                created_at   = excluded.created_at
            """,
            (query_hash, results_json, time.time()),
        )
        await db.commit()
