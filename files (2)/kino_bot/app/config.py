import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _ids(raw: str) -> list[int]:
    return [int(x) for x in raw.replace(" ", "").split(",") if x.lstrip("-").isdigit()]


class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "").strip()
    SUPER_ADMINS: list[int] = _ids(os.getenv("ADMINS", ""))
    DB_PATH: str = os.getenv("DB_PATH", "data/kino.db")
    BACKUP_DIR: Path = Path(os.getenv("BACKUP_DIR", "data/backups"))
    LOG_DIR: Path = Path(os.getenv("LOG_DIR", "data/logs"))
    BACKUP_HOURS: float = float(os.getenv("BACKUP_HOURS", "24"))
    BACKUP_KEEP: int = int(os.getenv("BACKUP_KEEP", "7"))
    THROTTLE: float = float(os.getenv("THROTTLE_SECONDS", "0.5"))
    PAGE_SIZE: int = 8


cfg = Config()
