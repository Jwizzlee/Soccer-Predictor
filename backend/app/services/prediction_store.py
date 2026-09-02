"""Persistent SQLite store for user prediction history."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import aiosqlite

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "billing.db"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS prediction_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    clerk_user_id TEXT NOT NULL,
    player_id INTEGER,
    league_id INTEGER,
    player_name TEXT NOT NULL,
    team_name TEXT,
    prop_type TEXT NOT NULL,
    line REAL NOT NULL,
    recommendation TEXT NOT NULL,
    confidence INTEGER NOT NULL,
    hit_rate REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_prediction_history_user_created
    ON prediction_history (clerk_user_id, created_at DESC);
"""

HISTORY_LIMIT = 10


@dataclass(frozen=True)
class PredictionHistoryRow:
    id: int
    clerk_user_id: str
    player_id: int | None
    league_id: int | None
    player_name: str
    team_name: str | None
    prop_type: str
    line: float
    recommendation: str
    confidence: int
    hit_rate: float
    created_at: str


class PredictionStore:
    def __init__(self) -> None:
        self._db: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        if self._db is not None:
            return

        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._db = await aiosqlite.connect(DB_PATH)
        self._db.row_factory = aiosqlite.Row
        await self._db.executescript(SCHEMA_SQL)
        await self._migrate_schema()
        await self._db.commit()

    async def _migrate_schema(self) -> None:
        columns = await self._fetchall("PRAGMA table_info(prediction_history)", ())
        existing = {row["name"] for row in columns}
        migrations = {
            "player_id": "ALTER TABLE prediction_history ADD COLUMN player_id INTEGER",
            "league_id": "ALTER TABLE prediction_history ADD COLUMN league_id INTEGER",
        }
        for column, sql in migrations.items():
            if column not in existing:
                await self._db.execute(sql)

    async def close(self) -> None:
        if self._db is not None:
            await self._db.close()
            self._db = None

    async def insert_prediction(
        self,
        *,
        clerk_user_id: str,
        player_id: int,
        league_id: int | None,
        player_name: str,
        team_name: str | None,
        prop_type: str,
        line: float,
        recommendation: str,
        confidence: int,
        hit_rate: float,
    ) -> None:
        await self._execute(
            """
            INSERT INTO prediction_history (
                clerk_user_id,
                player_id,
                league_id,
                player_name,
                team_name,
                prop_type,
                line,
                recommendation,
                confidence,
                hit_rate
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                clerk_user_id,
                player_id,
                league_id,
                player_name,
                team_name,
                prop_type,
                line,
                recommendation,
                confidence,
                hit_rate,
            ),
        )

    async def list_recent(
        self, clerk_user_id: str, limit: int = HISTORY_LIMIT
    ) -> list[PredictionHistoryRow]:
        rows = await self._fetchall(
            """
            SELECT
                id,
                clerk_user_id,
                player_id,
                league_id,
                player_name,
                team_name,
                prop_type,
                line,
                recommendation,
                confidence,
                hit_rate,
                created_at
            FROM prediction_history
            WHERE clerk_user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (clerk_user_id, limit),
        )
        return [
            PredictionHistoryRow(
                id=int(row["id"]),
                clerk_user_id=str(row["clerk_user_id"]),
                player_id=int(row["player_id"]) if row["player_id"] is not None else None,
                league_id=int(row["league_id"]) if row["league_id"] is not None else None,
                player_name=str(row["player_name"]),
                team_name=str(row["team_name"]) if row["team_name"] else None,
                prop_type=str(row["prop_type"]),
                line=float(row["line"]),
                recommendation=str(row["recommendation"]),
                confidence=int(row["confidence"]),
                hit_rate=float(row["hit_rate"]),
                created_at=str(row["created_at"]),
            )
            for row in rows
        ]

    async def _fetchall(self, query: str, params: tuple) -> list[aiosqlite.Row]:
        db = self._require_db()
        async with db.execute(query, params) as cursor:
            return await cursor.fetchall()

    async def _execute(self, query: str, params: tuple) -> None:
        db = self._require_db()
        await db.execute(query, params)
        await db.commit()

    def _require_db(self) -> aiosqlite.Connection:
        if self._db is None:
            raise RuntimeError("Prediction database is not initialized")
        return self._db


prediction_store = PredictionStore()
