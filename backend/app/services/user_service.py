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


def _ensure_saved_searches_table(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS saved_searches (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                problem_text TEXT NULL,
                phase_iri TEXT NULL,
                cluster_iris TEXT[] NULL,
                paradigm_iri TEXT NULL,
                max_results INTEGER NULL,
                task_iri TEXT NULL,
                conditions TEXT[] NULL,
                performance_prefs TEXT[] NULL,
                dataset_type_iri TEXT NULL
            )
            """
        )
    conn.commit()


def _user_exists(conn: psycopg.Connection, user_id: int) -> bool:
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM users WHERE id = %s", (user_id,))
        return cur.fetchone() is not None


def _ensure_user_and_saved_search_schema(conn: psycopg.Connection, user_id: int) -> None:
    _ensure_users_table(conn)
    _ensure_saved_searches_table(conn)
    if not _user_exists(conn, user_id):
        raise ValueError("User not found")


def save_search(user_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    with get_postgres_connection() as conn:
        _ensure_user_and_saved_search_schema(conn, user_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO saved_searches (
                    user_id,
                    problem_text,
                    phase_iri,
                    cluster_iris,
                    paradigm_iri,
                    max_results,
                    task_iri,
                    conditions,
                    performance_prefs,
                    dataset_type_iri
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING
                    id,
                    user_id,
                    created_at,
                    problem_text,
                    phase_iri,
                    cluster_iris,
                    paradigm_iri,
                    max_results,
                    task_iri,
                    conditions,
                    performance_prefs,
                    dataset_type_iri
                """,
                (
                    user_id,
                    payload.get("problem_text"),
                    payload.get("phase_iri"),
                    payload.get("cluster_iris"),
                    payload.get("paradigm_iri"),
                    payload.get("max_results"),
                    payload.get("task_iri"),
                    payload.get("conditions"),
                    payload.get("performance_prefs"),
                    payload.get("dataset_type_iri"),
                ),
            )
            row = cur.fetchone()
        conn.commit()

    if not isinstance(row, dict):
        raise RuntimeError("Failed to save search")
    return row


def list_saved_searches(user_id: int, limit: int = 20) -> list[dict[str, Any]]:
    with get_postgres_connection() as conn:
        _ensure_user_and_saved_search_schema(conn, user_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    user_id,
                    created_at,
                    problem_text,
                    phase_iri,
                    cluster_iris,
                    paradigm_iri,
                    max_results,
                    task_iri,
                    conditions,
                    performance_prefs,
                    dataset_type_iri
                FROM saved_searches
                WHERE user_id = %s
                ORDER BY created_at DESC, id DESC
                LIMIT %s
                """,
                (user_id, limit),
            )
            rows = cur.fetchall() or []

    return [row for row in rows if isinstance(row, dict)]
