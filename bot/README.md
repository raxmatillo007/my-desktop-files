## Telegram PPTX Bot (aiogram 3.x)

Bu loyiha **aiogram 3.x**, **python-pptx** va **Pexels API** yordamida ishlaydigan oddiy Telegram bot.
Bot siz yuborgan mavzu bo‘yicha slaydlar yaratadi va har bir slaydga internetdan rasm qo‘shadi.

### Bot ishlashi

1. `/start` yuborasiz → bot sizdan mavzuni so‘raydi.
2. Mavzuni yuborasiz (masalan: `Sun'iy intellekt`) → bot slaydlar sonini so‘raydi.
3. Slaydlar sonini yuborasiz (masalan: `10`) → bot `presentation.pptx` tayyorlab yuboradi.

### 1. Kerakli narsalar

- Python 3.10+ tavsiya qilinadi
- Telegram bot token (BotFather’dan)
- Pexels API kalit (rasmlar uchun)

### 2. Kutubxonalarni o‘rnatish

Terminalni shu papkada oching (masalan `C:\Users\Microsoft N\Desktop\bot`) va quyidagilarni bajaring:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

On Linux/macOS, activation looks like:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Set your bot token

On **Windows PowerShell**:

```powershell
$env:BOT_TOKEN = "8250278777:AAH48QXVN7ipKQNZLwnkBJqp42L6eO2p1BI"
```

On **Linux/macOS bash**:

```bash
export BOT_TOKEN="8250278777:AAH48QXVN7ipKQNZLwnkBJqp42L6eO2p1BI"
```

### 4. Pexels API kalitini qo‘yish

Pexels API key oling va `PEXELS_API_KEY` ga o‘rnating.

**Windows PowerShell**:

```powershell
$env:PEXELS_API_KEY = "qN8LhdjUN1zOjtXTVGhmce9VqmDGb7VKS8wyFttXnspnFoisfUmLCgdo"
```

**Linux/macOS bash**:

```bash
export PEXELS_API_KEY="YOUR_PEXELS_API_KEY_HERE"
```

### 5. OpenAI API kalitini qo‘yish (AI kontent uchun)

AI kontent generatsiya qilish uchun `OPENAI_API_KEY` kerak bo‘ladi.

**Windows PowerShell**:

```powershell
$env:OPENAI_API_KEY = "YOUR_OPENAI_API_KEY_HERE"
```

**Linux/macOS bash**:

```bash
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY_HERE"
```

Ixtiyoriy: model tanlash (default: `gpt-4o-mini`):

```powershell
$env:OPENAI_MODEL = "gpt-4o-mini"
```

### 6. Botni ishga tushirish

With the virtual environment activated and `BOT_TOKEN` set, run:

```bash
python main.py
```

You should see a message like:

```text
Bot is running. Press Ctrl+C to stop.
```

Telegram’da botingizni oching va:
- `/start` yuboring
- mavzu yuboring (masalan: `Sun'iy intellekt`)
- slaydlar sonini yuboring (masalan: `10`)
- tayyor `presentation.pptx` faylini olasiz

