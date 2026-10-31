import asyncio
import logging
from pyrogram import Client
from pyrogram.errors import FloodWait, RPCError

# my.telegram.org saytidan olinadigan shaxsiy kodlaringiz
API_ID = 34881938
API_HASH = "d023a99e5a6f42442e0bef868b6a7997"
SESSION_NAME = "zakirov_scraper_session"

# SOZLAMALAR
TARGET_BOT = "Zakirovsfilms_bot"      # Kinolar olinadigan maqsadli bot
DESTINATION_CHAT_ID = -1003773297585     # Kinolar tushadigan O'ZINGIZNING KANALINGIZ IDsi
START_CODE = 100                          # 1-koddan boshlaydi
END_CODE = 172                      # Taxminan 1500-kodgacha qidiradi (o'zgartirishingiz mumkin)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("zakirov_scraper")

async def main():
    async with Client(SESSION_NAME, api_id=API_ID, api_hash=API_HASH) as app:
        logger.info(f"@{TARGET_BOT} botidan kinolarni yig'ish boshlandi...")
        
        @app.on_message()
        async def handle_new_message(client, message):
            # Xabar aynan @Zakirovsfilms_bot dan kelganini tekshiramiz
            if message.chat and message.chat.username == TARGET_BOT:
                # Agar xabarda kino (video) yoki fayl (document) bo'lsa
                if message.video or message.document:
                    try:
                        # Kinoni o'zingizning kanalga ko'chirish
                        await message.copy(chat_id=DESTINATION_CHAT_ID)
                        logger.info(f"Kino muvaffaqiyatli kanalingizga ko'chirildi!")
                    except Exception as e:
                        logger.error(f"Kanalga ko'chirishda xatolik: {e}")

        # Ketma-ket kodlarni @Zakirovsfilms_bot ga yuborish
        for code in range(START_CODE, END_CODE + 1):
            try:
                logger.info(f"Botga {code} kodi yuborilmoqda...")
                await app.send_message(chat_id=TARGET_BOT, text=str(code))
                
                # Telegram akkauntingiz spamga tushib qolmasligi uchun 4 soniya kutish
                await asyncio.sleep(4)
                
            except FloodWait as e:
                logger.warning(f"FloodWait cheklovi: {e.value} soniya kutilmoqda...")
                await asyncio.sleep(e.value + 5)
            except RPCError as e:
                logger.error(f"Telegram xatoligi: {e}")
                break
            except Exception as e:
                logger.error(f"Kutilmagan xatolik: {e}")

        await asyncio.sleep(10)
        logger.info("Barcha kodlar tekshirib bo'lindi!")

if __name__ == "__main__":
    asyncio.run(main())
