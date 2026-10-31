import time
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from .database import db
from .utils import is_admin


class ThrottleMiddleware(BaseMiddleware):
    """Spamdan himoya: bir foydalanuvchidan juda tez kelgan so'rovlarni tashlab yuboradi."""

    def __init__(self, rate: float):
        self.rate = rate
        self._last: dict[int, float] = {}

    async def __call__(self, handler: Callable[[TelegramObject, dict], Awaitable[Any]],
                       event: TelegramObject, data: dict):
        user = data.get("event_from_user")
        if user is None or self.rate <= 0 or is_admin(user.id):
            return await handler(event, data)
        now = time.monotonic()
        if now - self._last.get(user.id, 0) < self.rate:
            if isinstance(event, CallbackQuery):
                await event.answer("⏳ Sekinroq, iltimos", cache_time=1)
            return None
        self._last[user.id] = now
        if len(self._last) > 50_000:
            cutoff = now - 60
            self._last = {k: v for k, v in self._last.items() if v > cutoff}
        return await handler(event, data)


class UserMiddleware(BaseMiddleware):
    """Foydalanuvchini bazaga yozadi va bloklanganlarni to'xtatadi."""

    async def __call__(self, handler, event: TelegramObject, data: dict):
        user = data.get("event_from_user")
        if user is not None and not user.is_bot:
            banned = await db.touch_user(user)
            if banned and not is_admin(user.id):
                if isinstance(event, CallbackQuery):
                    await event.answer("🚫 Siz bloklangansiz.", show_alert=True)
                elif isinstance(event, Message):
                    await event.answer("🚫 Siz bloklangansiz.")
                return None
        return await handler(event, data)
