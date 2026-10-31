"""Admin: kanallar, statistika, foydalanuvchilar, xabar yuborish, sozlamalar, adminlar, zaxira."""
import asyncio
import logging

from aiogram import Bot, F, Router
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from .. import keyboards as kb
from ..config import cfg
from ..database import db
from ..services.backup import make_backup, send_backup
from ..services.broadcast import run_broadcast
from ..states import AddAdmin, AddChannel, Broadcast, SetWelcome, UserAction
from ..utils import IsAdmin, esc, is_admin, is_super, safe_edit

log = logging.getLogger(__name__)
system = Router()
system.message.filter(IsAdmin())
system.callback_query.filter(IsAdmin())

TEXT = F.text & ~F.text.startswith("/")
_tasks: set[asyncio.Task] = set()


# ================================================== KANALLAR
async def channels_view(message: Message):
    rows = await db.fetchall("SELECT * FROM channels")
    buttons = [[(f"🗑 {r['title']}", f"a:chdel:{r['chat_id']}")] for r in rows]
    buttons.append([("➕ Kanal qo'shish", "a:chadd")])
    buttons.append([("🏠 Admin panel", "a:back")])
    text = ("📢 <b>Majburiy obuna kanallari</b>\n\n"
            + ("O'chirish uchun kanal tugmasini bosing." if rows else "Hozircha yo'q."))
    await safe_edit(message, text, kb.grid(buttons))


@system.callback_query(F.data == "a:ch")
async def ch_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer()
    await channels_view(call.message)


@system.callback_query(F.data.startswith("a:chdel:"))
async def ch_del(call: CallbackQuery):
    await db.execute("DELETE FROM channels WHERE chat_id=?", (int(call.data.split(":")[2]),))
    await call.answer("🗑 O'chirildi")
    await channels_view(call.message)


@system.callback_query(F.data == "a:chadd")
async def ch_add_start(call: CallbackQuery, state: FSMContext):
    await state.set_state(AddChannel.chat)
    await call.answer()
    await call.message.answer(
        "📢 Kanal <code>@username</code> yoki ID sini yuboring (masalan <code>-1001234567890</code>).\n"
        "⚠️ Avval botni o'sha kanalga <b>admin</b> qiling!\nBekor qilish: /cancel")


@system.message(AddChannel.chat, TEXT)
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
        link = f"https://t.me/{chat.username}" if chat.username else await bot.export_chat_invite_link(chat.id)
    except (TelegramBadRequest, TelegramForbiddenError) as e:
        await m.answer(f"❌ Kanal topilmadi yoki bot kira olmayapti.\n<code>{esc(e)}</code>")
        return
    await db.execute("INSERT OR REPLACE INTO channels (chat_id, title, link) VALUES (?, ?, ?)",
                     (chat.id, chat.title or str(chat.id), link))
    await state.clear()
    await m.answer(f"✅ Kanal qo'shildi: <b>{esc(chat.title)}</b>", reply_markup=kb.admin_menu())


# ================================================== STATISTIKA
@system.callback_query(F.data == "a:stats")
async def stats(call: CallbackQuery):
    s = db.scalar
    users = await s("SELECT COUNT(*) FROM users")
    active = await s("SELECT COUNT(*) FROM users WHERE active=1")
    banned = await s("SELECT COUNT(*) FROM users WHERE banned=1")
    today = await s("SELECT COUNT(*) FROM users WHERE date(joined_at)=date('now')")
    week = await s("SELECT COUNT(*) FROM users WHERE joined_at >= datetime('now','-7 days')")
    movies = await s("SELECT COUNT(*) FROM movies WHERE kind='movie'")
    series = await s("SELECT COUNT(*) FROM movies WHERE kind='series'")
    eps = await s("SELECT COUNT(*) FROM episodes")
    views = await s("SELECT COALESCE(SUM(views),0) FROM movies")
    favs = await s("SELECT COUNT(*) FROM favorites")
    chans = await s("SELECT COUNT(*) FROM channels")
    top = await db.fetchall("SELECT title, views FROM movies ORDER BY views DESC LIMIT 5")
    text = (
        "📊 <b>Statistika</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{users}</b> (faol: {active}, bloklangan: {banned})\n"
        f"🆕 Bugun: <b>{today}</b> | 7 kunda: <b>{week}</b>\n"
        f"🎬 Kinolar: <b>{movies}</b> | 📺 Seriallar: <b>{series}</b> ({eps} qism)\n"
        f"👁 Jami ko'rishlar: <b>{views}</b>\n"
        f"❤️ Sevimlilar: <b>{favs}</b>\n"
        f"📢 Kanallar: <b>{chans}</b>\n"
    )
    if top:
        text += "\n🔥 <b>Top 5:</b>\n" + "\n".join(
            f"{i}. {esc(t['title'])} - {t['views']}" for i, t in enumerate(top, 1))
    await call.answer()
    await safe_edit(call.message, text, kb.back_admin())


# ================================================== FOYDALANUVCHILAR
@system.callback_query(F.data == "a:users")
async def users_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    total = await db.scalar("SELECT COUNT(*) FROM users")
    await call.answer()
    await safe_edit(call.message, f"👥 <b>Foydalanuvchilar</b>: {total}", kb.grid([
        [("🔍 Ma'lumot", "a:u:info"), ("🚫 Ban", "a:u:ban")],
        [("✅ Bandan chiqarish", "a:u:unban")],
        [("🏠 Admin panel", "a:back")],
    ]))


@system.callback_query(F.data.regexp(r"^a:u:(info|ban|unban)$"))
async def users_action_start(call: CallbackQuery, state: FSMContext):
    action = call.data.split(":")[2]
    await state.set_state(UserAction.target)
    await state.update_data(action=action)
    await call.answer()
    await call.message.answer("👤 Foydalanuvchi Telegram ID sini yuboring.\nBekor qilish: /cancel")


@system.message(UserAction.target, TEXT)
async def users_action(m: Message, state: FSMContext):
    s = m.text.strip()
    if not s.isdigit() or len(s) > 15:
        await m.answer("⚠️ Faqat raqamli ID yuboring.")
        return
    uid = int(s)
    action = (await state.get_data())["action"]
    await state.clear()
    if action == "info":
        u = await db.fetchone("SELECT * FROM users WHERE id=?", (uid,))
        if not u:
            await m.answer("❌ Bunday foydalanuvchi bazada yo'q.", reply_markup=kb.admin_menu())
            return
        favs = await db.scalar("SELECT COUNT(*) FROM favorites WHERE user_id=?", (uid,))
        await m.answer(
            f"👤 <b>{esc(u['full_name'])}</b>\n🆔 <code>{uid}</code>\n"
            f"🔗 {('@' + esc(u['username'])) if u['username'] else '-'}\n"
            f"📅 Qo'shilgan: {u['joined_at']}\n🕒 Oxirgi faollik: {u['last_seen']}\n"
            f"Faol: {'ha' if u['active'] else 'yo`q'} | Ban: {'ha' if u['banned'] else 'yo`q'}\n"
            f"❤️ Sevimlilar: {favs}", reply_markup=kb.admin_menu())
        return
    if action == "ban":
        if is_admin(uid):
            await m.answer("⚠️ Adminni ban qilib bo'lmaydi.", reply_markup=kb.admin_menu())
            return
        await db.set_banned(uid, True)
        await m.answer(f"🚫 <code>{uid}</code> bloklandi.", reply_markup=kb.admin_menu())
    else:
        await db.set_banned(uid, False)
        await m.answer(f"✅ <code>{uid}</code> blokdan chiqarildi.", reply_markup=kb.admin_menu())


# ================================================== XABAR YUBORISH
@system.callback_query(F.data == "a:bc")
async def bc_start(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(Broadcast.msg)
    await call.answer()
    await call.message.answer(
        "📨 Barcha foydalanuvchilarga yuboriladigan xabarni yuboring "
        "(matn, rasm, video - istalgan).\nBekor qilish: /cancel")


@system.message(Broadcast.msg)
async def bc_msg(m: Message, state: FSMContext):
    await state.update_data(chat_id=m.chat.id, message_id=m.message_id)
    await state.set_state(Broadcast.confirm)
    total = await db.scalar("SELECT COUNT(*) FROM users WHERE active=1 AND banned=0")
    await m.answer(f"Xabar <b>{total}</b> ta foydalanuvchiga yuboriladi. Tasdiqlaysizmi?",
                   reply_markup=kb.grid([[("✅ Yuborish", "bc:yes"), ("❌ Bekor", "bc:no")]]))


@system.callback_query(Broadcast.confirm, F.data.in_({"bc:yes", "bc:no"}))
async def bc_confirm(call: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await state.clear()
    await call.answer()
    if call.data == "bc:no":
        await safe_edit(call.message, "❌ Bekor qilindi.", kb.back_admin())
        return
    await safe_edit(call.message, "⏳ Yuborish boshlandi...")
    task = asyncio.create_task(
        run_broadcast(bot, call.from_user.id, call.message, data["chat_id"], data["message_id"]))
    _tasks.add(task)
    task.add_done_callback(_tasks.discard)


# ================================================== SOZLAMALAR
def settings_markup(uid: int):
    protect = db.settings.get("protect") == "1"
    rows = [
        [(f"🔒 Himoyalangan kontent: {'YOQIQ' if protect else 'o`chiq'}", "a:set:protect")],
        [("👋 Salomlashuv matni", "a:set:welcome")],
    ]
    if is_super(uid):
        rows.append([("👮 Adminlar", "a:admins"), ("💾 Zaxira nusxa", "a:backup")])
    rows.append([("🏠 Admin panel", "a:back")])
    return kb.grid(rows)


@system.callback_query(F.data == "a:settings")
async def settings_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer()
    await safe_edit(call.message, "⚙️ <b>Sozlamalar</b>", settings_markup(call.from_user.id))


@system.callback_query(F.data == "a:set:protect")
async def set_protect(call: CallbackQuery):
    new = "0" if db.settings.get("protect") == "1" else "1"
    await db.set_setting("protect", new)
    await call.answer("Saqlandi")
    await safe_edit(call.message, "⚙️ <b>Sozlamalar</b>", settings_markup(call.from_user.id))


@system.callback_query(F.data == "a:set:welcome")
async def set_welcome_start(call: CallbackQuery, state: FSMContext):
    await state.set_state(SetWelcome.text)
    await call.answer()
    await call.message.answer(
        "👋 Yangi salomlashuv matnini yuboring. <code>{name}</code> o'rniga foydalanuvchi ismi qo'yiladi. "
        "HTML (<code>&lt;b&gt;</code>, <code>&lt;i&gt;</code>) ishlaydi.\n"
        "<code>-</code> yuborsangiz standart matn tiklanadi.\nBekor qilish: /cancel")


@system.message(SetWelcome.text, TEXT)
async def set_welcome(m: Message, state: FSMContext):
    value = m.text.strip()
    if value == "-":
        await db.del_setting("welcome")
        note = "✅ Standart matn tiklandi."
    else:
        await db.set_setting("welcome", value[:1500])
        note = "✅ Salomlashuv matni saqlandi."
    await state.clear()
    await m.answer(note, reply_markup=kb.admin_menu())


# ================================================== ADMINLAR (faqat bosh admin)
async def admins_view(message: Message):
    lines = [f"⭐ <code>{a}</code> (bosh admin)" for a in cfg.SUPER_ADMINS]
    lines += [f"👮 <code>{a}</code>" for a in sorted(db.admin_ids - set(cfg.SUPER_ADMINS))]
    buttons = [[(f"🗑 {a}", f"a:admdel:{a}")] for a in sorted(db.admin_ids - set(cfg.SUPER_ADMINS))]
    buttons.append([("➕ Admin qo'shish", "a:admadd")])
    buttons.append([("⬅️ Sozlamalar", "a:settings")])
    await safe_edit(message, "👮 <b>Adminlar</b>\n\n" + "\n".join(lines), kb.grid(buttons))


@system.callback_query(F.data == "a:admins")
async def admins_menu(call: CallbackQuery):
    if not is_super(call.from_user.id):
        await call.answer("Faqat bosh admin uchun", show_alert=True)
        return
    await call.answer()
    await admins_view(call.message)


@system.callback_query(F.data.startswith("a:admdel:"))
async def admin_del(call: CallbackQuery):
    if not is_super(call.from_user.id):
        await call.answer("Faqat bosh admin uchun", show_alert=True)
        return
    await db.remove_admin(int(call.data.split(":")[2]))
    await call.answer("🗑 O'chirildi")
    await admins_view(call.message)


@system.callback_query(F.data == "a:admadd")
async def admin_add_start(call: CallbackQuery, state: FSMContext):
    if not is_super(call.from_user.id):
        await call.answer("Faqat bosh admin uchun", show_alert=True)
        return
    await state.set_state(AddAdmin.uid)
    await call.answer()
    await call.message.answer("👮 Yangi adminning Telegram ID sini yuboring.\nBekor qilish: /cancel")


@system.message(AddAdmin.uid, TEXT)
async def admin_add(m: Message, state: FSMContext):
    s = m.text.strip()
    if not is_super(m.from_user.id):
        await state.clear()
        return
    if not s.isdigit() or len(s) > 15:
        await m.answer("⚠️ Faqat raqamli ID yuboring.")
        return
    await db.add_admin(int(s))
    await state.clear()
    await m.answer(f"✅ <code>{s}</code> admin qilindi.", reply_markup=kb.admin_menu())


# ================================================== ZAXIRA (faqat bosh admin)
@system.callback_query(F.data == "a:backup")
async def backup_now(call: CallbackQuery, bot: Bot):
    if not is_super(call.from_user.id):
        await call.answer("Faqat bosh admin uchun", show_alert=True)
        return
    await call.answer("⏳ Tayyorlanmoqda...")
    try:
        path = await make_backup()
        await send_backup(bot, call.from_user.id, path)
    except Exception as e:
        log.exception("Zaxira xatosi")
        await call.message.answer(f"❌ Zaxira olinmadi: <code>{esc(e)}</code>")
