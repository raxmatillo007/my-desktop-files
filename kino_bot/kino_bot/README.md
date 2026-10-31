# Kino Telegram Bot

Python 3.11+, aiogram 3.x va SQLite (`aiosqlite`) asosidagi Telegram kino bot.
Foydalanuvchilar kino kodini yuborib video yoki havola oladi. Admin paneldan
kino qo'shish, o'chirish, statistika ko'rish va foydalanuvchilarga xabar
yuborish mumkin.

## 1. Python o'rnatish

Python 3.11 yoki undan yangi versiyani o'rnating:

- Windows: [python.org/downloads](https://www.python.org/downloads/) sahifasidan
  Python o'rnatuvchisini yuklab oling. O'rnatishda **Add Python to PATH** ni
  belgilang.
- macOS yoki Linux: tizimingizdagi Python paket menejeridan yoki
  [python.org/downloads](https://www.python.org/downloads/) dan foydalaning.

Terminalda versiyani tekshiring:

```bash
python --version
```

Windows tizimida `python` buyrug'i mavjud bo'lmasa:

```powershell
py --version
```

## 2. Virtual muhit yaratish va faollashtirish

Terminalda `kino_bot` papkasiga o'ting:

```bash
cd kino_bot
```

Virtual muhit yarating:

```bash
python -m venv .venv
```

Uni faollashtiring.

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```bat
.venv\Scripts\activate.bat
```

macOS yoki Linux:

```bash
source .venv/bin/activate
```

## 3. Kutubxonalarni o'rnatish

Faol virtual muhitda kerakli kutubxonalarni o'rnating:

```bash
pip install -r requirements.txt
```

## 4. `.env` faylini sozlash

`kino_bot` papkasidagi `.env.example` faylini `.env` nomi bilan nusxalang.

macOS yoki Linux:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

`.env` faylini ochib qiymatlarni o'zingiznikiga almashtiring:

```dotenv
BOT_TOKEN=BotFather_dan_olingan_token
ADMIN_ID=123456789
CHANNELS=@kanal_username,@ikkinchi_kanal
DATABASE_PATH=kino_bot.db
```

Tokenni ommaviy repozitoriyga joylamang va boshqa odamlarga yubormang.

## 5. Telegram bot yaratish

1. Telegramda tasdiqlangan `@BotFather` akkauntini oching.
2. `/newbot` buyrug'ini yuboring.
3. Bot uchun ko'rsatiladigan nom va `bot` bilan tugaydigan username tanlang.
4. BotFather bergan tokenni `.env` faylidagi `BOT_TOKEN` qiymatiga kiriting.
5. BotFather bergan token maxfiy hisoblanadi; uni kodga yoki ommaviy faylga
   yozmang.

## 6. Botni kanallarga administrator qilish

Har bir majburiy obuna kanalida:

1. Kanal sozlamalarini oching.
2. Administratorlar bo'limidan bot username'ini qo'shing.
3. Botga kanal a'zolarini ko'rish uchun zarur administrator huquqlarini bering.

`get_chat_member` tekshiruvi ishonchli ishlashi uchun bot har bir kanalda
administrator bo'lishi kerak.

## 7. `ADMIN_ID` ni olish

Telegramda `@userinfobot` kabi akkaunt ID ko'rsatuvchi botdan o'z Telegram
raqamli ID'ingizni oling va `.env` ichidagi `ADMIN_ID` qiymatiga kiriting.
Bu botda admin paneldan faqat shu ID foydalana oladi.

## 8. `CHANNELS` ni sozlash

`.env` ichidagi `CHANNELS` qiymatiga barcha kanallarning public username'larini
vergul bilan ajratib yozing. `@` belgisini qoldiring va verguldan keyin
bo'sh joy qoldirmaslik mumkin:

```dotenv
CHANNELS=@kino_kanal,@yangiliklar_kanali
```

Har bir kanal uchun obuna tugmasi yaratiladi va bot foydalanuvchining a'zoligini
alohida tekshiradi. Tugmalar kanalning public `@username` manziliga bog'lanadi.

## 9. Botni ishga tushirish

Virtual muhit faolligini va `.env` to'g'ri sozlanganini tekshiring. `kino_bot`
papkasida quyidagini bajaring:

```bash
python bot.py
```

Bot Telegram bilan polling orqali bog'lanadi. SQLite bazasi birinchi ishga
tushishda `kino_bot.db` nomi bilan avtomatik yaratiladi.

## 10. Kino qo'shish

1. Bot bilan shaxsiy chatni oching va `/admin` buyrug'ini yuboring.
2. **➕ Kino qo'shish** tugmasini bosing.
3. Takrorlanmagan kino kodini yuboring.
4. Kino nomini yuboring.
5. Telegram video faylini yuboring, yoki `http://` / `https://` bilan
   boshlanadigan to'liq havolani yuboring.

Video yuborilganda bot uning `file_id` qiymatini, havola yuborilganda esa URL'ni
SQLite bazasiga saqlaydi. Kodlar katta-kichik harflarni farqlamaydi.
Bosqichni bekor qilish uchun `/cancel` yuboring.

## 11. Kino qidirish

Foydalanuvchi `/start` yuborib, majburiy kanallarga obuna bo'lishi kerak.
Obuna tasdiqlangach, botga kino kodini yuboring. Kod topilsa, bot kino nomi
bilan videosini yoki havolasini yuboradi; topilmasa, kino topilmagani haqida
xabar beradi.

## 12. Broadcast

1. Admin sifatida `/admin` yuboring.
2. **📢 Xabar yuborish** tugmasini bosing.
3. Tarqatmoqchi bo'lgan Telegram xabarini yuboring.

Bot xabarni bazadagi barcha `user_id` larga `copy_message` orqali nusxalaydi.
Matn, rasm, video, hujjat, audio, stiker va Telegram nusxalashni qo'llaydigan
boshqa xabar turlari shu usulda uzatiladi. Botni bloklagan foydalanuvchilar
yuborishni to'xtatmaydi; oxirida jami, yuborilgan va yuborilmagan xabarlar
soni ko'rsatiladi. Tarqatishni bekor qilish uchun `/cancel` yuboring.