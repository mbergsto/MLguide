from __future__ import annotations

from typing import Any

import psycopg

from app.postgres import get_postgres_connection


def _ensure_users_table(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(64) UNIQUE NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
    conn.commit()


def login_or_create_user(username: str) -> dict[str, Any]:
    with get_postgres_connection() as conn:
        _ensure_users_table(conn)
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (username)
                VALUES (%s)
                ON CONFLICT (username)
                DO UPDATE SET username = EXCLUDED.username
                RETURNING id, username, created_at
                """,
                (username,),
            )
            row = cur.fetchone()
        conn.commit()

    if not isinstance(row, dict):
        raise RuntimeError("Failed to load user")

    return row

