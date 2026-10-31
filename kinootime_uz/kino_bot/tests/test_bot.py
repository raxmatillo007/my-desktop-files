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
from aiogram.types import (ChatFullInfo, ChatMemberAdministrator, ChatMemberLeft, ChatMemberMember,
                           Message, MessageId, User)  # noqa: E402

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
        if name == "GetChat":
            cid = method.chat_id
            if isinstance(cid, str):  # @username
                cid = -100321
            return ChatFullInfo.model_validate({
                "id": cid, "type": "channel", "title": f"Kanal{cid}", "username": "bazakanal",
                "accent_color_id": 0, "max_reaction_count": 0, "accepted_gift_types": {
                    "unlimited_gifts": False, "limited_gifts": False, "unique_gifts": False,
                    "premium_subscription": False, "gifts_from_channels": False}})
        if name == "GetChatMember":
            u = User(id=method.user_id, is_bot=False, first_name="U")
            if self.member == "admin":
                return ChatMemberAdministrator.model_validate({
                    "status": "administrator", "user": u.model_dump(), **{k: False for k in (
                        "can_be_edited", "is_anonymous", "can_manage_chat", "can_delete_messages",
                        "can_manage_video_chats", "can_restrict_members", "can_promote_members",
                        "can_change_info", "can_invite_users", "can_post_stories", "can_edit_stories",
                        "can_delete_stories", "can_send_welcome_messages")}})
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

    async def forward_video(self, uid, fid, caption=None):
        extra = {"video": {"file_id": fid, "file_unique_id": fid + "u", "width": 1, "height": 1, "duration": 1}}
        if caption:
            extra["caption"] = caption
        await self._feed(message=self._message(uid, **extra))

    async def channel_video(self, chat_id, fid, caption=None):
        self.mid += 1
        post = {"message_id": self.mid, "date": int(time.time()),
                "chat": {"id": chat_id, "type": "channel", "title": "Baza"},
                "video": {"file_id": fid, "file_unique_id": fid + "u", "width": 1, "height": 1, "duration": 1}}
        if caption:
            post["caption"] = caption
        await self._feed(channel_post=post)

    async def forward_from_channel(self, uid, chat_id):
        await self._feed(message=self._message(uid, text="x", forward_origin={
            "type": "channel", "date": int(time.time()), "message_id": 7,
            "chat": {"id": chat_id, "type": "channel", "title": "Yangi baza"}}))

    async def edit_channel_video(self, chat_id, fid, caption):
        self.mid += 1
        await self._feed(edited_channel_post={
            "message_id": self.mid, "date": int(time.time()), "edit_date": int(time.time()),
            "chat": {"id": chat_id, "type": "channel", "title": "Baza"}, "caption": caption,
            "video": {"file_id": fid, "file_unique_id": fid + "u", "width": 1, "height": 1, "duration": 1}})

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

    print("\n[15b] Tezkor qo'shish")
    before = await db.scalar("SELECT COUNT(*) FROM movies")
    await h.press(ADMIN, "a:quick")
    await h.press(ADMIN, "a:quickc:1")
    await h.forward_video(ADMIN, "Q1", "Avatar\nZo'r film")
    await h.forward_video(ADMIN, "Q2", "Titanik")
    await h.forward_video(ADMIN, "Q3")
    session.clear()
    await h.forward_video(ADMIN, "Q1", "Avatar\nZo'r film")
    check(any("Allaqachon bor" in t for t in session.texts(ADMIN)), "takroriy video aniqlandi")
    check(await db.scalar("SELECT COUNT(*) FROM movies") == before + 3, "takroriy video qo'shilmadi")
    session.clear()
    await h.press(ADMIN, "a:quickdone")
    check(await db.scalar("SELECT COUNT(*) FROM movies") == before + 3, "3 ta video tezkor qo'shildi")
    av = await db.fetchone("SELECT * FROM movies WHERE title='Avatar'")
    check(av and av["description"] == "Zo'r film" and av["category_id"] == 1, "izohdan nom/tavsif/kategoriya olindi")
    check(any("Jami qo'shildi: <b>3</b>" in t and "Takroriy" in t for t in session.texts(ADMIN)),
          "yakuniy hisobot (takroriylar bilan) chiqdi")
    check(await db.scalar("SELECT COUNT(*) FROM movies WHERE title='Nomsiz kino'") == 1, "izohsiz video 'Nomsiz kino' bo'ldi")

    print("\n[15c] Baza kanallari (avto-import)")
    before = await db.scalar("SELECT COUNT(*) FROM movies")
    session.clear()
    await h.channel_video(-100777, "C0", "Begona")
    check(await db.scalar("SELECT COUNT(*) FROM movies") == before, "ulanmagan kanal e'tiborsiz qoldi")
    # forward orqali ulash (bot admin emas -> rad etiladi, admin bo'lsa -> ulanadi)
    await h.press(ADMIN, "a:sc:add")
    session.member = "member"
    session.clear()
    await h.forward_from_channel(ADMIN, -100777)
    check(-100777 not in db.storage and any("admin emas" in t for t in session.texts(ADMIN)),
          "bot admin bo'lmagan kanal ulanmadi")
    session.member = "admin"
    await h.forward_from_channel(ADMIN, -100777)
    check(-100777 in db.storage, "forward orqali baza kanali ulandi")
    session.member = "member"
    await h.press(ADMIN, "a:sc:set:-100777:1")
    check(db.storage[-100777] == 1, "kanal kategoriyaga bog'landi")
    session.clear()
    await h.channel_video(-100777, "C1", "🎬 Kanal Kinosi 🔥\n@reklama_kanal #kino\nhttps://t.me/x\nKanalimizga obuna bo'ling\nTavsif")
    m_new = await db.fetchone("SELECT * FROM movies WHERE unique_id='C1u'")
    check(m_new and m_new["title"] == "Kanal Kinosi" and m_new["description"] == "Tavsif",
          "izoh tozalandi (reklama/havola/teg/emoji olib tashlandi)")
    check(m_new["category_id"] == 1, "kategoriya kanalga qarab berildi")
    check(any("Bazaga qo'shildi" in (d.get("text") or "") for n, d in session.calls if n == "SendMessage"),
          "kanalga kod yozildi")
    session.clear()
    await h.channel_video(-100777, "C1", "Boshqa nom")
    check(await db.scalar("SELECT COUNT(*) FROM movies WHERE unique_id='C1u'") == 1, "kanalda takror qo'shilmadi")
    check(any("allaqachon" in (d.get("text") or "") for n, d in session.calls if n == "SendMessage"),
          "takror haqida kanalga xabar yozildi")
    await h.edit_channel_video(-100777, "C1", "Tahrirlangan Nom")
    check((await db.find_by_unique("C1u"))["title"] == "Tahrirlangan Nom", "kanalda izoh tahrirlansa, nom yangilandi")
    await h.press(ADMIN, "a:sc:del:-100777")
    check(-100777 not in db.storage, "baza kanali uzildi")
    # @username orqali ulash
    await h.press(ADMIN, "a:sc:add")
    session.member = "admin"
    await h.text(ADMIN, "@bazakanal")
    check(-100321 in db.storage, "@username orqali ham ulandi")
    session.member = "member"
    await h.press(ADMIN, "a:sc:del:-100321")

    print("\n[15d] Majburiy obuna kanali qo'shish (matn orqali)")
    await h.press(ADMIN, "a:chadd")
    session.member = "admin"
    await h.text(ADMIN, "@bazakanal")
    session.member = "member"
    check(await db.scalar("SELECT link FROM channels WHERE chat_id=-100321") == "https://t.me/bazakanal",
          "obuna kanali qo'shildi")
    await h.press(ADMIN, "a:chdel:-100321")

    print("\n[15e] Izoh tozalash va fayl nomi")
    from app.services.captions import media_title_desc as mtd
    check(mtd("🔥 Avatar (2009) 🔥\n#kino @kanal", None) == ("Avatar (2009)", ""), "emoji/teg/nom tozalandi")
    check(mtd(None, "Avatar_2009_1080p_WEB-DL.mp4")[0] == "Avatar 2009", "fayl nomidan texnik so'zlar olib tashlandi")
    check(mtd("@faqat_nom https://x.com", None)[0] == "Nomsiz kino", "faqat reklama bo'lsa 'Nomsiz kino'")
    check(mtd("Kanalimizga obuna bo'ling", None)[0] == "Kanalimizga obuna bo'ling", "yagona qator reklama bo'lsa ham yo'qolmaydi")
    check(mtd("**Avatar** (2009)\n1080p WEB-DL", None) == ("Avatar (2009)", ""),
          "caption format belgilari va texnik metadata tozalandi")

    print("\n[15f] Eski bazani yangilash (migratsiya) va .env dan kanal")
    import sqlite3
    from app.database import DB
    old_path = f"{TMP}/old.db"
    c = sqlite3.connect(old_path)
    c.executescript("""CREATE TABLE movies (code INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL DEFAULT 'movie',
        title TEXT NOT NULL, search TEXT NOT NULL, description TEXT NOT NULL DEFAULT '', category_id INTEGER,
        file_id TEXT, file_type TEXT, views INTEGER NOT NULL DEFAULT 0, added_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        INSERT INTO movies (title, search, file_id, file_type) VALUES ('Eski', 'eski', 'F', 'video');
        CREATE TABLE settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        INSERT INTO settings VALUES ('storage_channel', '-100999');""")
    c.commit(); c.close()
    d = DB(); d.path = old_path
    cfg.STORAGE_CHANNELS = [-100555]
    await d.init()
    cols = {r["name"] for r in await d.fetchall("PRAGMA table_info(movies)")}
    check("unique_id" in cols, "eski bazaga unique_id ustuni qo'shildi")
    check((await d.get_movie(1))["title"] == "Eski", "eski kinolar saqlanib qoldi")
    check(set(d.storage) == {-100999, -100555}, "eski sozlama va .env kanali baza kanallariga ko'chdi")
    check("storage_channel" not in d.settings, "eski sozlama tozalandi")
    test_code = await d.add_movie(title="Kod test", description="", category_id=None,
                                  kind="series", file_id=None, file_type=None)
    await d.add_episode(test_code, "EP_TEST", "video")
    await d.execute("INSERT INTO favorites (user_id, movie_code) VALUES (?, ?)", (1, test_code))
    await d.reassign_movie_code(test_code, 99)
    check(await d.get_movie(99) is not None and await d.episode_numbers(99) == [1]
          and await d.is_fav(1, 99), "kod o'zgarganda kino, qismlar va sevimlilar birga yangilandi")
    try:
        await d.reassign_movie_code(99, 1)
    except ValueError:
        check(await d.get_movie(99) is not None, "band kod ziddiyatida transaction rollback qilindi")
    else:
        check(False, "band kod ziddiyati rad etildi")
    await d.close()
    cfg.STORAGE_CHANNELS = []

    print("\n[16] Kino o'chirish")
    await h.press(ADMIN, "a:e:delok:1")
    check(await db.get_movie(1) is None, "kino o'chirildi")

    print("\n[17] Zaxira va FSM saqlash")
    expected = await db.scalar("SELECT COUNT(*) FROM movies")
    path = await make_backup()
    import sqlite3
    c = sqlite3.connect(path)
    check(c.execute("SELECT COUNT(*) FROM movies").fetchone()[0] == expected, "zaxira nusxa to'g'ri ochildi")
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

    print("\n[20] Bir vaqtda 30 ta video forward (poyga holati)")
    before = await db.scalar("SELECT COUNT(*) FROM movies")
    await h.press(ADMIN, "a:quick")
    await h.press(ADMIN, "a:quickc:0")
    session.clear()
    ids = [f"P{i}" for i in range(30)] + ["P3", "P7"]   # 2 ta takror
    await asyncio.gather(*(h.forward_video(ADMIN, fid, f"Film {fid}") for fid in ids))
    await h.press(ADMIN, "a:quickdone")
    check(await db.scalar("SELECT COUNT(*) FROM movies") == before + 30, "aynan 30 ta qo'shildi, takrorlar o'tmadi")
    check(await db.scalar("SELECT COUNT(DISTINCT unique_id) FROM movies WHERE title LIKE 'Film P%'") == 30,
          "takroriy yozuv yo'q")
    check(any("Jami qo'shildi: <b>30</b>" in t and "Takroriy (qo'shilmadi): 2" in t for t in session.texts(ADMIN)),
          "hisobot to'g'ri: 30 ta qo'shildi, 2 ta takror")

    print("\n🎉 BARCHA SINOVLAR O'TDI")


async def runner():
    try:
        await main()
    finally:
        await db.close()


asyncio.run(runner())
