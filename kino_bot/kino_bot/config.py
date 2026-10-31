"""Configuration for the Kino Telegram bot.

Values are read from environment variables (or a local .env file). The example
placeholders make the file easy to run locally after filling in the required
bot token and administrator ID.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

try:
    ADMIN_ID = int(os.getenv("ADMIN_ID", "0").strip())
except ValueError as exc:
    raise ValueError("ADMIN_ID must be a valid integer Telegram user ID.") from exc

_channels_value = os.getenv("CHANNELS", "@channel1,@channel2")
CHANNELS = [
    channel.strip()
    for channel in _channels_value.split(",")
    if channel.strip()
]

_database_path = os.getenv("DATABASE_PATH", "kino_bot.db").strip()
DATABASE_PATH = (
    Path(_database_path)
    if Path(_database_path).is_absolute()
    else PROJECT_DIR / _database_path
)