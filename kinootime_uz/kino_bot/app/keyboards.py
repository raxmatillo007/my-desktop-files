from aiogram.types import (
    InlineKeyboardButton as IB,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

BTN_SEARCH = "🔎 Qidirish"
BTN_CATS = "🗂 Kategoriyalar"
BTN_TOP = "🔥 Top kinolar"
BTN_NEW = "🆕 Yangi kinolar"
BTN_FAV = "❤️ Sevimlilar"
BTN_HELP = "ℹ️ Yordam"
BTN_ADMIN = "🛠 Admin panel"


def grid(rows: list[list[tuple[str, str]]]) -> InlineKeyboardMarkup:
    """[[(matn, callback_data), ...], ...] -> InlineKeyboardMarkup"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [IB(text=t, callback_data=d) for t, d in row] for row in rows
    ])


def main_menu(admin: bool = False) -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text=BTN_SEARCH), KeyboardButton(text=BTN_CATS)],
        [KeyboardButton(text=BTN_TOP), KeyboardButton(text=BTN_NEW)],
        [KeyboardButton(text=BTN_FAV), KeyboardButton(text=BTN_HELP)],
    ]
    if admin:
        rows.append([KeyboardButton(text=BTN_ADMIN)])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True,
                               input_field_placeholder="Kino nomi yoki kodi...")


# ------------------------------------------------ foydalanuvchi
def sub_kb(channels, payload: str) -> InlineKeyboardMarkup:
    rows = [[IB(text=f"📢 {ch['title']}", url=ch["link"])] for ch in channels]
    rows.append([IB(text="✅ Tekshirish", callback_data=f"check:{payload}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def fav_text(is_fav: bool) -> str:
    return "💔 Sevimlilardan olish" if is_fav else "❤️ Sevimlilarga qo'shish"


def _fav_rows(code: int, is_fav: bool):
    return [
        [IB(text=fav_text(is_fav), callback_data=f"fav:{code}")],
        [IB(text="❌ Yopish", callback_data="close_message")],
    ]


def movie_kb(code: int, is_fav: bool) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=_fav_rows(code, is_fav))


def episodes_kb(code, numbers, page, is_fav, per_page=20) -> InlineKeyboardMarkup:
    chunk = numbers[page * per_page:(page + 1) * per_page]
    rows, row = [], []
    for n in chunk:
        row.append(IB(text=str(n), callback_data=f"ep:{code}:{n}"))
        if len(row) == 5:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    pages = max((len(numbers) + per_page - 1) // per_page, 1)
    if pages > 1:
        nav = []
        if page > 0:
            nav.append(IB(text="⬅️", callback_data=f"epl:{code}:{page - 1}"))
        nav.append(IB(text=f"{page + 1}/{pages}", callback_data="noop"))
        if page + 1 < pages:
            nav.append(IB(text="➡️", callback_data=f"epl:{code}:{page + 1}"))
        rows.append(nav)
    rows += _fav_rows(code, is_fav)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def episode_nav_kb(code: int, prev, nxt) -> InlineKeyboardMarkup:
    nav = []
    if prev:
        nav.append(IB(text=f"⬅️ {prev}-qism", callback_data=f"ep:{code}:{prev}"))
    if nxt:
        nav.append(IB(text=f"{nxt}-qism ➡️", callback_data=f"ep:{code}:{nxt}"))
    rows = [nav] if nav else []
    rows.append([IB(text="📋 Barcha qismlar", callback_data=f"m:{code}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def list_kb(rows_data, kind: str, arg, page: int, total: int, per_page: int) -> InlineKeyboardMarkup:
    rows = []
    for r in rows_data:
        icon = "📺" if r["kind"] == "series" else "🎬"
        rows.append([IB(text=f"{icon} {r['title'][:48]}", callback_data=f"m:{r['code']}")])
    pages = max((total + per_page - 1) // per_page, 1)
    if pages > 1:
        nav = []
        if page > 0:
            nav.append(IB(text="⬅️", callback_data=f"lst:{kind}:{arg}:{page - 1}"))
        nav.append(IB(text=f"{page + 1}/{pages}", callback_data="noop"))
        if page + 1 < pages:
            nav.append(IB(text="➡️", callback_data=f"lst:{kind}:{arg}:{page + 1}"))
        rows.append(nav)
    if kind == "cat":
        rows.append([IB(text="🗂 Kategoriyalar", callback_data="cats")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def search_kb(rows_data) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [IB(text=f"{'📺' if r['kind'] == 'series' else '🎬'} {r['title'][:48]} ({r['code']})",
            callback_data=f"m:{r['code']}")] for r in rows_data
    ])


# ------------------------------------------------ admin
def admin_menu() -> InlineKeyboardMarkup:
    return grid([
        [("➕ Qo'shish", "a:add"), ("⚡ Tezkor qo'shish", "a:quick")],
        [("🔧 Boshqarish", "a:manage"), ("🎞 Ro'yxat", "a:list:0")],
        [("🗂 Kategoriyalar", "a:cats"), ("📢 Kanallar", "a:ch")],
        [("👥 Foydalanuvchilar", "a:users"), ("📨 Xabar yuborish", "a:bc")],
        [("📊 Statistika", "a:stats"), ("⚙️ Sozlamalar", "a:settings")],
    ])


def back_admin() -> InlineKeyboardMarkup:
    return grid([[("🏠 Admin panel", "a:back")]])
