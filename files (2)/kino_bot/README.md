# 🎬 Kino Bot (professional versiya)

Telegram uchun to'liq kino/serial bot: aiogram 3 + SQLite.

## Imkoniyatlar
**Foydalanuvchi:** kod yoki nom bo'yicha qidirish · seriallar (qismlar, oldingi/keyingi) ·
kategoriyalar · 🔥 Top · 🆕 Yangi · ❤️ Sevimlilar · 🔗 ulashish (deep link) · majburiy obuna.

**Admin (`/admin`):** kino/serial qo'shish (ko'p qismni ketma-ket yuklash) · tahrirlash
(nom, tavsif, kategoriya, fayl) · qism o'chirish · kategoriyalar · kanallar · foydalanuvchilarni
ban/unban · statistika · barchaga xabar (progress bilan) · salomlashuv matni · himoyalangan kontent
· adminlarni bot ichidan boshqarish · zaxira nusxa.

**Texnik:** FSM holati bazada saqlanadi (qayta ishga tushsa ham yo'qolmaydi) · spamdan himoya ·
avtomatik kunlik zaxira (bosh adminga yuboriladi) · log fayllari (aylanuvchi) · Docker · systemd.

## Ishga tushirish (oddiy)
```
pip install -r requirements.txt
cp .env.example .env      # BOT_TOKEN va ADMINS ni to'ldiring
python main.py
```

## Docker bilan
```
cp .env.example .env
docker compose up -d --build
docker compose logs -f
```
Ma'lumotlar `./data` papkasida saqlanadi (baza, zaxira, loglar).

## VPS da systemd bilan
`kino-bot.service` faylini `/etc/systemd/system/` ga nusxalab, yo'llarni to'g'rilang:
```
sudo systemctl daemon-reload
sudo systemctl enable --now kino-bot
```

## Foydalanish
1. `/admin` -> ➕ Qo'shish -> 🎬 Kino yoki 📺 Serial.
2. Majburiy obuna: 📢 Kanallar -> kanal qo'shing (bot kanalda ADMIN bo'lishi shart).
3. Foydalanuvchilar kodni yuboradi yoki nomini yozadi.

## Sinov
`python tests/test_bot.py` - Telegramsiz, soxta sessiya bilan butun oqimni tekshiradi.

## Eslatma
Videoni botga to'g'ridan-to'g'ri yuklang. Bot faqat Telegram `file_id` sini saqlaydi,
shuning uchun serverda kino fayllari saqlanmaydi. Zaxira nusxa bazani saqlaydi, lekin
`file_id` lar faqat shu bot uchun ishlaydi: tokenni almashtirsangiz kinolarni qayta yuklash kerak.
