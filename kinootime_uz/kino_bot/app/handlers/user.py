import logging

from aiogram import Bot, F, Router
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandObject, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ChatMemberUpdated, InlineKeyboardMarkup, Message

from .. import keyboards as kb
from ..database import db
from ..services import content
from ..utils import ensure_sub, esc, get_unsubscribed, is_admin, safe_edit

log = logging.getLogger(__name__)
user = Router()

DEFAULT_WELCOME = (
    "👋 Assalomu alaykum, <b>{name}</b>!\n\n"
    "🎬 Kino <b>kodini</b> yuboring yoki <b>nomini</b> yozib qidiring.\n\n"
    "Quyidagi menyudan ham foydalanishingiz mumkin 👇"
)


async def send_welcome(bot: Bot, uid: int, name: str):
    tpl = db.settings.get("welcome") or DEFAULT_WELCOME
    text = tpl.replace("{name}", esc(name))
    try:
        await bot.send_message(uid, text, reply_markup=kb.main_menu(is_admin(uid)))
    except TelegramBadRequest:
        await bot.send_message(uid, DEFAULT_WELCOME.replace("{name}", esc(name)),
                               reply_markup=kb.main_menu(is_admin(uid)))


def _code_ok(s: str) -> bool:
    return s.isdigit() and len(s) <= 9


# ------------------------------------------------ bloklash holati
@user.my_chat_member(F.chat.type == "private")
async def on_my_chat_member(event: ChatMemberUpdated):
    gone = event.new_chat_member.status in (ChatMemberStatus.KICKED, ChatMemberStatus.LEFT)
    await db.execute("UPDATE users SET active=? WHERE id=?", (0 if gone else 1, event.from_user.id))


# ------------------------------------------------ buyruqlar
@user.message(CommandStart())
async def cmd_start(m: Message, command: CommandObject, state: FSMContext, bot: Bot):
    await state.clear()
    arg = (command.args or "").strip()[:20]
    movie_code = arg[1:] if arg[:1] == "m" and _code_ok(arg[1:]) else None
    payload = f"m{movie_code}" if movie_code else "0"
    if not await ensure_sub(bot, m.from_user.id, payload):
        return
    await send_welcome(bot, m.from_user.id, m.from_user.full_name)
    if movie_code:
        await content.show_movie(bot, m.from_user.id, int(movie_code))


@user.message(Command("help"))
@user.message(F.text == kb.BTN_HELP)
async def cmd_help(m: Message):
    await m.answer(
        "ℹ️ <b>Yordam</b>\n\n"
        "• Kino <b>kodini</b> yuboring - kino keladi.\n"
        "• Kino <b>nomini</b> yozing - qidiruv natijalari chiqadi.\n"
        "• 🗂 Kategoriyalar, 🔥 Top va 🆕 Yangi bo'limlaridan tanlang.\n"
        "• ❤️ tugmasi bilan kinoni sevimlilarga saqlang.\n"
        "• /start - botni qayta ishga tushirish."
    )


# ------------------------------------------------ menyu tugmalari
@user.message(F.text == kb.BTN_SEARCH)
async def menu_search(m: Message):
    await m.answer("🔎 Kino <b>nomini</b> yoki <b>kodini</b> yozing:")


@user.message(F.text == kb.BTN_CATS)
async def menu_cats(m: Message, bot: Bot):
    if not await ensure_sub(bot, m.from_user.id):
        return
    text, markup = await content.categories_view()
    await m.answer(text, reply_markup=markup)


async def _menu_list(m: Message, bot: Bot, kind: str):
    if not await ensure_sub(bot, m.from_user.id):
        return
    text, markup = await content.render_list(kind, 0, m.from_user.id, 0)
    await m.answer(text, reply_markup=markup)


@user.message(F.text == kb.BTN_TOP)
async def menu_top(m: Message, bot: Bot):
    await _menu_list(m, bot, "top")


@user.message(F.text == kb.BTN_NEW)
async def menu_new(m: Message, bot: Bot):
    await _menu_list(m, bot, "new")


@user.message(F.text == kb.BTN_FAV)
async def menu_fav(m: Message, bot: Bot):
    await _menu_list(m, bot, "fav")


# ------------------------------------------------ matn: kod yoki qidiruv
@user.message(StateFilter(None), F.text & ~F.text.startswith("/"))
async def on_text(m: Message, bot: Bot):
    text = m.text.strip()
    is_code = _code_ok(text)
    if not await ensure_sub(bot, m.from_user.id, f"m{text}" if is_code else "0"):
        return
    if is_code:
        await content.show_movie(bot, m.from_user.id, int(text))
        return
    if len(text) < 2:
        await m.answer("🔎 Qidirish uchun kamida 2 ta harf yozing.")
        return
    rows = await db.search_movies(text)
    if not rows:
        await m.answer("😕 Hech narsa topilmadi. Boshqacha yozib ko'ring yoki kino kodini yuboring.")
        return
    await m.answer(f"🔎 <b>Natijalar</b> ({len(rows)}):", reply_markup=kb.search_kb(rows))


# ------------------------------------------------ callbacklar
@user.callback_query(F.data == "close_message")
async def cb_close_message(call: CallbackQuery):
    try:
        await call.message.delete()
        await call.answer()
    except TelegramBadRequest:
        await call.answer("Xabarni o'chirib bo'lmadi.", show_alert=True)


@user.callback_query(F.data == "noop")
async def cb_noop(call: CallbackQuery):
    await call.answer()


@user.callback_query(F.data.startswith("check:"))
async def cb_check(call: CallbackQuery, bot: Bot):
    payload = call.data.split(":", 1)[1]
    if await get_unsubscribed(bot, call.from_user.id, use_cache=False):
        await call.answer("❌ Hali barcha kanallarga obuna bo'lmadingiz!", show_alert=True)
        return
    await call.answer("✅ Rahmat!")
    try:
        await call.message.delete()
    except TelegramBadRequest:
        pass
    await send_welcome(bot, call.from_user.id, call.from_user.full_name)
    if payload.startswith("m") and _code_ok(payload[1:]):
        await content.show_movie(bot, call.from_user.id, int(payload[1:]))


@user.callback_query(F.data.startswith("m:"))
async def cb_movie(call: CallbackQuery, bot: Bot):
    code = call.data.split(":")[1]
    await call.answer()
    if _code_ok(code) and await ensure_sub(bot, call.from_user.id, f"m{code}"):
        await content.show_movie(bot, call.from_user.id, int(code))


@user.callback_query(F.data.startswith("ep:"))
async def cb_episode(call: CallbackQuery, bot: Bot):
    _, code, number = call.data.split(":")
    await call.answer()
    if await ensure_sub(bot, call.from_user.id, f"m{code}"):
        await content.show_episode(bot, call.from_user.id, int(code), int(number))


@user.callback_query(F.data.startswith("epl:"))
async def cb_episode_page(call: CallbackQuery):
    _, code, page = call.data.split(":")
    code, page = int(code), int(page)
    movie = await db.get_movie(code)
    if not movie:
        await call.answer("Topilmadi", show_alert=True)
        return
    numbers = await db.episode_numbers(code)
    is_fav = await db.is_fav(call.from_user.id, code)
    from ..utils import deeplink
    markup = kb.episodes_kb(code, numbers, page, is_fav)
    await call.answer()
    try:
        await call.message.edit_reply_markup(reply_markup=markup)
    except TelegramBadRequest:
        pass


@user.callback_query(F.data.startswith("fav:"))
async def cb_fav(call: CallbackQuery):
    code = int(call.data.split(":")[1])
    if not await db.get_movie(code):
        await call.answer("Kino topilmadi", show_alert=True)
        return
    now_fav = await db.toggle_fav(call.from_user.id, code)
    await call.answer("❤️ Sevimlilarga qo'shildi" if now_fav else "💔 Sevimlilardan olindi")
    markup = call.message.reply_markup
    if not markup:
        return
    rows = []
    for row in markup.inline_keyboard:
        rows.append([
            btn.model_copy(update={"text": kb.fav_text(now_fav)}) if btn.callback_data == call.data else btn
            for btn in row
        ])
    try:
        await call.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    except TelegramBadRequest:
        pass


@user.callback_query(F.data == "cats")
async def cb_cats(call: CallbackQuery):
    text, markup = await content.categories_view()
    await call.answer()
    await safe_edit(call.message, text, markup)


@user.callback_query(F.data.startswith("lst:"))
async def cb_list(call: CallbackQuery, bot: Bot):
    _, kind, arg, page = call.data.split(":")
    await call.answer()
    if not await ensure_sub(bot, call.from_user.id):
        return
    text, markup = await content.render_list(kind, int(arg), call.from_user.id, int(page))
    await safe_edit(call.message, text, markup)
