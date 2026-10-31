"""Required-channel membership gate for aiogram 3.x."""

from __future__ import annotations

import logging
from collections.abc import Sequence

from aiogram import Bot, F, Router
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import CallbackQuery, Message

from config import ADMIN_ID, CHANNELS
from database import Database
from keyboards import subscription_keyboard


logger = logging.getLogger(__name__)
router = Router(name="subscription")

START_MESSAGE = (
    "Assalomu alaykum! Kino kodini yuboring, men sizga kino fayli yoki "
    "havolasini topib beraman."
)
JOIN_REQUIRED_MESSAGE = (
    "Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling, "
    "so'ng «✅ Tasdiqlash» tugmasini bosing."
)
SUBSCRIPTION_CONFIRMED_MESSAGE = (
    "Obuna tasdiqlandi.\n\n"
    "Assalomu alaykum! Kino kodini yuboring, men sizga kino fayli yoki "
    "havolasini topib beraman."
)

_ALLOWED_MEMBER_STATUSES = {
    ChatMemberStatus.CREATOR,
    ChatMemberStatus.ADMINISTRATOR,
    ChatMemberStatus.MEMBER,
}


async def is_subscribed(
    bot: Bot,
    user_id: int,
    channels: Sequence[str] | None = None,
) -> bool:
    """Return True only if the user has an allowed status in every channel."""
    required_channels = CHANNELS if channels is None else channels

    for channel in required_channels:
        try:
            member = await bot.get_chat_member(
                chat_id=channel,
                user_id=user_id,
            )
        except (TelegramBadRequest, TelegramForbiddenError):
            logger.warning(
                "Could not verify user %s in required channel %s; denying access.",
                user_id,
                channel,
                exc_info=True,
            )
            return False

        if member.status not in _ALLOWED_MEMBER_STATUSES:
            return False

    return True


async def require_subscription(message: Message, bot: Bot) -> bool:
    """Allow admins or subscribed users; prompt other users to join channels."""
    user = message.from_user
    if user is None or user.id == ADMIN_ID:
        return True

    if await is_subscribed(bot, user.id):
        return True

    await message.answer(
        JOIN_REQUIRED_MESSAGE,
        reply_markup=subscription_keyboard(),
    )
    return False


@router.callback_query(F.data == "check_sub")
async def check_subscription_callback(
    callback: CallbackQuery,
    bot: Bot,
    db: Database,
) -> None:
    """Recheck all required channels when the user confirms subscription."""
    if (
        callback.from_user.id != ADMIN_ID
        and not await is_subscribed(bot, callback.from_user.id)
    ):
        await callback.answer(
            "Siz hali barcha kanallarga obuna bo'lmadingiz.",
            show_alert=True,
        )
        return

    await db.add_user(callback.from_user.id)
    await callback.answer("Obuna tasdiqlandi.")
    if isinstance(callback.message, Message):
        await callback.message.answer(SUBSCRIPTION_CONFIRMED_MESSAGE)