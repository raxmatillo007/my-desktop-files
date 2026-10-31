"""Application entry point for the Kino Telegram bot."""

from __future__ import annotations

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from config import BOT_TOKEN
from database import Database
from handlers.admin import router as admin_router
from handlers.subscription import router as subscription_router
from handlers.user import router as user_router


def create_dispatcher() -> Dispatcher:
    """Create the Dispatcher and register every bot router."""
    dispatcher = Dispatcher()
    dispatcher.include_router(subscription_router)
    dispatcher.include_router(user_router)
    dispatcher.include_router(admin_router)
    return dispatcher


async def main() -> None:
    """Initialize storage, register commands and routers, then start polling."""
    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN is missing. Add your Telegram bot token to kino_bot/.env."
        )

    database = Database()
    await database.init_db()
    dispatcher = create_dispatcher()

    commands = [
        BotCommand(command="start", description="Botni boshlash"),
        BotCommand(command="admin", description="Admin panel"),
        BotCommand(command="cancel", description="Joriy amalni bekor qilish"),
    ]

    async with Bot(token=BOT_TOKEN) as bot:
        await bot.set_my_commands(commands)
        await dispatcher.start_polling(bot, db=database)


if __name__ == "__main__":
    asyncio.run(main())