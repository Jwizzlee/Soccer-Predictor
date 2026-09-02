"""Persistent SQLite billing store for Clerk ↔ Stripe mappings."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import aiosqlite

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "billing.db"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS billing_subscriptions (
    clerk_user_id TEXT PRIMARY KEY,
    stripe_customer_id TEXT UNIQUE,
    subscription_status TEXT NOT NULL DEFAULT 'inactive',
    is_active INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


@dataclass(frozen=True)
class CachedSubscription:
    active: bool
    status: str


class BillingStore:
    def __init__(self) -> None:
        self._db: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        if self._db is not None:
            return

        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._db = await aiosqlite.connect(DB_PATH)
        self._db.row_factory = aiosqlite.Row
        await self._db.executescript(SCHEMA_SQL)
        await self._db.commit()

    async def close(self) -> None:
        if self._db is not None:
            await self._db.close()
            self._db = None

    async def get_customer_id(self, clerk_user_id: str) -> str | None:
        row = await self._fetchone(
            "SELECT stripe_customer_id FROM billing_subscriptions WHERE clerk_user_id = ?",
            (clerk_user_id,),
        )
        if row is None:
            return None
        customer_id = row["stripe_customer_id"]
        return str(customer_id) if customer_id else None

    async def get_clerk_user_id(self, stripe_customer_id: str) -> str | None:
        row = await self._fetchone(
            "SELECT clerk_user_id FROM billing_subscriptions WHERE stripe_customer_id = ?",
            (stripe_customer_id,),
        )
        if row is None:
            return None
        return str(row["clerk_user_id"])

    async def get_subscription(self, clerk_user_id: str) -> CachedSubscription | None:
        row = await self._fetchone(
            """
            SELECT subscription_status, is_active
            FROM billing_subscriptions
            WHERE clerk_user_id = ?
            """,
            (clerk_user_id,),
        )
        if row is None:
            return None
        return CachedSubscription(
            active=bool(row["is_active"]),
            status=str(row["subscription_status"]),
        )

    async def set_customer_mapping(
        self, clerk_user_id: str, stripe_customer_id: str
    ) -> None:
        await self._execute(
            """
            INSERT INTO billing_subscriptions (
                clerk_user_id,
                stripe_customer_id,
                subscription_status,
                is_active
            )
            VALUES (?, ?, 'inactive', 0)
            ON CONFLICT(clerk_user_id) DO UPDATE SET
                stripe_customer_id = excluded.stripe_customer_id,
                updated_at = CURRENT_TIMESTAMP
            """,
            (clerk_user_id, stripe_customer_id),
        )

    async def set_subscription(
        self, clerk_user_id: str, active: bool, status: str
    ) -> None:
        await self._execute(
            """
            INSERT INTO billing_subscriptions (
                clerk_user_id,
                stripe_customer_id,
                subscription_status,
                is_active
            )
            VALUES (?, NULL, ?, ?)
            ON CONFLICT(clerk_user_id) DO UPDATE SET
                subscription_status = excluded.subscription_status,
                is_active = excluded.is_active,
                updated_at = CURRENT_TIMESTAMP
            """,
            (clerk_user_id, status, int(active)),
        )

    async def _fetchone(self, query: str, params: tuple) -> aiosqlite.Row | None:
        db = self._require_db()
        async with db.execute(query, params) as cursor:
            return await cursor.fetchone()

    async def _execute(self, query: str, params: tuple) -> None:
        db = self._require_db()
        await db.execute(query, params)
        await db.commit()

    def _require_db(self) -> aiosqlite.Connection:
        if self._db is None:
            raise RuntimeError("Billing database is not initialized")
        return self._db


billing_store = BillingStore()
