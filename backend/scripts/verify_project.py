#!/usr/bin/env python3
"""Verify Sports Predictor backend health: imports and SQLite schema."""

from __future__ import annotations

import asyncio
import sqlite3
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = BACKEND_ROOT / "app" / "data" / "billing.db"
REQUIRED_TABLES = ("billing_subscriptions", "prediction_history")

sys.path.insert(0, str(BACKEND_ROOT))


def verify_imports() -> None:
    from app.main import app  # noqa: F401

    print("PASS: FastAPI app imports cleanly")


async def ensure_schema() -> None:
    from app.services.billing_store import billing_store
    from app.services.prediction_store import prediction_store

    await billing_store.connect()
    await prediction_store.connect()
    await billing_store.close()
    await prediction_store.close()
    print("PASS: SQLite stores connect and initialize schema")


def verify_tables() -> None:
    if not DB_PATH.exists():
        raise RuntimeError(f"Database not found at {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    try:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        missing = [name for name in REQUIRED_TABLES if name not in tables]
        if missing:
            raise RuntimeError(f"Missing tables: {', '.join(missing)}")

        for name in REQUIRED_TABLES:
            print(f"PASS: Table '{name}' exists")
    finally:
        conn.close()


async def main() -> int:
    print("Sports Predictor — backend verification")
    print("=" * 40)
    try:
        verify_imports()
        await ensure_schema()
        verify_tables()
    except Exception as exc:
        print(f"FAIL: {exc}")
        return 1

    print("=" * 40)
    print("All backend checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
