import logging

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import SimpleEventIsolation
from aiogram.types import ErrorEvent

from .config import cfg
from .database import db
from .handlers.admin_content import content
from .handlers.admin_core import core
from .handlers.admin_system import system
from .handlers.user import user
from .middlewares import ThrottleMiddleware, UserMiddleware
from .storage import SQLiteStorage

log = logging.getLogger(__name__)


def build_dispatcher(throttle: float | None = None) -> Dispatcher:
    dp = Dispatcher(storage=SQLiteStorage(db), events_isolation=SimpleEventIsolation())
    rate = cfg.THROTTLE if throttle is None else throttle
    throttle_mw, user_mw = ThrottleMiddleware(rate), UserMiddleware()
    dp.throttle_mw = throttle_mw  # sinov va sozlash uchun
    for observer in (dp.message, dp.callback_query):
        observer.outer_middleware(throttle_mw)
        observer.outer_middleware(user_mw)

    # Tartib muhim: /cancel va /admin (core) holat ishlovchilaridan oldin turishi kerak
    dp.include_routers(core, content, system, user)

    @dp.error()
    async def on_error(event: ErrorEvent):
        log.exception("Kutilmagan xato: %s", event.exception)
        return True

    return dp
