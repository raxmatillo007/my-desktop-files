"""
Kino Bot - Telegram (aiogram 3 + SQLite)

Imkoniyatlar:
  Foydalanuvchi: kod yoki nom bo'yicha kino olish, majburiy obuna tekshiruvi
  Admin (/admin): kino qo'shish/o'chirish/ro'yxat, kanallar boshqaruvi,
                  statistika, barchaga xabar yuborish
"""
import asyncio
import html
import logging
import os
import sys

import aiosqlite
from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatMemberStatus, ParseMode
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramRetryAfter,
)
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, ErrorEvent, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMINS = [int(x) for x in os.getenv("ADMINS", "").replace(" ", "").split(",") if x.isdigit()]
DB_PATH = os.getenv("DB_PATH", "kino.db")
PROTECT_CONTENT = os.getenv("PROTECT_CONTENT", "false").lower() == "true"
PAGE_SIZE = 10

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("kino_bot")

BOT_USERNAME = ""
_tasks: set = set()


# ============================================================ DATABASE
SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    full_name TEXT,
    username TEXT,
    active INTEGER DEFAULT 1,
    joined_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS movies (
    code INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    search TEXT NOT NULL,
    description TEXT DEFAULT '',
    file_id TEXT NOT NULL,
    file_type TEXT NOT NULL,
    views INTEGER DEFAULT 0,
    added_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS channels (
    chat_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    link TEXT NOT NULL
);
"""


class DB:
    def __init__(self, path: str):
        self.path = path
        self.conn: aiosqlite.Connection | None = None

    async def init(self):
        self.conn = await aiosqlite.connect(self.path)
        self.conn.row_factory = aiosqlite.Row
        await self.conn.executescript(SCHEMA)
        await self.conn.commit()

    async def close(self):
        if self.conn:
            await self.conn.close()

    async def execute(self, sql: str, params: tuple = ()):
        cur = await self.conn.execute(sql, params)
        await self.conn.commit()
        return cur

    async def fetchall(self, sql: str, params: tuple = ()):
        cur = await self.conn.execute(sql, params)
        rows = await cur.fetchall()
        await cur.close()
        return rows

    async def fetchone(self, sql: str, params: tuple = ()):
        cur = await self.conn.execute(sql, params)
        row = await cur.fetchone()
        await cur.close()
        return row


db = DB(DB_PATH)


# ============================================================ HELPERS
def esc(text) -> str:
    return html.escape(str(text or ""))


async def safe_edit(message: Message, text: str, reply_markup=None):
    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            log.warning("edit_text xatosi: %s", e)


async def add_user(user):
    await db.execute(
        """INSERT INTO users (id, full_name, username) VALUES (?, ?, ?)
           ON CONFLICT(id) DO UPDATE SET full_name=excluded.full_name,
           username=excluded.username, active=1""",
        (user.id, user.full_name, user.username),
    )


async def get_unsubscribed(bot: Bot, user_id: int):
    """Foydalanuvchi obuna bo'lmagan kanallar ro'yxati."""
    if user_id in ADMINS:
        return []
    result = []
    for ch in await db.fetchall("SELECT * FROM channels"):
        try:
            member = await bot.get_chat_member(ch["chat_id"], user_id)
            left = member.status in (ChatMemberStatus.LEFT, ChatMemberStatus.KICKED)
            restricted_out = (
                member.status == ChatMemberStatus.RESTRICTED
                and not getattr(member, "is_member", True)
            )
            if left or restricted_out:
                result.append(ch)
        except (TelegramBadRequest, TelegramForbiddenError) as e:
            # Bot kanalda admin emas yoki kanal o'chirilgan - o'tkazib yuboramiz
            log.warning("Kanal %s tekshirilmadi: %s", ch["chat_id"], e)
    return result


def sub_kb(channels, code: int):
    b = InlineKeyboardBuilder()
    for ch in channels:
        b.button(text=f"📢 {ch['title']}", url=ch["link"])
    b.button(text="✅ Tekshirish", callback_data=f"check:{code}")
    b.adjust(1)
    return b.as_markup()


async def send_movie(bot: Bot, chat_id: int, movie) -> bool:
    caption = f"🎬 <b>{esc(movie['title'])}</b>\n"
    if movie["description"]:
        caption += f"\n{esc(movie['description'])[:600]}\n"
    caption += f"\n🔢 Kod: <code>{movie['code']}</code>"
    if BOT_USERNAME:
        caption += f"\n🤖 @{BOT_USERNAME}"
    try:
        if movie["file_type"] == "video":
            await bot.send_video(chat_id, movie["file_id"], caption=caption,
                                 protect_content=PROTECT_CONTENT)
        else:
            await bot.send_document(chat_id, movie["file_id"], caption=caption,
                                    protect_content=PROTECT_CONTENT)
    except TelegramBadRequest as e:
        log.error("Kino yuborilmadi (kod %s): %s", movie["code"], e)
        await bot.send_message(chat_id, "⚠️ Kinoni yuborishda xatolik. Keyinroq urinib ko'ring.")
        return False
    await db.execute("UPDATE movies SET views = views + 1 WHERE code = ?", (movie["code"],))
    return True


async def deliver_code(bot: Bot, chat_id: int, code: int):
    movie = await db.fetchone("SELECT * FROM movies WHERE code = ?", (code,))
    if not movie:
        await bot.send_message(chat_id, "❌ Bunday kodli kino topilmadi.")
        return
    await send_movie(bot, chat_id, movie)


WELCOME = (
    "👋 Assalomu alaykum, <b>{name}</b>!\n\n"
    "🎬 Kino olish uchun <b>kino kodini</b> yuboring.\n"
    "🔎 Yoki kino <b>nomini</b> yozib qidiring."
)


# ============================================================ USER ROUTER
user = Router()


@user.message(CommandStart())
async def cmd_start(m: Message, state: FSMContext, bot: Bot):
    await state.clear()
    await add_user(m.from_user)
    unsub = await get_unsubscribed(bot, m.from_user.id)
    if unsub:
        await m.answer("❗ Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:",
                       reply_markup=sub_kb(unsub, 0))
        return
    await m.answer(WELCOME.format(name=esc(m.from_user.full_name)))


@user.message(Command("help"))
async def cmd_help(m: Message):
    await m.answer(
        "ℹ️ <b>Yordam</b>\n\n"
        "• Kino kodini yuboring - kino keladi.\n"
        "• Kino nomini yozing - qidiruv natijalari chiqadi.\n"
        "• /start - botni qayta ishga tushirish."
    )


@user.callback_query(F.data.startswith("check:"))
async def cb_check(call: CallbackQuery, bot: Bot):
    code = int(call.data.split(":")[1])
    unsub = await get_unsubscribed(bot, call.from_user.id)
    if unsub:
        await call.answer("❌ Hali barcha kanallarga obuna bo'lmadingiz!", show_alert=True)
        return
    await call.answer("✅ Rahmat!")
    try:
        await call.message.delete()
    except TelegramBadRequest:
        pass
    if code > 0:
        await deliver_code(bot, call.from_user.id, code)
    else:
        await bot.send_message(call.from_user.id,
                               WELCOME.format(name=esc(call.from_user.full_name)))


@user.callback_query(F.data.startswith("movie:"))
async def cb_movie(call: CallbackQuery, bot: Bot):
    code = int(call.data.split(":")[1])
    unsub = await get_unsubscribed(bot, call.from_user.id)
    if unsub:
        await call.answer()
        await bot.send_message(call.from_user.id,
                               "❗ Avval quyidagi kanallarga obuna bo'ling:",
                               reply_markup=sub_kb(unsub, code))
        return
    await call.answer()
    await deliver_code(bot, call.from_user.id, code)


@user.message(StateFilter(None), F.text)
async def on_text(m: Message, bot: Bot):
    text = m.text.strip()
    if text.startswith("/"):
        return
    await add_user(m.from_user)
    is_code = text.isdigit() and len(text) < 10
    code = int(text) if is_code else 0

    unsub = await get_unsubscribed(bot, m.from_user.id)
    if unsub:
        await m.answer("❗ Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:",
                       reply_markup=sub_kb(unsub, code))
        return

    if is_code:
        await deliver_code(bot, m.chat.id, code)
        return

    if len(text) < 2:
        await m.answer("🔎 Qidirish uchun kamida 2 ta harf yozing.")
        return
    rows = await db.fetchall(
        "SELECT code, title FROM movies WHERE search LIKE ? ORDER BY views DESC LIMIT 10",
        (f"%{text.lower()}%",),
    )
    if not rows:
        await m.answer("😕 Hech narsa topilmadi. Kino kodini yuborib ko'ring.")
        return
    b = InlineKeyboardBuilder()
    for r in rows:
        b.button(text=f"🎬 {r['title']} ({r['code']})", callback_data=f"movie:{r['code']}")
    b.adjust(1)
    await m.answer("🔎 Qidiruv natijalari:", reply_markup=b.as_markup())


# ============================================================ ADMIN ROUTER
admin = Router()
admin.message.filter(F.from_user.id.in_(ADMINS))
admin.callback_query.filter(F.from_user.id.in_(ADMINS))


class AddMovie(StatesGroup):
    file = State()
    title = State()
    desc = State()


class DelMovie(StatesGroup):
    code = State()


class AddChannel(StatesGroup):
    chat = State()


class Broadcast(StatesGroup):
    msg = State()
    confirm = State()


def admin_menu():
    b = InlineKeyboardBuilder()
    b.button(text="➕ Kino qo'shish", callback_data="adm:add")
    b.button(text="🗑 Kino o'chirish", callback_data="adm:del")
    b.button(text="🎞 Kinolar ro'yxati", callback_data="adm:list:0")
    b.button(text="📢 Kanallar", callback_data="adm:ch")
    b.button(text="📊 Statistika", callback_data="adm:stats")
    b.button(text="📨 Xabar yuborish", callback_data="adm:bc")
    b.adjust(2)
    return b.as_markup()


def back_kb():
    b = InlineKeyboardBuilder()
    b.button(text="⬅️ Admin panel", callback_data="adm:back")
    return b.as_markup()


@admin.message(Command("cancel"))
async def adm_cancel(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("❌ Bekor qilindi.", reply_markup=admin_menu())


@admin.message(Command("admin"))
async def adm_panel(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("🛠 <b>Admin panel</b>", reply_markup=admin_menu())


@admin.callback_query(F.data == "adm:back")
async def adm_back(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer()
    await safe_edit(call.message, "🛠 <b>Admin panel</b>", admin_menu())


# ---------- Kino qo'shish
@admin.callback_query(F.data == "adm:add")
async def add_start(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(AddMovie.file)
    await call.message.answer("🎥 Kino faylini (video yoki hujjat) yuboring.\nBekor qilish: /cancel")


@admin.message(AddMovie.file, F.video | F.document)
async def add_file(m: Message, state: FSMContext):
    if m.video:
        await state.update_data(file_id=m.video.file_id, file_type="video")
    else:
        await state.update_data(file_id=m.document.file_id, file_type="document")
    await state.set_state(AddMovie.title)
    await m.answer("✏️ Kino nomini yuboring:")


@admin.message(AddMovie.file)
async def add_file_bad(m: Message):
    await m.answer("⚠️ Iltimos, video yoki hujjat yuboring. Bekor qilish: /cancel")


@admin.message(AddMovie.title, F.text)
async def add_title(m: Message, state: FSMContext):
    title = m.text.strip()
    if not title or len(title) > 200:
        await m.answer("⚠️ Nom 1-200 belgi bo'lishi kerak.")
        return
    await state.update_data(title=title)
    await state.set_state(AddMovie.desc)
    await m.answer("📝 Tavsif yuboring (kerak bo'lmasa <code>-</code> yuboring):")


@admin.message(AddMovie.desc, F.text)
async def add_desc(m: Message, state: FSMContext):
    desc = "" if m.text.strip() == "-" else m.text.strip()[:600]
    data = await state.get_data()
    cur = await db.execute(
        "INSERT INTO movies (title, search, description, file_id, file_type) VALUES (?, ?, ?, ?, ?)",
        (data["title"], data["title"].lower(), desc, data["file_id"], data["file_type"]),
    )
    await state.clear()
    await m.answer(
        f"✅ Kino qo'shildi!\n\n🎬 <b>{esc(data['title'])}</b>\n🔢 Kod: <code>{cur.lastrowid}</code>",
        reply_markup=admin_menu(),
    )


# ---------- Kino o'chirish
@admin.callback_query(F.data == "adm:del")
async def del_start(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(DelMovie.code)
    await call.message.answer("🗑 O'chiriladigan kino kodini yuboring.\nBekor qilish: /cancel")


@admin.message(DelMovie.code, F.text)
async def del_code(m: Message, state: FSMContext):
    if not m.text.strip().isdigit():
        await m.answer("⚠️ Faqat raqam yuboring.")
        return
    code = int(m.text.strip())
    movie = await db.fetchone("SELECT title FROM movies WHERE code = ?", (code,))
    if not movie:
        await m.answer("❌ Bunday kodli kino yo'q.")
        return
    await db.execute("DELETE FROM movies WHERE code = ?", (code,))
    await state.clear()
    await m.answer(f"✅ <b>{esc(movie['title'])}</b> o'chirildi.", reply_markup=admin_menu())


# ---------- Kinolar ro'yxati
@admin.callback_query(F.data.startswith("adm:list:"))
async def movie_list(call: CallbackQuery):
    page = max(int(call.data.split(":")[2]), 0)
    total = (await db.fetchone("SELECT COUNT(*) AS c FROM movies"))["c"]
    rows = await db.fetchall(
        "SELECT code, title, views FROM movies ORDER BY code DESC LIMIT ? OFFSET ?",
        (PAGE_SIZE, page * PAGE_SIZE),
    )
    await call.answer()
    if not rows:
        await safe_edit(call.message, "📭 Kinolar yo'q.", back_kb())
        return
    pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    text = f"🎞 <b>Kinolar</b> ({page + 1}/{pages}), jami: {total}\n\n"
    text += "\n".join(f"<code>{r['code']}</code> - {esc(r['title'])} (👁 {r['views']})" for r in rows)
    b = InlineKeyboardBuilder()
    if page > 0:
        b.button(text="⬅️", callback_data=f"adm:list:{page - 1}")
    if (page + 1) * PAGE_SIZE < total:
        b.button(text="➡️", callback_data=f"adm:list:{page + 1}")
    b.button(text="🏠 Admin panel", callback_data="adm:back")
    b.adjust(2, 1)
    await safe_edit(call.message, text, b.as_markup())


# ---------- Kanallar
async def channels_view(message: Message):
    rows = await db.fetchall("SELECT * FROM channels")
    b = InlineKeyboardBuilder()
    for r in rows:
        b.button(text=f"🗑 {r['title']}", callback_data=f"chdel:{r['chat_id']}")
    b.button(text="➕ Kanal qo'shish", callback_data="adm:chadd")
    b.button(text="🏠 Admin panel", callback_data="adm:back")
    b.adjust(1)
    text = "📢 <b>Majburiy obuna kanallari</b>\n\n"
    text += "Bo'sh." if not rows else "O'chirish uchun kanal tugmasini bosing."
    await safe_edit(message, text, b.as_markup())


@admin.callback_query(F.data == "adm:ch")
async def ch_menu(call: CallbackQuery):
    await call.answer()
    await channels_view(call.message)


@admin.callback_query(F.data.startswith("chdel:"))
async def ch_del(call: CallbackQuery):
    await db.execute("DELETE FROM channels WHERE chat_id = ?", (int(call.data.split(":")[1]),))
    await call.answer("🗑 O'chirildi")
    await channels_view(call.message)


@admin.callback_query(F.data == "adm:chadd")
async def ch_add_start(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(AddChannel.chat)
    await call.message.answer(
        "📢 Kanal <code>@username</code> yoki ID sini yuboring (masalan <code>-1001234567890</code>).\n"
        "⚠️ Avval botni o'sha kanalga <b>admin</b> qiling!\nBekor qilish: /cancel"
    )


@admin.message(AddChannel.chat, F.text)
async def ch_add(m: Message, state: FSMContext, bot: Bot):
    raw = m.text.strip()
    if raw.lstrip("-").isdigit():
        ident = int(raw)
    else:
        ident = raw if raw.startswith("@") else f"@{raw}"
    try:
        chat = await bot.get_chat(ident)
        me = await bot.get_chat_member(chat.id, bot.id)
        if me.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR):
            await m.answer("⚠️ Bot bu kanalda admin emas. Avval admin qiling va qayta yuboring.")
            return
        if chat.username:
            link = f"https://t.me/{chat.username}"
        else:
            link = await bot.export_chat_invite_link(chat.id)
    except (TelegramBadRequest, TelegramForbiddenError) as e:
        await m.answer(f"❌ Kanal topilmadi yoki bot kira olmayapti.\n<code>{esc(e)}</code>")
        return
    await db.execute(
        "INSERT OR REPLACE INTO channels (chat_id, title, link) VALUES (?, ?, ?)",
        (chat.id, chat.title or str(chat.id), link),
    )
    await state.clear()
    await m.answer(f"✅ Kanal qo'shildi: <b>{esc(chat.title)}</b>", reply_markup=admin_menu())


# ---------- Statistika
@admin.callback_query(F.data == "adm:stats")
async def stats(call: CallbackQuery):
    q = db.fetchone
    users = (await q("SELECT COUNT(*) AS c FROM users"))["c"]
    active = (await q("SELECT COUNT(*) AS c FROM users WHERE active = 1"))["c"]
    today = (await q("SELECT COUNT(*) AS c FROM users WHERE date(joined_at) = date('now')"))["c"]
    movies = (await q("SELECT COUNT(*) AS c FROM movies"))["c"]
    views = (await q("SELECT COALESCE(SUM(views), 0) AS c FROM movies"))["c"]
    chans = (await q("SELECT COUNT(*) AS c FROM channels"))["c"]
    top = await db.fetchall("SELECT title, views FROM movies ORDER BY views DESC LIMIT 5")
    text = (
        "📊 <b>Statistika</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{users}</b> (faol: {active})\n"
        f"🆕 Bugun qo'shilgan: <b>{today}</b>\n"
        f"🎞 Kinolar: <b>{movies}</b>\n"
        f"👁 Jami ko'rishlar: <b>{views}</b>\n"
        f"📢 Kanallar: <b>{chans}</b>\n"
    )
    if top:
        text += "\n🔥 <b>Top kinolar:</b>\n" + "\n".join(
            f"{i}. {esc(t['title'])} - {t['views']}" for i, t in enumerate(top, 1)
        )
    await call.answer()
    await safe_edit(call.message, text, back_kb())


# ---------- Xabar yuborish
@admin.callback_query(F.data == "adm:bc")
async def bc_start(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Broadcast.msg)
    await call.message.answer(
        "📨 Barcha foydalanuvchilarga yuboriladigan xabarni yuboring "
        "(matn, rasm, video - istalgan).\nBekor qilish: /cancel"
    )


@admin.message(Broadcast.msg)
async def bc_msg(m: Message, state: FSMContext):
    await state.update_data(chat_id=m.chat.id, message_id=m.message_id)
    await state.set_state(Broadcast.confirm)
    total = (await db.fetchone("SELECT COUNT(*) AS c FROM users WHERE active = 1"))["c"]
    b = InlineKeyboardBuilder()
    b.button(text="✅ Yuborish", callback_data="bc:yes")
    b.button(text="❌ Bekor qilish", callback_data="bc:no")
    await m.answer(f"Xabar <b>{total}</b> ta foydalanuvchiga yuboriladi. Tasdiqlaysizmi?",
                   reply_markup=b.as_markup())


async def run_broadcast(bot: Bot, admin_id: int, from_chat: int, msg_id: int):
    users = await db.fetchall("SELECT id FROM users WHERE active = 1")
    ok = fail = 0
    for u in users:
        try:
            await bot.copy_message(u["id"], from_chat, msg_id)
            ok += 1
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
            try:
                await bot.copy_message(u["id"], from_chat, msg_id)
                ok += 1
            except Exception:
                fail += 1
        except TelegramForbiddenError:
            await db.execute("UPDATE users SET active = 0 WHERE id = ?", (u["id"],))
            fail += 1
        except Exception as e:
            log.warning("Broadcast xatosi %s: %s", u["id"], e)
            fail += 1
        await asyncio.sleep(0.05)
    await bot.send_message(admin_id, f"📨 Yuborish tugadi.\n✅ Yetkazildi: {ok}\n❌ Yetkazilmadi: {fail}")


@admin.callback_query(Broadcast.confirm, F.data.in_({"bc:yes", "bc:no"}))
async def bc_confirm(call: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await state.clear()
    await call.answer()
    if call.data == "bc:no":
        await safe_edit(call.message, "❌ Bekor qilindi.", back_kb())
        return
    await safe_edit(call.message, "⏳ Yuborish boshlandi. Tugagach xabar beraman.")
    task = asyncio.create_task(
        run_broadcast(bot, call.from_user.id, data["chat_id"], data["message_id"])
    )
    _tasks.add(task)
    task.add_done_callback(_tasks.discard)


# ============================================================ MAIN
async def main():
    global BOT_USERNAME
    if not BOT_TOKEN:
        sys.exit("❌ BOT_TOKEN topilmadi. .env faylini to'ldiring.")
    if not ADMINS:
        log.warning("ADMINS bo'sh! Admin panelga hech kim kira olmaydi.")

    await db.init()
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    BOT_USERNAME = (await bot.get_me()).username or ""

    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(admin)
    dp.include_router(user)

    @dp.error()
    async def on_error(event: ErrorEvent):
        log.exception("Kutilmagan xato: %s", event.exception)

    log.info("Bot ishga tushdi: @%s", BOT_USERNAME)
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await db.close()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("Bot to'xtatildi.")
