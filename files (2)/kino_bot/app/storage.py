"""FSM holatlarini SQLite'da saqlaydi - bot qayta ishga tushsa ham admin jarayoni yo'qolmaydi."""
import json
from typing import Any, Dict, Optional

from aiogram.fsm.state import State
from aiogram.fsm.storage.base import BaseStorage, StateType, StorageKey

from .database import DB


class SQLiteStorage(BaseStorage):
    def __init__(self, db: DB):
        self.db = db

    @staticmethod
    def _key(key: StorageKey) -> str:
        return ":".join(str(getattr(key, f, 0) or 0) for f in
                        ("bot_id", "chat_id", "user_id", "thread_id", "destiny"))

    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        value = state.state if isinstance(state, State) else state
        await self.db.execute(
            "INSERT INTO fsm (key, state) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET state=excluded.state",
            (self._key(key), value),
        )

    async def get_state(self, key: StorageKey) -> Optional[str]:
        return await self.db.scalar("SELECT state FROM fsm WHERE key=?", (self._key(key),))

    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
        await self.db.execute(
            "INSERT INTO fsm (key, data) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET data=excluded.data",
            (self._key(key), json.dumps(data, ensure_ascii=False)),
        )

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        raw = await self.db.scalar("SELECT data FROM fsm WHERE key=?", (self._key(key),))
        return json.loads(raw) if raw else {}

    async def close(self) -> None:
        return None
