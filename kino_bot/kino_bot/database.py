"""Asynchronous SQLite storage for users and movie records."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import aiosqlite

from config import DATABASE_PATH


class Database:
    """Provides asynchronous operations for the Kino bot's SQLite database.

    Movie codes are normalized with ``casefold`` before storage and lookup, so
    a code can be retrieved regardless of the capitalization used by a user.
    """

    def __init__(self, db_path: str | Path = DATABASE_PATH) -> None:
        self.db_path = Path(db_path)

    async def init_db(self) -> None:
        """Create the database file, tables, and indexes if they do not exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        async with aiosqlite.connect(self.db_path, timeout=30) as connection:
            await connection.execute("PRAGMA journal_mode = WAL")
            await connection.execute("PRAGMA foreign_keys = ON")
            await connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    join_date TEXT NOT NULL
                )
                """
            )
            await connection.execute(
                """
                CREATE TABLE IF NOT EXISTS movies (
                    code TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    file_id_or_link TEXT NOT NULL
                )
                """
            )
            await connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_users_join_date ON users (join_date)"
            )
            await connection.commit()

    async def add_user(self, user_id: int, join_date: str | None = None) -> bool:
        """Add a user if missing; return True only when a new row was inserted."""
        if user_id <= 0:
            raise ValueError("user_id must be a positive Telegram user ID.")

        registered_at = join_date or datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        )
        async with aiosqlite.connect(self.db_path, timeout=30) as connection:
            cursor = await connection.execute(
                """
                INSERT OR IGNORE INTO users (user_id, join_date)
                VALUES (?, ?)
                """,
                (user_id, registered_at),
            )
            await connection.commit()
            return cursor.rowcount == 1

    async def user_exists(self, user_id: int) -> bool:
        """Return whether a user ID has already been registered."""
        async with aiosqlite.connect(self.db_path, timeout=30) as connection:
            cursor = await connection.execute(
                "SELECT 1 FROM users WHERE user_id = ? LIMIT 1",
                (user_id,),
            )
            return await cursor.fetchone() is not None

    async def get_user_count(self) -> int:
        """Return the total number of registered users."""
        async with aiosqlite.connect(self.db_path, timeout=30) as connection:
            cursor = await connection.execute("SELECT COUNT(*) FROM users")
            row = await cursor.fetchone()
            return int(row[0]) if row is not None else 0

    async def get_all_users(self) -> list[int]:
        """Return all registered Telegram user IDs in ascending order."""
        async with aiosqlite.connect(self.db_path, timeout=30) as connection:
            cursor = await connection.execute(
                "SELECT user_id FROM users ORDER BY user_id"
            )
            rows = await cursor.fetchall()
            return [int(row[0]) for row in rows]

    async def add_movie(
        self,
        code: str,
        title: str,
        file_id_or_link: str,
    ) -> None:
        """Insert a movie or update the existing movie with the same code."""
        normalized_code = code.strip().casefold()
        clean_title = title.strip()
        media = file_id_or_link.strip()

        if not normalized_code:
            raise ValueError("Movie code cannot be empty.")
        if not clean_title:
            raise ValueError("Movie title cannot be empty.")
        if not media:
            raise ValueError("Movie file ID or link cannot be empty.")

        async with aiosqlite.connect(self.db_path, timeout=30) as connection:
            await connection.execute(
                """
                INSERT INTO movies (code, title, file_id_or_link)
                VALUES (?, ?, ?)
                ON CONFLICT(code) DO UPDATE SET
                    title = excluded.title,
                    file_id_or_link = excluded.file_id_or_link
                """,
                (normalized_code, clean_title, media),
            )
            await connection.commit()

    async def get_movie(self, code: str) -> dict[str, str] | None:
        """Return a movie as a dictionary, or None when its code is unknown."""
        normalized_code = code.strip().casefold()
        if not normalized_code:
            return None

        async with aiosqlite.connect(self.db_path, timeout=30) as connection:
            connection.row_factory = aiosqlite.Row
            cursor = await connection.execute(
                """
                SELECT code, title, file_id_or_link
                FROM movies
                WHERE code = ?
                LIMIT 1
                """,
                (normalized_code,),
            )
            row = await cursor.fetchone()
            if row is None:
                return None
            return {
                "code": str(row["code"]),
                "title": str(row["title"]),
                "file_id_or_link": str(row["file_id_or_link"]),
            }

    async def movie_exists(self, code: str) -> bool:
        """Return whether a movie code exists, ignoring its capitalization."""
        normalized_code = code.strip().casefold()
        if not normalized_code:
            return False

        async with aiosqlite.connect(self.db_path, timeout=30) as connection:
            cursor = await connection.execute(
                "SELECT 1 FROM movies WHERE code = ? LIMIT 1",
                (normalized_code,),
            )
            return await cursor.fetchone() is not None

    async def delete_movie(self, code: str) -> bool:
        """Delete the movie matching a code; return True if a row was removed."""
        normalized_code = code.strip().casefold()
        if not normalized_code:
            return False

        async with aiosqlite.connect(self.db_path, timeout=30) as connection:
            cursor = await connection.execute(
                "DELETE FROM movies WHERE code = ?",
                (normalized_code,),
            )
            await connection.commit()
            return cursor.rowcount == 1

    async def get_movie_count(self) -> int:
        """Return the total number of movies in the database."""
        async with aiosqlite.connect(self.db_path, timeout=30) as connection:
            cursor = await connection.execute("SELECT COUNT(*) FROM movies")
            row: Any = await cursor.fetchone()
            return int(row[0]) if row is not None else 0