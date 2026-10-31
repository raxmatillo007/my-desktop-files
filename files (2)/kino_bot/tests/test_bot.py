"""
Telegram serverisiz sinov: soxta sessiya orqali butun bot oqimini tekshiradi.
Ishga tushirish:  python tests/test_bot.py
"""
import asyncio
import os
import sys
import tempfile
import time
from pathlib import Path

TMP = tempfile.mkdtemp()
os.environ.update({
    "DB_PATH": f"{TMP}/t.db", "BACKUP_DIR": f"{TMP}/bk", "LOG_DIR": f"{TMP}/lg",
    "ADMINS": "1", "BOT_TOKEN": "123:abc",
})
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from aiogram import Bot  # noqa: E402
from aiogram.client.session.base import BaseSession  # noqa: E402
from aiogram.fsm.storage.base import StorageKey  # noqa: E402
from aiogram.types import (ChatMemberLeft, ChatMemberMember, Message, MessageId, User)  # noqa: E402

from app.bot_factory import build_dispatcher  # noqa: E402
from app.config import cfg  # noqa: E402
from app.database import db  # noqa: E402
from app.services.backup import make_backup  # noqa: E402
from app.storage import SQLiteStorage  # noqa: E402
from app.utils import rt  # noqa: E402

BOT_USER = User(id=999, is_bot=True, first_name="Bot", username="test_bot")


class FakeSession(BaseSession):
    def __init__(self):
        super().__init__()
        self.calls = []
        self.n = 1000
        self.member = "member"

    async def close(self): ...

    async def stream_content(self, *a, **k):
        yield b""

    def _msg(self, method):
        self.n += 1
        chat_id = getattr(method, "chat_id", None) or 1
        return Message.model_validate({
            "message_id": self.n, "date": int(time.time()),
            "chat": {"id": chat_id, "type": "private"}, "text": "x"})

    async def make_request(self, bot, method, timeout=None):
        name = type(method).__name__
        self.calls.append((name, method.model_dump(exclude_none=True)))
        if name in ("SendMessage", "SendVideo", "SendDocument", "SendPhoto",
                    "EditMessageText", "EditMessageReplyMarkup"):
            return self._msg(method)
        if name == "CopyMessage":
            self.n += 1
            return MessageId(message_id=self.n)
        if name == "GetMe":
            return BOT_USER
        if name == "GetChatMember":
            u = User(id=method.user_id, is_bot=False, first_name="U")
            if self.member == "left":
                return ChatMemberLeft(status="left", user=u)
            return ChatMemberMember(status="member", user=u)
        return True

    def sent(self, name, to=None):
        return [d for n, d in self.calls if n == name and (to is None or d.get("chat_id") == to)]

    def texts(self, to):
        return [d.get("text") or d.get("caption") or "" for n, d in self.calls
                if n in ("SendMessage", "SendVideo", "SendDocument", "EditMessageText")
                and d.get("chat_id", to) == to]

    def clear(self):
        self.calls.clear()


class Harness:
    def __init__(self, dp, bot, session):
        self.dp, self.bot, self.s, self.uid = dp, bot, session, 0
        self.mid = 0

    def _from(self, uid):
        return {"id": uid, "is_bot": False, "first_name": f"User{uid}"}

    async def _feed(self, **kw):
        self.uid += 1
        await self.dp.feed_raw_update(self.bot, {"update_id": self.uid, **kw})

    def _message(self, uid, **extra):
        self.mid += 1
        return {"message_id": self.mid, "date": int(time.time()),
                "chat": {"id": uid, "type": "private"}, "from": self._from(uid), **extra}

    async def text(self, uid, text):
        extra = {"text": text}
        if text.startswith("/"):
            extra["entities"] = [{"type": "bot_command", "offset": 0, "length": len(text.split()[0])}]
        await self._feed(message=self._message(uid, **extra))

    async def video(self, uid, fid):
        await self._feed(message=self._message(uid, video={
            "file_id": fid, "file_unique_id": fid + "u", "width": 1, "height": 1, "duration": 1}))

    async def press(self, uid, data, markup=None):
        msg = {"message_id": 50, "date": int(time.time()), "chat": {"id": uid, "type": "private"},
               "from": {"id": 999, "is_bot": True, "first_name": "Bot"}, "text": "menu"}
        if markup:
            msg["reply_markup"] = markup
        await self._feed(callback_query={"id": str(self.uid), "from": self._from(uid),
                                         "chat_instance": "ci", "data": data, "message": msg})


def check(cond, label):
    print(("  ✅ " if cond else "  ❌ ") + label)
    if not cond:
        raise AssertionError(label)


async def main():
    await db.init()
    session = FakeSession()
    bot = Bot("123:abc", session=session)
    rt.bot_username = "test_bot"
    dp = build_dispatcher(throttle=0)
    h = Harness(dp, bot, session)
    ADMIN, U = 1, 2

    print("\n[1] Foydalanuvchi /start")
    await h.text(U, "/start")
    check(any("Assalomu" in t for t in session.texts(U)), "salomlashuv yuborildi")
    check(await db.scalar("SELECT COUNT(*) FROM users WHERE id=?", (U,)) == 1, "foydalanuvchi bazaga yozildi")

    print("\n[2] Admin panel")
    session.clear()
    await h.text(ADMIN, "/admin")
    check(any("Admin panel" in t for t in session.texts(ADMIN)), "/admin panel ochildi")
    await h.text(U, "/admin")
    check(not any("Admin panel" in t for t in session.texts(U)), "oddiy foydalanuvchiga admin panel berilmadi")

    print("\n[3] Kategoriya qo'shish")
    await h.press(ADMIN, "a:cataddb")
    await h.text(ADMIN, "Jangari")
    check(await db.scalar("SELECT COUNT(*) FROM categories") == 1, "kategoriya yaratildi")
    await h.press(ADMIN, "a:cataddb")
    session.clear()
    await h.text(ADMIN, "Jangari")
    check(any("allaqachon" in t for t in session.texts(ADMIN)), "takroriy kategoriya rad etildi")
    await h.text(ADMIN, "/cancel")

    print("\n[4] Kino qo'shish")
    await h.press(ADMIN, "a:addk:movie")
    await h.video(ADMIN, "VID_MOVIE")
    await h.text(ADMIN, "Test Kino")
    await h.text(ADMIN, "Zo'r kino & <tavsif>")
    await h.press(ADMIN, "a:addc:1")
    m = await db.get_movie(1)
    check(m and m["title"] == "Test Kino" and m["category_id"] == 1 and m["file_id"] == "VID_MOVIE",
          "kino kategoriya bilan saqlandi (kod 1)")

    print("\n[5] Serial va qismlar")
    await h.press(ADMIN, "a:addk:series")
    await h.text(ADMIN, "Test Serial")
    await h.text(ADMIN, "-")
    await h.press(ADMIN, "a:addc:0")
    check((await db.get_movie(2))["kind"] == "series", "serial yaratildi (kod 2)")
    await h.video(ADMIN, "EP1")
    await h.video(ADMIN, "EP2")
    await h.video(ADMIN, "EP3")
    await h.press(ADMIN, "a:epdone")
    check(await db.episode_numbers(2) == [1, 2, 3], "3 ta qism ketma-ket raqam oldi")

    print("\n[6] Foydalanuvchi kino oladi")
    session.clear()
    await h.text(U, "1")
    check(len(session.sent("SendVideo", U)) == 1, "kod bo'yicha video yuborildi")
    check("&lt;tavsif&gt;" in session.sent("SendVideo", U)[0]["caption"], "HTML to'g'ri escape qilindi")
    check((await db.get_movie(1))["views"] == 1, "ko'rishlar hisoblandi")
    session.clear()
    await h.text(U, "999")
    check(any("topilmadi" in t for t in session.texts(U)), "mavjud bo'lmagan kod xabari")
    session.clear()
    await h.text(U, "test kino")
    check(any("Natijalar" in t for t in session.texts(U)), "nom bo'yicha qidiruv ishladi")
    session.clear()
    await h.text(U, "qwertyuiop")
    check(any("topilmadi" in t for t in session.texts(U)), "topilmagan qidiruv xabari")

    print("\n[7] Serial ko'rish")
    session.clear()
    await h.press(U, "m:2")
    msg = session.sent("SendMessage", U)[-1]
    check("Qismlar soni" in msg["text"], "serial kartasi chiqdi")
    session.clear()
    await h.press(U, "ep:2:2")
    check(len(session.sent("SendVideo", U)) == 1, "2-qism yuborildi")
    kbd = str(session.sent("SendVideo", U)[0]["reply_markup"])
    check("ep:2:1" in kbd and "ep:2:3" in kbd, "oldingi/keyingi qism tugmalari bor")

    print("\n[8] Sevimlilar")
    markup = {"inline_keyboard": [[{"text": "❤️ Sevimlilarga qo'shish", "callback_data": "fav:1"}]]}
    session.clear()
    await h.press(U, "fav:1", markup)
    check(await db.is_fav(U, 1), "sevimlilarga qo'shildi")
    check(len(session.sent("EditMessageReplyMarkup")) == 1, "tugma yangilandi")
    session.clear()
    await h.text(U, "❤️ Sevimlilar")
    check(any("Sevimlilar" in t for t in session.texts(U)), "sevimlilar ro'yxati ochildi")
    await h.press(U, "fav:1", markup)
    check(not await db.is_fav(U, 1), "sevimlilardan olib tashlandi")

    print("\n[9] Menyu: kategoriyalar, top, yangi")
    for btn, word in (("🗂 Kategoriyalar", "Kategoriyani"), ("🔥 Top kinolar", "ko'p ko'rilgan"),
                      ("🆕 Yangi kinolar", "Yangi")):
        session.clear()
        await h.text(U, btn)
        check(any(word in t for t in session.texts(U)), btn)
    session.clear()
    await h.press(U, "lst:cat:1:0")
    check(len(session.sent("EditMessageText")) == 1, "kategoriya ro'yxati ochildi")

    print("\n[10] Deep link")
    session.clear()
    await h.text(U, "/start m1")
    check(len(session.sent("SendVideo", U)) == 1, "/start m1 kinoni yubordi")

    print("\n[11] Admin kinoni boshqaradi")
    await h.text(ADMIN, "/admin")
    await h.press(ADMIN, "a:manage")
    await h.text(ADMIN, "1")
    await h.press(ADMIN, "a:e:title:1")
    await h.text(ADMIN, "Yangi Nom")
    check((await db.get_movie(1))["title"] == "Yangi Nom", "nom o'zgartirildi")
    await h.press(ADMIN, "a:e:setcat:1:0")
    check((await db.get_movie(1))["category_id"] is None, "kategoriya olib tashlandi")
    await h.press(ADMIN, "a:e:epdel:2")
    await h.text(ADMIN, "2")
    check(await db.episode_numbers(2) == [1, 3], "2-qism o'chirildi")
    await h.press(ADMIN, "a:e:eps:2")
    await h.video(ADMIN, "EP4")
    await h.press(ADMIN, "a:epdone")
    check(await db.episode_numbers(2) == [1, 3, 4], "yangi qism 4-raqam oldi")

    print("\n[12] Majburiy obuna")
    await db.execute("INSERT INTO channels VALUES (?, ?, ?)", (-100500, "Kanal", "https://t.me/kanal"))
    session.member = "left"
    session.clear()
    await h.text(3, "1")
    check(any("obuna bo'ling" in t for t in session.texts(3)), "obuna bo'lmaganga talab ko'rsatildi")
    check(len(session.sent("SendVideo", 3)) == 0, "kino berilmadi")
    session.clear()
    await h.press(3, "check:m1")
    check(len(session.sent("SendVideo", 3)) == 0, "obunasiz «Tekshirish» o'tmadi")
    session.member = "member"
    session.clear()
    await h.press(3, "check:m1")
    check(len(session.sent("SendVideo", 3)) == 1, "obuna bo'lgach kino yuborildi")
    session.member = "left"
    session.clear()
    await h.text(ADMIN, "1")
    check(len(session.sent("SendVideo", ADMIN)) == 1, "admin obunadan ozod")
    session.member = "member"

    print("\n[13] Ban")
    await h.press(ADMIN, "a:u:ban")
    await h.text(ADMIN, "2")
    session.clear()
    await h.text(U, "1")
    check(any("bloklangan" in t for t in session.texts(U)), "bloklangan foydalanuvchi to'xtatildi")
    await h.press(ADMIN, "a:u:unban")
    await h.text(ADMIN, "2")
    session.clear()
    await h.text(U, "1")
    check(len(session.sent("SendVideo", U)) == 1, "blokdan chiqgach ishladi")

    print("\n[14] Xabar yuborish (broadcast)")
    await h.press(ADMIN, "a:bc")
    await h.text(ADMIN, "Hammaga salom!")
    session.clear()
    await h.press(ADMIN, "bc:yes")
    await asyncio.sleep(1.0)
    n_users = await db.scalar("SELECT COUNT(*) FROM users WHERE active=1 AND banned=0")
    check(len(session.sent("CopyMessage")) == n_users, f"{n_users} ta foydalanuvchiga nusxa yuborildi")

    print("\n[15] Sozlamalar, adminlar, statistika")
    await h.press(ADMIN, "a:set:protect")
    check(db.settings.get("protect") == "1", "himoya yoqildi")
    session.clear()
    await h.text(U, "1")
    check(session.sent("SendVideo", U)[0].get("protect_content") is True, "protect_content ishladi")
    await h.press(ADMIN, "a:set:protect")
    await h.press(ADMIN, "a:set:welcome")
    await h.text(ADMIN, "Salom, {name}!")
    session.clear()
    await h.text(U, "/start")
    check(any("Salom, User2!" in t for t in session.texts(U)), "maxsus salomlashuv ishladi")
    await h.press(ADMIN, "a:admadd")
    await h.text(ADMIN, "77")
    check(77 in db.admin_ids, "yangi admin qo'shildi")
    session.clear()
    await h.text(77, "/admin")
    check(any("Admin panel" in t for t in session.texts(77)), "yangi admin panelga kira oldi")
    await h.press(77, "a:admins")
    check(len(session.sent("AnswerCallbackQuery")) >= 1, "oddiy admin «Adminlar» bo'limiga kira olmadi")
    session.clear()
    await h.press(ADMIN, "a:stats")
    check("Statistika" in session.sent("EditMessageText")[0]["text"], "statistika chiqdi")

    print("\n[16] Kino o'chirish")
    await h.press(ADMIN, "a:e:delok:1")
    check(await db.get_movie(1) is None, "kino o'chirildi")

    print("\n[17] Zaxira va FSM saqlash")
    path = await make_backup()
    import sqlite3
    c = sqlite3.connect(path)
    check(c.execute("SELECT COUNT(*) FROM movies").fetchone()[0] == 1, "zaxira nusxa to'g'ri ochildi")
    c.close()
    st = SQLiteStorage(db)
    key = StorageKey(bot_id=1, chat_id=5, user_id=5)
    await st.set_state(key, "AddMovie:title")
    await st.set_data(key, {"title": "Ўзбек"})
    st2 = SQLiteStorage(db)
    check(await st2.get_state(key) == "AddMovie:title" and (await st2.get_data(key))["title"] == "Ўзбек",
          "FSM holati bazada saqlanadi")

    print("\n[18] Spamdan himoya")
    dp.throttle_mw.rate = 5
    session.clear()
    await h.text(50, "/help")
    await h.text(50, "/help")
    check(len(session.sent("SendMessage", 50)) == 1, "ikkinchi tez so'rov tashlandi")

    print("\n[19] Noto'g'ri kiritishlar (xatosiz ishlashi)")
    session.clear()
    await h.text(U, "9" * 30)
    await h.text(U, "a")
    await h.text(U, "%_\\")
    await h.press(U, "ep:999:1")
    await h.press(U, "m:abc")
    check(True, "g'alati kiritishlarda bot qulamadi")

    print("\n🎉 BARCHA SINOVLAR O'TDI")


async def runner():
    try:
        await main()
    finally:
        await db.close()


asyncio.run(runner())
