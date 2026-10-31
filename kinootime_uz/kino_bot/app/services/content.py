"""Kino/serial ko'rsatish va ro'yxatlar."""
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from .. import keyboards as kb
from ..config import cfg
from ..database import db
from ..utils import deeplink, esc, rt

log = logging.getLogger(__name__)


def _protect() -> bool:
    return db.settings.get("protect") == "1"


def _footer() -> str:
    return f"\n🤖 @{rt.bot_username}" if rt.bot_username else ""


def card_text(m) -> str:
    icon = "📺" if m["kind"] == "series" else "🎬"
    text = f"{icon} <b>{esc(m['title'])}</b>\n"
    if m["category"]:
        text += f"🗂 {esc(m['category'])}\n"
    if m["description"]:
        text += f"\n{esc(m['description'][:500])}\n"
    text += f"\n🔢 Kod: <code>{m['code']}</code>"
    return text


async def _send_file(bot: Bot, chat_id: int, file_type: str, file_id: str, caption: str, markup):
    kwargs = dict(caption=caption, reply_markup=markup, protect_content=_protect())
    if file_type == "video":
        return await bot.send_video(chat_id, file_id, **kwargs)
    return await bot.send_document(chat_id, file_id, **kwargs)


async def show_movie(bot: Bot, user_id: int, code: int) -> None:
    movie = await db.get_movie(code)
    if not movie:
        await bot.send_message(user_id, "❌ Bunday kodli kino topilmadi.")
        return
    is_fav = await db.is_fav(user_id, code)
    link = deeplink(code)

    if movie["kind"] == "series":
        numbers = await db.episode_numbers(code)
        if not numbers:
            await bot.send_message(user_id, "📭 Bu serialga hali qismlar yuklanmagan.")
            return
        await db.add_view(code)
        text = card_text(movie) + f"\n📺 Qismlar soni: <b>{len(numbers)}</b>" + _footer()
        await bot.send_message(
            user_id, text,
            reply_markup=kb.episodes_kb(code, numbers, 0, is_fav),
        )
        return

    try:
        await _send_file(bot, user_id, movie["file_type"], movie["file_id"],
                         card_text(movie) + _footer(),
                         kb.movie_kb(code, is_fav))
    except TelegramForbiddenError:
        return
    except TelegramBadRequest as e:
        log.error("Kino yuborilmadi (kod %s): %s", code, e)
        await bot.send_message(user_id, "⚠️ Kinoni yuborishda xatolik. Keyinroq urinib ko'ring.")
        return
    await db.add_view(code)


async def show_episode(bot: Bot, user_id: int, code: int, number: int) -> None:
    movie = await db.get_movie(code)
    ep = await db.get_episode(code, number)
    if not movie or not ep:
        await bot.send_message(user_id, "❌ Qism topilmadi.")
        return
    prev, nxt = await db.neighbors(code, number)
    caption = (f"📺 <b>{esc(movie['title'])}</b> - {number}-qism\n\n"
               f"🔢 Kod: <code>{code}</code>" + _footer())
    try:
        await _send_file(bot, user_id, ep["file_type"], ep["file_id"], caption,
                         kb.episode_nav_kb(code, prev, nxt))
    except TelegramForbiddenError:
        return
    except TelegramBadRequest as e:
        log.error("Qism yuborilmadi (%s/%s): %s", code, number, e)
        await bot.send_message(user_id, "⚠️ Qismni yuborishda xatolik.")


async def render_list(kind: str, arg: int, user_id: int, page: int):
    """(matn, klaviatura) qaytaradi."""
    per = cfg.PAGE_SIZE
    off = max(page, 0) * per
    cols = "m.code, m.title, m.kind"
    if kind == "cat":
        name = await db.scalar("SELECT name FROM categories WHERE id=?", (arg,))
        title = f"🗂 <b>{esc(name or 'Kategoriya')}</b>"
        total = await db.scalar("SELECT COUNT(*) FROM movies WHERE category_id=?", (arg,))
        rows = await db.fetchall(
            f"SELECT {cols} FROM movies m WHERE category_id=? ORDER BY code DESC LIMIT ? OFFSET ?",
            (arg, per, off))
    elif kind == "top":
        title = "🔥 <b>Eng ko'p ko'rilgan</b>"
        total = await db.scalar("SELECT COUNT(*) FROM movies")
        rows = await db.fetchall(
            f"SELECT {cols} FROM movies m ORDER BY views DESC, code DESC LIMIT ? OFFSET ?", (per, off))
    elif kind == "fav":
        title = "❤️ <b>Sevimlilar</b>"
        total = await db.scalar("SELECT COUNT(*) FROM favorites WHERE user_id=?", (user_id,))
        rows = await db.fetchall(
            f"SELECT {cols} FROM favorites f JOIN movies m ON m.code=f.movie_code "
            "WHERE f.user_id=? ORDER BY m.code DESC LIMIT ? OFFSET ?", (user_id, per, off))
    else:
        kind = "new"
        title = "🆕 <b>Yangi qo'shilganlar</b>"
        total = await db.scalar("SELECT COUNT(*) FROM movies")
        rows = await db.fetchall(
            f"SELECT {cols} FROM movies m ORDER BY code DESC LIMIT ? OFFSET ?", (per, off))
    if not total:
        return f"{title}\n\n📭 Hozircha bo'sh.", (kb.list_kb([], kind, arg, 0, 0, per) if kind == "cat" else None)
    return (f"{title}\n\nJami: {total} ta",
            kb.list_kb(rows, kind, arg, page, total, per))


async def categories_view():
    rows = await db.fetchall(
        "SELECT c.id, c.name, COUNT(m.code) AS n FROM categories c "
        "LEFT JOIN movies m ON m.category_id = c.id "
        "GROUP BY c.id HAVING COUNT(m.code) > 0 ORDER BY c.name")
    if not rows:
        return "🗂 Kategoriyalar hali yo'q.", None
    return "🗂 <b>Kategoriyani tanlang:</b>", kb.grid(
        [[(f"{r['name']} ({r['n']})", f"lst:cat:{r['id']}:0")] for r in rows])
