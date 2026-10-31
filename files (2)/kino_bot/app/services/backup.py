import asyncio
import logging
from datetime import datetime
from pathlib import Path

from aiogram import Bot
from aiogram.types import FSInputFile

from ..config import cfg
from ..database import db

log = logging.getLogger(__name__)


async def make_backup() -> Path:
    cfg.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    path = cfg.BACKUP_DIR / f"kino_{datetime.now():%Y%m%d_%H%M%S}.db"
    await db.vacuum_into(str(path))
    files = sorted(cfg.BACKUP_DIR.glob("kino_*.db"))
    for old in files[:-cfg.BACKUP_KEEP]:
        old.unlink(missing_ok=True)
    return path


async def send_backup(bot: Bot, chat_id: int, path: Path):
    await bot.send_document(chat_id, FSInputFile(path),
                            caption=f"💾 Zaxira nusxa: {path.name}")


async def backup_loop(bot: Bot):
    """Har BACKUP_HOURS soatda zaxira olib, bosh adminlarga yuboradi."""
    if cfg.BACKUP_HOURS <= 0:
        return
    while True:
        await asyncio.sleep(cfg.BACKUP_HOURS * 3600)
        try:
            path = await make_backup()
            for admin_id in cfg.SUPER_ADMINS:
                try:
                    await send_backup(bot, admin_id, path)
                except Exception as e:
                    log.warning("Zaxira %s ga yuborilmadi: %s", admin_id, e)
            log.info("Zaxira nusxa olindi: %s", path)
        except asyncio.CancelledError:
            raise
        except Exception:
            log.exception("Zaxira olishda xato")
