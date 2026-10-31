"""Inline keyboards used by the Kino bot."""

from __future__ import annotations

from collections.abc import Sequence
from urllib.parse import urlparse

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import CHANNELS


def _channel_url(channel: str) -> str:
    """Build a Telegram URL for a public channel username or t.me URL."""
    value = channel.strip()
    parsed = urlparse(value)

    if parsed.scheme in {"http", "https"} and parsed.netloc.lower() in {
        "t.me",
        "www.t.me",
    }:
        return value

    username = value.removeprefix("@").strip("/")
    return f"https://t.me/{username}"


def subscription_keyboard(
    channels: Sequence[str] | None = None,
) -> InlineKeyboardMarkup:
    """Create channel buttons followed by the subscription confirmation button."""
    required_channels = CHANNELS if channels is None else channels
    builder = InlineKeyboardBuilder()

    for index, channel in enumerate(required_channels, start=1):
        builder.button(
            text=f"📢 Kanal {index}",
            url=_channel_url(channel),
        )

    builder.adjust(1)
    builder.row(
        InlineKeyboardButton(
            text="✅ Tasdiqlash",
            callback_data="check_sub",
        )
    )
    return builder.as_markup()


def admin_keyboard() -> InlineKeyboardMarkup:
    """Create the administrator's main menu."""
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Statistika", callback_data="admin:stats")
    builder.button(text="➕ Kino qo'shish", callback_data="admin:add_movie")
    builder.button(text="🗑 Kino o'chirish", callback_data="admin:delete_movie")
    builder.button(text="📢 Xabar yuborish", callback_data="admin:broadcast")
    builder.button(text="❌ Yopish", callback_data="admin:close")
    builder.adjust(1)
    return builder.as_markup()