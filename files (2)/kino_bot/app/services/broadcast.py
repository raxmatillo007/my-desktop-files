import asyncio
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from aiogram.types import Message

from ..database import db

log = logging.getLogger(__name__)


async def _copy(bot: Bot, uid: int, from_chat: int, msg_id: int):
    await bot.copy_message(uid, from_chat, msg_id)


async def run_broadcast(bot: Bot, admin_id: int, status: Message, from_chat: int, msg_id: int):
    users = await db.fetchall("SELECT id FROM users WHERE active=1 AND banned=0")
    total = len(users)
    ok = fail = blocked = 0
    for i, u in enumerate(users, 1):
        uid = u["id"]
        try:
            await _copy(bot, uid, from_chat, msg_id)
            ok += 1
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after + 1)
            try:
                await _copy(bot, uid, from_chat, msg_id)
                ok += 1
            except Exception:
                fail += 1
        except TelegramForbiddenError:
            await db.execute("UPDATE users SET active=0 WHERE id=?", (uid,))
            blocked += 1
        except Exception as e:
            log.warning("Broadcast xatosi %s: %s", uid, e)
            fail += 1
        if i % 100 == 0:
            try:
                await status.edit_text(f"⏳ Yuborilmoqda... {i}/{total}")
            except Exception:
                pass
        await asyncio.sleep(0.04)
    text = (f"📨 <b>Yuborish tugadi</b>\n\n👥 Jami: {total}\n✅ Yetkazildi: {ok}\n"
            f"🚫 Botni bloklagan: {blocked}\n❌ Xato: {fail}")
    try:
        await status.edit_text(text)
    except Exception:
        await bot.send_message(admin_id, text)
