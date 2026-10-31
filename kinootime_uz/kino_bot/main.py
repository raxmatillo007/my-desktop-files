import asyncio
import logging
import sys
from logging.handlers import RotatingFileHandler

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, BotCommandScopeChat

from app.bot_factory import build_dispatcher
from app.config import cfg
from app.database import db
from app.services.backup import backup_loop
from app.utils import rt

log = logging.getLogger("kino_bot")


def setup_logging():
    cfg.LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.StreamHandler(),
            RotatingFileHandler(cfg.LOG_DIR / "bot.log", maxBytes=5_000_000,
                                backupCount=3, encoding="utf-8"),
        ],
    )


async def set_commands(bot: Bot):
    base = [BotCommand(command="start", description="Botni ishga tushirish"),
            BotCommand(command="help", description="Yordam")]
    await bot.set_my_commands(base)
    admin_cmds = base + [BotCommand(command="admin", description="Admin panel"),
                         BotCommand(command="cancel", description="Amalni bekor qilish"),
                         BotCommand(command="edit_code", description="Kino kodini o'zgartirish")]
    for admin_id in cfg.SUPER_ADMINS:
        try:
            await bot.set_my_commands(admin_cmds, scope=BotCommandScopeChat(chat_id=admin_id))
        except Exception as e:
            log.warning("Admin buyruqlari %s uchun o'rnatilmadi: %s", admin_id, e)


async def main():
    setup_logging()
    if not cfg.BOT_TOKEN:
        sys.exit("❌ BOT_TOKEN topilmadi. .env faylini to'ldiring.")
    if not cfg.SUPER_ADMINS:
        log.warning("ADMINS bo'sh! Admin panelga hech kim kira olmaydi.")

    await db.init()
    bot = Bot(cfg.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    rt.bot_username = (await bot.get_me()).username or ""
    dp = build_dispatcher()
    await set_commands(bot)
    backup_task = asyncio.create_task(backup_loop(bot))

    log.info("Bot ishga tushdi: @%s", rt.bot_username)
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        backup_task.cancel()
        await bot.session.close()
        await db.close()
        log.info("Bot to'xtatildi.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
