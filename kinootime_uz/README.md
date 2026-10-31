# 🎬 Kino Bot (professional versiya)

Telegram uchun to'liq kino/serial bot: aiogram 3 + SQLite.

## Imkoniyatlar
**Foydalanuvchi:** kod yoki nom bo'yicha qidirish · seriallar (qismlar, oldingi/keyingi) ·
kategoriyalar · 🔥 Top · 🆕 Yangi · ❤️ Sevimlilar · 🔗 ulashish (deep link) · majburiy obuna.

**Admin (`/admin`):** kino/serial qo'shish · ⚡ tezkor qo'shish · 📥 baza kanallari · tahrirlash
(nom, tavsif, kategoriya, fayl) · qism boshqarish · kategoriyalar · majburiy obuna kanallari ·
ban/unban · statistika · barchaga xabar (progress bilan) · salomlashuv matni · himoyalangan kontent ·
adminlarni bot ichidan boshqarish · zaxira nusxa.

**Texnik:** FSM holati bazada saqlanadi · spamdan himoya · kunlik avtomatik zaxira ·
aylanuvchi log fayllari · eski bazani avtomatik yangilash (migratsiya) · Docker · systemd.

## Ishga tushirish
```
pip install -r requirements.txt
cp .env.example .env      # BOT_TOKEN va ADMINS ni to'ldiring (har biri alohida qatorda)
python main.py
```
Docker bilan: `docker compose up -d --build`

## Kinolarni tez qo'shish

### 1) ⚡ Tezkor qo'shish
`/admin` -> ⚡ Tezkor qo'shish. Kanaldan bir nechta videoni belgilab botga forward qiling.
Har bir videoning izohi nom bo'ladi (1-qator = nom, qolgani = tavsif).

### 2) 📥 Baza kanallari (avtomatik)
1. Yangi kanal yarating, botni unga **admin** qiling (faqat «Xabar yuborish» huquqi yetarli).
2. `/admin` -> ⚙️ Sozlamalar -> 📥 Baza kanallari -> ➕ Kanal ulash, so'ng kanaldan
   istalgan xabarni botga **forward** qiling (yoki `@username` / ID yuboring).
   Xohlasangiz `.env` dagi `STORAGE_CHANNEL=-100...` ga ham yozish mumkin.
3. Endi kanalga video tashlang: bot o'zi bazaga qo'shadi va kanalga kodni yozadi.
4. Har bir baza kanalini alohida **kategoriyaga** bog'lash mumkin (masalan, "Jangari" kanali).
5. Kanalda izohni tahrirlasangiz, bazadagi nom ham yangilanadi.

### Avtomatik tozalash va himoya
- Izohdan reklama, havola, `@nom`, `#teg` va emojilar olib tashlanadi. Izoh bo'lmasa, fayl nomi
  ishlatiladi (`Avatar_2009_1080p_WEB-DL.mp4` -> `Avatar 2009`).
- Bazada bor video qayta qo'shilmaydi (takrorlar haqida xabar beriladi).
- Bot kanalga admin bo'lishidan oldin tashlangan videolarni ko'rmaydi (Telegram cheklovi):
  ularni ⚡ Tezkor qo'shish orqali forward qiling.

## Sinov
`python tests/test_bot.py` - Telegramsiz, soxta sessiya bilan butun oqimni tekshiradi (81 ta tekshiruv).

## Muhim eslatmalar
- Faqat o'zingizda huquqi yoki ruxsati bor kinolarni joylang. Ruxsatsiz tarqatish mualliflik
  huquqini buzadi va bot/kanal bloklanishiga olib kelishi mumkin.
- Kinolar Telegramda saqlanadi, botda faqat `file_id`. Bot tokenini almashtirsangiz, kinolarni
  qayta yuklash kerak bo'ladi.
- Bot doim ishlashi uchun VPS/serverda turishi kerak.
