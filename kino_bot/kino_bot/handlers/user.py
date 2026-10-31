"""User-facing commands and movie-code lookup for aiogram 3.x."""

from __future__ import annotations

import logging
from urllib.parse import urlparse

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import ADMIN_ID
from database import Database
from handlers.subscription import START_MESSAGE, require_subscription


logger = logging.getLogger(__name__)
router = Router(name="user")

MOVIE_NOT_FOUND_MESSAGE = "❌ Afsuski, bunday kodli kino topilmadi."


def _is_http_url(value: str) -> bool:
    """Return True for an HTTP(S) URL with a host name."""
    parsed = urlparse(value.strip())
    return parsed.scheme.lower() in {"http", "https"} and bool(parsed.netloc)


async def _prepare_user_request(
    message: Message,
    bot: Bot,
    db: Database,
) -> bool:
    """Check membership and register the user before serving a request."""
    user = message.from_user
    if user is None:
        return False

    if user.id != ADMIN_ID and not await require_subscription(message, bot):
        return False

    await db.add_user(user.id)
    return True


@router.message(CommandStart())
async def start_command(
    message: Message,
    bot: Bot,
    db: Database,
) -> None:
    """Welcome a user after verifying required channel membership."""
    if not await _prepare_user_request(message, bot, db):
        return

    await message.answer(START_MESSAGE)


@router.message(F.text, ~F.text.startswith("/"))
async def search_movie(
    message: Message,
    bot: Bot,
    db: Database,
) -> None:
    """Find a movie by its case-insensitive code and send its video or link."""
    if not await _prepare_user_request(message, bot, db):
        return

    code = (message.text or "").strip()
    if not code:
        await message.answer(MOVIE_NOT_FOUND_MESSAGE)
        return

    movie = await db.get_movie(code)
    if movie is None:
        await message.answer(MOVIE_NOT_FOUND_MESSAGE)
        return

    title = movie["title"]
    media = movie["file_id_or_link"].strip()

    if _is_http_url(media):
        await message.answer(f"🎬 {title}\n\n{media}")
        return

    try:
        await message.answer_video(
            video=media,
            caption=f"🎬 {title}",
        )
    except TelegramBadRequest:
        logger.exception("Could not send the video for movie code %s.", code)
        await message.answer(
            "❌ Kino videosini yuborib bo'lmadi. Administrator bilan bog'laning."
        )