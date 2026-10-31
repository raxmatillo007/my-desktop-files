import html
import logging
import time

from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.filters import BaseFilter
from aiogram.types import Message, TelegramObject

from .config import cfg
from .database import db

log = logging.getLogger(__name__)


class Runtime:
    bot_username: str = ""


rt = Runtime()


def esc(text) -> str:
    return html.escape(str(text if text is not None else ""))


def deeplink(code: int) -> str:
    return f"https://t.me/{rt.bot_username}?start=m{code}"


def is_super(uid: int) -> bool:
    return uid in cfg.SUPER_ADMINS


def is_admin(uid: int) -> bool:
    return uid in cfg.SUPER_ADMINS or uid in db.admin_ids


class IsAdmin(BaseFilter):
    async def __call__(self, event: TelegramObject) -> bool:
        user = getattr(event, "from_user", None)
        return bool(user) and is_admin(user.id)


async def safe_edit(message: Message, text: str, reply_markup=None):
    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            log.warning("edit_text bajarilmadi: %s", e)


# ------------------------------------------------ majburiy obuna
_sub_ok: dict[int, float] = {}
SUB_CACHE_SECONDS = 120


async def get_unsubscribed(bot: Bot, user_id: int, use_cache: bool = True) -> list:
    if is_admin(user_id):
        return []
    if use_cache and time.time() - _sub_ok.get(user_id, 0) < SUB_CACHE_SECONDS:
        return []
    result = []
    for ch in await db.fetchall("SELECT * FROM channels"):
        try:
            member = await bot.get_chat_member(ch["chat_id"], user_id)
            left = member.status in (ChatMemberStatus.LEFT, ChatMemberStatus.KICKED)
            gone = (member.status == ChatMemberStatus.RESTRICTED
                    and not getattr(member, "is_member", True))
            if left or gone:
                result.append(ch)
        except (TelegramBadRequest, TelegramForbiddenError) as e:
            log.warning("Kanal %s tekshirilmadi (bot admin emasmi?): %s", ch["chat_id"], e)
    if not result:
        _sub_ok[user_id] = time.time()
        if len(_sub_ok) > 100_000:
            _sub_ok.clear()
    return result


async def ensure_sub(bot: Bot, user_id: int, payload: str = "0") -> bool:
    """Obuna bo'lgan bo'lsa True. Aks holda obuna xabarini yuboradi va False qaytaradi."""
    from . import keyboards as kb  # circular import oldini olish

    unsub = await get_unsubscribed(bot, user_id)
    if not unsub:
        return True
    await bot.send_message(
        user_id,
        "❗ Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling, so'ng "
        "«✅ Tekshirish» tugmasini bosing:",
        reply_markup=kb.sub_kb(unsub, payload),
    )
    return False
