import asyncio
import logging
import time
from pathlib import Path

import aiosqlite

from .config import cfg

log = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    full_name TEXT,
    username TEXT,
    active INTEGER NOT NULL DEFAULT 1,
    banned INTEGER NOT NULL DEFAULT 0,
    joined_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY,
    added_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS movies (
    code INTEGER PRIMARY KEY AUTOINCREMENT,
    kind TEXT NOT NULL DEFAULT 'movie',
    title TEXT NOT NULL,
    search TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    category_id INTEGER,
    file_id TEXT,
    file_type TEXT,
    views INTEGER NOT NULL DEFAULT 0,
    added_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_movies_cat ON movies(category_id);
CREATE INDEX IF NOT EXISTS idx_movies_views ON movies(views);
CREATE TABLE IF NOT EXISTS episodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    movie_code INTEGER NOT NULL,
    number INTEGER NOT NULL,
    file_id TEXT NOT NULL,
    file_type TEXT NOT NULL,
    UNIQUE(movie_code, number)
);
CREATE TABLE IF NOT EXISTS favorites (
    user_id INTEGER NOT NULL,
    movie_code INTEGER NOT NULL,
    PRIMARY KEY (user_id, movie_code)
);
CREATE TABLE IF NOT EXISTS channels (
    chat_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    link TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS fsm (
    key TEXT PRIMARY KEY,
    state TEXT,
    data TEXT NOT NULL DEFAULT '{}'
);
"""


class DB:
    def __init__(self):
        self.path = cfg.DB_PATH
        self.conn: aiosqlite.Connection | None = None
        self.lock: asyncio.Lock | None = None
        self.admin_ids: set[int] = set()
        self.banned_ids: set[int] = set()
        self.settings: dict[str, str] = {}
        self._seen: dict[int, tuple] = {}

    # ------------------------------------------------ lifecycle
    async def init(self):
        self.lock = asyncio.Lock()
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = await aiosqlite.connect(self.path)
        self.conn.row_factory = aiosqlite.Row
        await self.conn.execute("PRAGMA journal_mode=WAL")
        await self.conn.execute("PRAGMA synchronous=NORMAL")
        await self.conn.execute("PRAGMA busy_timeout=5000")
        await self.conn.executescript(SCHEMA)
        await self.conn.commit()
        self.admin_ids = {r["id"] for r in await self.fetchall("SELECT id FROM admins")}
        self.banned_ids = {r["id"] for r in await self.fetchall("SELECT id FROM users WHERE banned=1")}
        self.settings = {r["key"]: r["value"] for r in await self.fetchall("SELECT key, value FROM settings")}

    async def close(self):
        if self.conn:
            await self.conn.close()
            self.conn = None

    # ------------------------------------------------ primitives
    async def execute(self, sql: str, params: tuple = ()):
        async with self.lock:
            cur = await self.conn.execute(sql, params)
            await self.conn.commit()
            return cur

    async def transaction(self, statements: list[tuple[str, tuple]]):
        async with self.lock:
            try:
                for sql, params in statements:
                    await self.conn.execute(sql, params)
                await self.conn.commit()
            except Exception:
                await self.conn.rollback()
                raise

    async def fetchall(self, sql: str, params: tuple = ()):
        cur = await self.conn.execute(sql, params)
        rows = await cur.fetchall()
        await cur.close()
        return rows

    async def fetchone(self, sql: str, params: tuple = ()):
        cur = await self.conn.execute(sql, params)
        row = await cur.fetchone()
        await cur.close()
        return row

    async def scalar(self, sql: str, params: tuple = ()):
        row = await self.fetchone(sql, params)
        return row[0] if row else None

    async def vacuum_into(self, path: str):
        async with self.lock:
            await self.conn.execute("VACUUM INTO ?", (path,))

    # ------------------------------------------------ settings
    async def set_setting(self, key: str, value: str):
        await self.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )
        self.settings[key] = value

    async def del_setting(self, key: str):
        await self.execute("DELETE FROM settings WHERE key=?", (key,))
        self.settings.pop(key, None)

    # ------------------------------------------------ admins / users
    async def add_admin(self, uid: int):
        await self.execute("INSERT OR IGNORE INTO admins (id) VALUES (?)", (uid,))
        self.admin_ids.add(uid)

    async def remove_admin(self, uid: int):
        await self.execute("DELETE FROM admins WHERE id=?", (uid,))
        self.admin_ids.discard(uid)

    async def touch_user(self, user) -> bool:
        """Foydalanuvchini saqlaydi/yangilaydi. Ban holatini qaytaradi."""
        now = time.time()
        sig = (user.full_name, user.username)
        cached = self._seen.get(user.id)
        if cached is None or cached[0] != sig or now - cached[1] > 600:
            await self.execute(
                """INSERT INTO users (id, full_name, username) VALUES (?, ?, ?)
                   ON CONFLICT(id) DO UPDATE SET full_name=excluded.full_name,
                   username=excluded.username, active=1, last_seen=CURRENT_TIMESTAMP""",
                (user.id, user.full_name, user.username),
            )
            self._seen[user.id] = (sig, now)
        return user.id in self.banned_ids

    async def set_banned(self, uid: int, banned: bool):
        await self.execute(
            "INSERT INTO users (id, banned) VALUES (?, ?) "
            "ON CONFLICT(id) DO UPDATE SET banned=excluded.banned",
            (uid, int(banned)),
        )
        (self.banned_ids.add if banned else self.banned_ids.discard)(uid)

    # ------------------------------------------------ movies
    async def add_movie(self, *, title, description, category_id, kind, file_id=None, file_type=None) -> int:
        cur = await self.execute(
            "INSERT INTO movies (kind, title, search, description, category_id, file_id, file_type) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (kind, title, title.lower(), description, category_id, file_id, file_type),
        )
        return cur.lastrowid

    async def get_movie(self, code: int):
        return await self.fetchone(
            "SELECT m.*, c.name AS category FROM movies m "
            "LEFT JOIN categories c ON c.id = m.category_id WHERE m.code = ?",
            (code,),
        )

    async def search_movies(self, query: str, limit: int = 15):
        words = [w for w in query.lower().split() if w][:5]
        if not words:
            return []
        cond = " AND ".join("search LIKE ? ESCAPE '\\'" for _ in words)
        params = tuple(
            "%" + w.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%" for w in words
        )
        return await self.fetchall(
            f"SELECT code, title, kind FROM movies WHERE {cond} "
            "ORDER BY views DESC, code DESC LIMIT ?",
            params + (limit,),
        )

    async def delete_movie(self, code: int):
        await self.transaction([
            ("DELETE FROM episodes WHERE movie_code=?", (code,)),
            ("DELETE FROM favorites WHERE movie_code=?", (code,)),
            ("DELETE FROM movies WHERE code=?", (code,)),
        ])

    async def add_view(self, code: int):
        await self.execute("UPDATE movies SET views = views + 1 WHERE code=?", (code,))

    # ------------------------------------------------ episodes
    async def add_episode(self, code: int, file_id: str, file_type: str) -> int:
        cur = await self.execute(
            "INSERT INTO episodes (movie_code, number, file_id, file_type) "
            "SELECT ?, COALESCE(MAX(number), 0) + 1, ?, ? FROM episodes WHERE movie_code=?",
            (code, file_id, file_type, code),
        )
        return await self.scalar("SELECT number FROM episodes WHERE id=?", (cur.lastrowid,))

    async def episode_numbers(self, code: int) -> list[int]:
        rows = await self.fetchall(
            "SELECT number FROM episodes WHERE movie_code=? ORDER BY number", (code,)
        )
        return [r["number"] for r in rows]

    async def get_episode(self, code: int, number: int):
        return await self.fetchone(
            "SELECT * FROM episodes WHERE movie_code=? AND number=?", (code, number)
        )

    async def neighbors(self, code: int, number: int):
        prev = await self.scalar(
            "SELECT MAX(number) FROM episodes WHERE movie_code=? AND number<?", (code, number))
        nxt = await self.scalar(
            "SELECT MIN(number) FROM episodes WHERE movie_code=? AND number>?", (code, number))
        return prev, nxt

    async def delete_episode(self, code: int, number: int) -> bool:
        cur = await self.execute(
            "DELETE FROM episodes WHERE movie_code=? AND number=?", (code, number))
        return cur.rowcount > 0

    # ------------------------------------------------ favorites
    async def is_fav(self, user_id: int, code: int) -> bool:
        return bool(await self.scalar(
            "SELECT 1 FROM favorites WHERE user_id=? AND movie_code=?", (user_id, code)))

    async def toggle_fav(self, user_id: int, code: int) -> bool:
        if await self.is_fav(user_id, code):
            await self.execute(
                "DELETE FROM favorites WHERE user_id=? AND movie_code=?", (user_id, code))
            return False
        await self.execute(
            "INSERT OR IGNORE INTO favorites (user_id, movie_code) VALUES (?, ?)", (user_id, code))
        return True


db = DB()
