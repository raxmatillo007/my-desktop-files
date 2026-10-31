"""Admin: kino/serial qo'shish, boshqarish, qismlar, kategoriyalar."""
import logging
import sqlite3

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from .. import keyboards as kb
from ..database import db
from ..services.captions import media_title_desc
from ..states import (AddCategory, AddEpisode, AddMovie, DelEpisode, EditField, Manage, QuickAdd)
from ..utils import IsAdmin, deeplink, esc, is_admin, safe_edit

log = logging.getLogger(__name__)
content = Router()
content.message.filter(IsAdmin())
content.callback_query.filter(IsAdmin())

TEXT = F.text & ~F.text.startswith("/")
FILE = F.video | F.document


@content.message(Command("edit"))
async def edit_bot_caption(m: Message, command: CommandObject):
    if not m.from_user or not is_admin(m.from_user.id):
        await m.answer("⛔ Bu buyruq faqat adminlar uchun.")
        return

    target = m.reply_to_message
    new_caption = (command.args or "").strip()
    if not target:
        await m.answer("⚠️ Tahrirlamoqchi bo'lgan kino xabariga reply qilib /edit yangi matn yuboring.")
        return
    if not new_caption:
        await m.answer("⚠️ Yangi caption matnini kiriting: /edit yangi matn")
        return
    if len(new_caption) > 1024:
        await m.answer("⚠️ Caption 1024 belgidan oshmasligi kerak.")
        return
    if not (target.photo or target.video) or target.caption is None:
        await m.answer("⚠️ Reply qilingan xabar caption'li rasm yoki video bo'lishi kerak.")
        return

    bot_user = await m.bot.get_me()
    if not target.from_user or target.from_user.id != bot_user.id:
        await m.answer("⚠️ Faqat bot yuborgan xabar caption'ini tahrirlash mumkin.")
        return

    try:
        await m.bot.edit_message_caption(
            chat_id=target.chat.id,
            message_id=target.message_id,
            caption=new_caption,
            reply_markup=target.reply_markup,
            parse_mode=None,
        )
    except TelegramBadRequest:
        log.exception("Bot xabari caption'ini tahrirlash amalga oshmadi")
        await m.answer("❌ Caption'ni tahrirlab bo'lmadi.")
        return

    await m.answer("✅ Kino caption'i yangilandi.")


@content.message(Command("edit_code"))
async def edit_movie_code(m: Message, command: CommandObject):
    if not m.from_user or not is_admin(m.from_user.id):
        await m.answer("⛔ Bu buyruq faqat adminlar uchun.")
        return

    args = (command.args or "").split()
    if len(args) != 2 or any(not value.isdecimal() or len(value) > 19 for value in args):
        await m.answer("Foydalanish: <code>/edit_code eski_kod yangi_kod</code>")
        return

    old_code, new_code = map(int, args)
    if new_code > 9_223_372_036_854_775_807 or old_code > 9_223_372_036_854_775_807:
        await m.answer("⚠️ Kod SQLite qo'llab-quvvatlaydigan chegaradan katta.")
        return

    try:
        await db.reassign_movie_code(old_code, new_code)
    except LookupError as exc:
        await m.answer(f"❌ {esc(exc)}")
        return
    except ValueError as exc:
        await m.answer(f"⚠️ {esc(exc)}")
        return
    except Exception:
        log.exception("Kino kodi almashtirilmadi: %s -> %s", old_code, new_code)
        await m.answer("❌ Kodni almashtirishda kutilmagan xatolik yuz berdi.")
        return

    await m.answer(f"✅ Kino kodi <code>{old_code}</code> dan <code>{new_code}</code> ga o'zgartirildi.")


def _file_of(m: Message):
    """(file_id, turi, unique_id)"""
    if m.video:
        return m.video.file_id, "video", m.video.file_unique_id
    if m.document:
        return m.document.file_id, "document", m.document.file_unique_id
    return None, None, None


# ================================================== QO'SHISH
@content.callback_query(F.data == "a:add")
async def add_choose(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer()
    await safe_edit(call.message, "Nima qo'shamiz?", kb.grid([
        [("🎬 Kino", "a:addk:movie"), ("📺 Serial", "a:addk:series")],
        [("🏠 Admin panel", "a:back")],
    ]))


@content.callback_query(F.data.startswith("a:addk:"))
async def add_kind(call: CallbackQuery, state: FSMContext):
    kind = call.data.split(":")[2]
    await state.clear()
    await state.update_data(kind=kind)
    await call.answer()
    if kind == "movie":
        await state.set_state(AddMovie.file)
        await call.message.answer("🎥 Kino faylini (video yoki hujjat) yuboring.\nBekor qilish: /cancel")
    else:
        await state.set_state(AddMovie.title)
        await call.message.answer("✏️ Serial nomini yuboring.\nBekor qilish: /cancel")


@content.message(AddMovie.file, FILE)
async def add_file(m: Message, state: FSMContext):
    file_id, file_type, uid = _file_of(m)
    await state.update_data(file_id=file_id, file_type=file_type, unique_id=uid)
    dup = await db.find_by_unique(uid)
    if dup:
        await m.answer(f"ℹ️ Diqqat: bu video bazada allaqachon bor (kod <code>{dup['code']}</code>: "
                       f"{esc(dup['title'])}). Baribir davom etamiz.")
    await state.set_state(AddMovie.title)
    await m.answer("✏️ Kino nomini yuboring:")


@content.message(AddMovie.file)
async def add_file_bad(m: Message):
    await m.answer("⚠️ Iltimos, video yoki hujjat yuboring. Bekor qilish: /cancel")


@content.message(AddMovie.title, TEXT)
async def add_title(m: Message, state: FSMContext):
    title = m.text.strip()
    if len(title) > 200:
        await m.answer("⚠️ Nom 200 belgidan oshmasligi kerak.")
        return
    await state.update_data(title=title)
    await state.set_state(AddMovie.desc)
    await m.answer("📝 Tavsif yuboring (kerak bo'lmasa <code>-</code> yuboring):")


@content.message(AddMovie.desc, TEXT)
async def add_desc(m: Message, state: FSMContext):
    desc = "" if m.text.strip() == "-" else m.text.strip()[:600]
    await state.update_data(desc=desc)
    cats = await db.fetchall("SELECT id, name FROM categories ORDER BY name")
    if not cats:
        await save_new(m, state, None)
        return
    await state.set_state(AddMovie.category)
    rows = [[(c["name"], f"a:addc:{c['id']}")] for c in cats]
    rows.append([("⏭ Kategoriyasiz", "a:addc:0")])
    await m.answer("🗂 Kategoriyani tanlang:", reply_markup=kb.grid(rows))


@content.callback_query(AddMovie.category, F.data.startswith("a:addc:"))
async def add_category(call: CallbackQuery, state: FSMContext):
    cid = int(call.data.split(":")[2])
    await call.answer()
    await save_new(call.message, state, cid or None)


async def save_new(target: Message, state: FSMContext, cid):
    data = await state.get_data()
    code = await db.add_movie(
        title=data["title"], description=data.get("desc", ""), category_id=cid,
        kind=data["kind"], file_id=data.get("file_id"), file_type=data.get("file_type"),
        unique_id=data.get("unique_id"),
    )
    if data["kind"] == "series":
        await state.set_state(AddEpisode.files)
        await state.set_data({"code": code})
        await target.answer(
            f"✅ Serial yaratildi. Kod: <code>{code}</code>\n\n"
            "📺 Endi qismlarni <b>ketma-ket</b> yuboring (1-qism, 2-qism, ...). "
            "Tugagach «✅ Tugatish» ni bosing.",
            reply_markup=kb.grid([[("✅ Tugatish", "a:epdone")]]),
        )
    else:
        await state.clear()
        await target.answer(
            f"✅ Kino qo'shildi!\n\n🎬 <b>{esc(data['title'])}</b>\n🔢 Kod: <code>{code}</code>\n"
            f"🔗 {deeplink(code)}",
            reply_markup=kb.admin_menu(),
        )


# ================================================== QISMLAR
@content.message(AddEpisode.files, FILE)
async def ep_add(m: Message, state: FSMContext):
    code = (await state.get_data())["code"]
    file_id, file_type, _ = _file_of(m)
    number = await db.add_episode(code, file_id, file_type)
    await m.answer(f"✅ {number}-qism qo'shildi. Keyingisini yuboring yoki tugating.",
                   reply_markup=kb.grid([[("✅ Tugatish", "a:epdone")]]))


@content.message(AddEpisode.files)
async def ep_bad(m: Message):
    await m.answer("⚠️ Video yoki hujjat yuboring, yoki «✅ Tugatish» ni bosing.")


@content.callback_query(F.data == "a:epdone")
async def ep_done(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    await call.answer("Tayyor")
    code = data.get("code")
    extra = ""
    if code:
        n = len(await db.episode_numbers(code))
        extra = f"\n📺 Qismlar soni: {n}\n🔗 {deeplink(code)}"
    await call.message.answer(f"✅ Saqlandi.{extra}", reply_markup=kb.admin_menu())


# ================================================== BOSHQARISH
async def render_card(code: int):
    m = await db.get_movie(code)
    if not m:
        return None
    is_series = m["kind"] == "series"
    text = (f"🛠 <b>{esc(m['title'])}</b>\n"
            f"Turi: {'📺 Serial' if is_series else '🎬 Kino'}\n"
            f"🗂 Kategoriya: {esc(m['category'] or '-')}\n"
            f"👁 Ko'rishlar: {m['views']}\n🔢 Kod: <code>{code}</code>\n")
    if is_series:
        text += f"📺 Qismlar: {len(await db.episode_numbers(code))}\n"
    text += f"🔗 {deeplink(code)}\n"
    if m["description"]:
        text += f"\n📝 {esc(m['description'][:300])}"
    rows = [
        [("✏️ Nom", f"a:e:title:{code}"), ("📝 Tavsif", f"a:e:desc:{code}")],
        [("🗂 Kategoriya", f"a:e:cat:{code}")],
    ]
    if is_series:
        rows.append([("➕ Qism qo'shish", f"a:e:eps:{code}"), ("🗑 Qism o'chirish", f"a:e:epdel:{code}")])
    else:
        rows.append([("🎞 Faylni almashtirish", f"a:e:file:{code}")])
    rows.append([("🗑 O'chirish", f"a:e:del:{code}")])
    rows.append([("🏠 Admin panel", "a:back")])
    return text, kb.grid(rows)


@content.callback_query(F.data == "a:manage")
async def manage_start(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(Manage.code)
    await call.answer()
    await call.message.answer("🔧 Kino/serial <b>kodini</b> yuboring.\nBekor qilish: /cancel")


@content.message(Manage.code, TEXT)
async def manage_code(m: Message, state: FSMContext):
    s = m.text.strip()
    if not s.isdigit() or len(s) > 9:
        await m.answer("⚠️ Faqat raqam yuboring.")
        return
    card = await render_card(int(s))
    if not card:
        await m.answer("❌ Bunday kodli kino yo'q.")
        return
    await state.clear()
    await m.answer(card[0], reply_markup=card[1])


@content.callback_query(F.data.startswith("a:card:"))
async def show_card(call: CallbackQuery, state: FSMContext):
    await state.clear()
    card = await render_card(int(call.data.split(":")[2]))
    await call.answer()
    if card:
        await safe_edit(call.message, card[0], card[1])


@content.callback_query(F.data.regexp(r"^a:e:(title|desc|file):\d+$"))
async def edit_start(call: CallbackQuery, state: FSMContext):
    _, _, field, code = call.data.split(":")
    await state.clear()
    await state.set_state(EditField.value)
    await state.update_data(code=int(code), field=field)
    prompts = {
        "title": "✏️ Yangi nomni yuboring:",
        "desc": "📝 Yangi tavsifni yuboring (<code>-</code> = tozalash):",
        "file": "🎞 Yangi faylni (video yoki hujjat) yuboring:",
    }
    await call.answer()
    await call.message.answer(prompts[field] + "\nBekor qilish: /cancel")


@content.message(EditField.value, FILE | TEXT)
async def edit_value(m: Message, state: FSMContext):
    data = await state.get_data()
    code, field = data["code"], data["field"]
    if field == "file":
        file_id, file_type, uid = _file_of(m)
        if not file_id:
            await m.answer("⚠️ Video yoki hujjat yuboring.")
            return
        await db.execute("UPDATE movies SET file_id=?, file_type=?, unique_id=? WHERE code=?",
                         (file_id, file_type, uid, code))
    else:
        if not m.text:
            await m.answer("⚠️ Matn yuboring.")
            return
        value = m.text.strip()
        if field == "title":
            if len(value) > 200:
                await m.answer("⚠️ Nom 200 belgidan oshmasligi kerak.")
                return
            await db.execute("UPDATE movies SET title=?, search=? WHERE code=?",
                             (value, value.lower(), code))
        else:
            await db.execute("UPDATE movies SET description=? WHERE code=?",
                             ("" if value == "-" else value[:600], code))
    await state.clear()
    card = await render_card(code)
    await m.answer("✅ Yangilandi.")
    if card:
        await m.answer(card[0], reply_markup=card[1])


@content.callback_query(F.data.regexp(r"^a:e:cat:\d+$"))
async def edit_cat(call: CallbackQuery):
    code = int(call.data.split(":")[3])
    cats = await db.fetchall("SELECT id, name FROM categories ORDER BY name")
    rows = [[(c["name"], f"a:e:setcat:{code}:{c['id']}")] for c in cats]
    rows.append([("⏭ Kategoriyasiz", f"a:e:setcat:{code}:0")])
    rows.append([("⬅️ Orqaga", f"a:card:{code}")])
    await call.answer()
    await safe_edit(call.message, "🗂 Kategoriyani tanlang:", kb.grid(rows))


@content.callback_query(F.data.startswith("a:e:setcat:"))
async def edit_setcat(call: CallbackQuery):
    _, _, _, code, cid = call.data.split(":")
    await db.execute("UPDATE movies SET category_id=? WHERE code=?", (int(cid) or None, int(code)))
    await call.answer("✅ Saqlandi")
    card = await render_card(int(code))
    if card:
        await safe_edit(call.message, card[0], card[1])


@content.callback_query(F.data.regexp(r"^a:e:eps:\d+$"))
async def edit_eps(call: CallbackQuery, state: FSMContext):
    code = int(call.data.split(":")[3])
    await state.clear()
    await state.set_state(AddEpisode.files)
    await state.set_data({"code": code})
    await call.answer()
    await call.message.answer(
        "📺 Yangi qismlarni ketma-ket yuboring. Tugagach «✅ Tugatish» ni bosing.",
        reply_markup=kb.grid([[("✅ Tugatish", "a:epdone")]]))


@content.callback_query(F.data.regexp(r"^a:e:epdel:\d+$"))
async def edit_epdel(call: CallbackQuery, state: FSMContext):
    code = int(call.data.split(":")[3])
    nums = await db.episode_numbers(code)
    if not nums:
        await call.answer("Qismlar yo'q", show_alert=True)
        return
    await state.clear()
    await state.set_state(DelEpisode.number)
    await state.update_data(code=code)
    await call.answer()
    await call.message.answer(
        f"🗑 O'chiriladigan qism raqamini yuboring (mavjud: {nums[0]}-{nums[-1]}).\nBekor qilish: /cancel")


@content.message(DelEpisode.number, TEXT)
async def epdel_number(m: Message, state: FSMContext):
    s = m.text.strip()
    if not s.isdigit() or len(s) > 6:
        await m.answer("⚠️ Faqat raqam yuboring.")
        return
    code = (await state.get_data())["code"]
    if not await db.delete_episode(code, int(s)):
        await m.answer("❌ Bunday qism yo'q.")
        return
    await state.clear()
    card = await render_card(code)
    await m.answer(f"✅ {s}-qism o'chirildi.")
    if card:
        await m.answer(card[0], reply_markup=card[1])


@content.callback_query(F.data.regexp(r"^a:e:del:\d+$"))
async def edit_del(call: CallbackQuery):
    code = int(call.data.split(":")[3])
    await call.answer()
    await safe_edit(call.message, f"⚠️ <code>{code}</code> kodli kontent butunlay o'chiriladi. Ishonchingiz komilmi?",
                    kb.grid([[("✅ Ha, o'chirish", f"a:e:delok:{code}"), ("❌ Yo'q", f"a:card:{code}")]]))


@content.callback_query(F.data.startswith("a:e:delok:"))
async def edit_delok(call: CallbackQuery):
    await db.delete_movie(int(call.data.split(":")[3]))
    await call.answer("🗑 O'chirildi")
    await safe_edit(call.message, "✅ O'chirildi.", kb.back_admin())


# ================================================== RO'YXAT
@content.callback_query(F.data.startswith("a:list:"))
async def admin_list(call: CallbackQuery):
    page = max(int(call.data.split(":")[2]), 0)
    per = 10
    total = await db.scalar("SELECT COUNT(*) FROM movies")
    rows = await db.fetchall(
        "SELECT code, title, kind, views FROM movies ORDER BY code DESC LIMIT ? OFFSET ?",
        (per, page * per))
    await call.answer()
    if not rows:
        await safe_edit(call.message, "📭 Hozircha kontent yo'q.", kb.back_admin())
        return
    pages = (total + per - 1) // per
    text = f"🎞 <b>Kontent</b> ({page + 1}/{pages}), jami: {total}\n\n" + "\n".join(
        f"<code>{r['code']}</code> {'📺' if r['kind'] == 'series' else '🎬'} {esc(r['title'])} (👁 {r['views']})"
        for r in rows)
    nav = []
    if page > 0:
        nav.append(("⬅️", f"a:list:{page - 1}"))
    if (page + 1) * per < total:
        nav.append(("➡️", f"a:list:{page + 1}"))
    markup = kb.grid(([nav] if nav else []) + [[("🏠 Admin panel", "a:back")]])
    await safe_edit(call.message, text, markup)


# ================================================== KATEGORIYALAR
async def cats_view(message: Message):
    rows = await db.fetchall(
        "SELECT c.id, c.name, (SELECT COUNT(*) FROM movies m WHERE m.category_id=c.id) AS n "
        "FROM categories c ORDER BY c.name")
    buttons = [[(f"🗑 {r['name']} ({r['n']})", f"a:catdel:{r['id']}")] for r in rows]
    buttons.append([("➕ Kategoriya qo'shish", "a:cataddb")])
    buttons.append([("🏠 Admin panel", "a:back")])
    text = "🗂 <b>Kategoriyalar</b>\n\n" + ("O'chirish uchun tugmani bosing." if rows else "Hozircha yo'q.")
    await safe_edit(message, text, kb.grid(buttons))


@content.callback_query(F.data == "a:cats")
async def cats_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer()
    await cats_view(call.message)


@content.callback_query(F.data.startswith("a:catdel:"))
async def cat_del(call: CallbackQuery):
    cid = int(call.data.split(":")[2])
    await db.transaction([
        ("UPDATE movies SET category_id=NULL WHERE category_id=?", (cid,)),
        ("UPDATE storage_channels SET category_id=NULL WHERE category_id=?", (cid,)),
        ("DELETE FROM categories WHERE id=?", (cid,)),
    ])
    await db.load_storage()
    await call.answer("🗑 O'chirildi")
    await cats_view(call.message)


@content.callback_query(F.data == "a:cataddb")
async def cat_add_start(call: CallbackQuery, state: FSMContext):
    await state.set_state(AddCategory.name)
    await call.answer()
    await call.message.answer("🗂 Kategoriya nomini yuboring (masalan: Jangari).\nBekor qilish: /cancel")


@content.message(AddCategory.name, TEXT)
async def cat_add(m: Message, state: FSMContext):
    name = m.text.strip()
    if len(name) > 40:
        await m.answer("⚠️ Nom 40 belgidan oshmasligi kerak.")
        return
    try:
        await db.execute("INSERT INTO categories (name) VALUES (?)", (name,))
    except sqlite3.IntegrityError:
        await m.answer("⚠️ Bunday kategoriya allaqachon bor.")
        return
    await state.clear()
    await m.answer(f"✅ Kategoriya qo'shildi: <b>{esc(name)}</b>", reply_markup=kb.admin_menu())


# ================================================== TEZKOR QO'SHISH
def parse_media(m: Message):
    """Izohdan toza sarlavha va tavsif (reklama, havola, #teg, emoji olib tashlanadi)."""
    media = m.video or m.document
    return media_title_desc(m.caption, getattr(media, "file_name", None))


async def _try_answer(m: Message, text: str):
    try:
        await m.answer(text)
    except Exception:  # Telegram tezlik cheklovi: kino baribir saqlangan
        log.debug("Javob yuborilmadi: %s", text[:40])


async def _quick_begin(target: Message, state: FSMContext, cid):
    await state.set_state(QuickAdd.files)
    await state.set_data({"cid": cid, "n": 0, "dups": 0, "first": 0, "last": 0})
    await target.answer(
        "⚡ <b>Tezkor rejim yoqildi.</b>\n\n"
        "Videolarni yuboring yoki kanaldan <b>bir nechtasini belgilab forward qiling</b>. "
        "Videoning <b>izohi</b> kino nomi bo'ladi (1-qator = nom, qolgani = tavsif). "
        "Reklama, havola, @nom va #teglar avtomatik olib tashlanadi. "
        "Bazada bor video qayta qo'shilmaydi.\n\nTugagach «✅ Tugatish» ni bosing.",
        reply_markup=kb.grid([[("✅ Tugatish", "a:quickdone")]]))


@content.callback_query(F.data == "a:quick")
async def quick_start(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer()
    cats = await db.fetchall("SELECT id, name FROM categories ORDER BY name")
    if not cats:
        await _quick_begin(call.message, state, None)
        return
    rows = [[(c["name"], f"a:quickc:{c['id']}")] for c in cats]
    rows.append([("⏭ Kategoriyasiz", "a:quickc:0")])
    await safe_edit(call.message, "🗂 Hammasi qaysi kategoriyaga qo'shilsin?", kb.grid(rows))


@content.callback_query(F.data.startswith("a:quickc:"))
async def quick_cat(call: CallbackQuery, state: FSMContext):
    cid = int(call.data.split(":")[2])
    await call.answer()
    await _quick_begin(call.message, state, cid or None)


@content.message(QuickAdd.files, FILE)
async def quick_add(m: Message, state: FSMContext):
    data = await state.get_data()
    file_id, file_type, uid = _file_of(m)
    dup = await db.find_by_unique(uid)
    if dup:
        await state.update_data(dups=data.get("dups", 0) + 1)
        await _try_answer(m, f"⚠️ Allaqachon bor (kod <code>{dup['code']}</code>): {esc(dup['title'])}")
        return
    title, desc = parse_media(m)
    code = await db.add_movie(title=title, description=desc, category_id=data.get("cid"),
                              kind="movie", file_id=file_id, file_type=file_type, unique_id=uid)
    await state.update_data(n=data.get("n", 0) + 1, first=data.get("first") or code, last=code)
    await _try_answer(m, f"✅ <code>{code}</code> - {esc(title)}")


@content.message(QuickAdd.files)
async def quick_bad(m: Message):
    await m.answer("⚠️ Video yoki hujjat yuboring, yoki «✅ Tugatish» ni bosing.")


@content.callback_query(F.data == "a:quickdone")
async def quick_done(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    await call.answer("Tayyor")
    n, dups = data.get("n", 0), data.get("dups", 0)
    text = f"✅ Jami qo'shildi: <b>{n}</b> ta"
    if n:
        text += f"\n🔢 Kodlar: {data['first']} - {data['last']}"
    if dups:
        text += f"\n⚠️ Takroriy (qo'shilmadi): {dups} ta"
    await call.message.answer(text, reply_markup=kb.admin_menu())


# ================================================== BAZA KANALLARI (avtomatik import)
async def _reply_in_channel(bot: Bot, m: Message, text: str):
    try:
        await bot.send_message(m.chat.id, text, reply_to_message_id=m.message_id)
    except Exception as e:
        log.warning("Baza kanaliga javob yuborilmadi (botda 'xabar yuborish' huquqi bormi?): %s", e)


def _is_video_doc(m: Message) -> bool:
    return not m.document or (m.document.mime_type or "").startswith("video/")


@content.channel_post(FILE)
async def on_storage_post(m: Message, bot: Bot):
    """Baza kanaliga tashlangan har bir video avtomatik bazaga qo'shiladi."""
    if m.chat.id not in db.storage or not _is_video_doc(m):
        return
    file_id, file_type, uid = _file_of(m)
    dup = await db.find_by_unique(uid)
    if dup:
        await _reply_in_channel(
            bot, m, f"⚠️ Bu video bazada allaqachon bor. Kod: <code>{dup['code']}</code>")
        return
    title, desc = parse_media(m)
    code = await db.add_movie(title=title, description=desc, category_id=db.storage[m.chat.id],
                              kind="movie", file_id=file_id, file_type=file_type, unique_id=uid)
    body = "\n\n".join(part for part in (title, desc) if part)
    signature = f'🤖 Search Movies by Code: <a href="{esc(deeplink(code))}">Join Our Bot</a>'
    formatted_caption = f"{esc(body)}\n\n{signature}" if body else signature
    try:
        await bot.edit_message_caption(
            chat_id=m.chat.id,
            message_id=m.message_id,
            caption=formatted_caption,
            parse_mode="HTML",
        )
    except TelegramBadRequest as e:
        log.warning("Baza postining caption'i formatlanmadi (kod %s): %s", code, e)
    await _reply_in_channel(bot, m, f"✅ Bazaga qo'shildi. Kod: <code>{code}</code>\n🎬 {esc(title)}")


@content.edited_channel_post(FILE)
async def on_storage_edit(m: Message):
    """Kanalda izoh tahrirlansa, bazadagi nom va tavsif ham yangilanadi."""
    if m.chat.id not in db.storage or not _is_video_doc(m):
        return
    _, _, uid = _file_of(m)
    movie = await db.find_by_unique(uid)
    if not movie:
        return
    title, desc = parse_media(m)
    if title == media_title_desc(None, None)[0]:  # "Nomsiz kino": yaxshi nomni buzmaymiz
        return
    await db.execute("UPDATE movies SET title=?, search=?, description=? WHERE code=?",
                     (title, title.lower(), desc, movie["code"]))
