# 📊 Kripto + Gold Signal Boti (MT5 ulangan)

## 📁 Fayl tuzilmasi
```
trading_bot/
├── bot.py              ← Asosiy bot
├── signals.py          ← Kripto tahlil (Binance/CoinGecko)
├── gold_analyzer.py    ← Gold tahlil (9 strategiya)
├── gold_commands.py    ← Gold Telegram komandalar
├── mt5_trader.py       ← MT5 ulanish va order yuborish
├── trade_confirm.py    ← Yarim avtomatik savdo tizimi
├── webhook_server.py   ← TradingView webhook
├── requirements.txt
└── .env
```

## 🚀 Ishga tushirish

### 1. O'rnatish
```bash
pip install -r requirements.txt
cp .env.example .env
# .env ni to'ldiring
```

### ⚠️ MUHIM: MT5 faqat Windows da ishlaydi!
MetaTrader5 Python kutubxonasi faqat Windows OS da ishlaydi.
Linux/Mac uchun Windows VPS ijaraga oling.

### 2. MT5 sozlash
1. MT5 dasturini oching
2. Tools → Options → Expert Advisors →
   ✅ "Allow automated trading" belgilang
   ✅ "Allow DLL imports" belgilang
3. .env ga login/password/server kiriting

### 3. Botni ishga tushirish
```bash
python bot.py
```

## 🤖 Komandalar

| Komanda | Tavsif |
|---------|--------|
| `/gold` | To'liq Gold tahlili |
| `/goldtrade` | Tahlil + Savdo taklifi |
| `/goldsignal` | Qisqa signal |
| `/goldsubscribe` | Avtomatik signal |
| `/goldalert 2050` | Narx ogohlantirish |
| `/account` | MT5 hisob holati |
| `/positions` | Ochiq pozitsiyalar |
| `/history` | Savdo tarixi |
| `/signal BTCUSDT` | Kripto signal |
| `/top10` | Top 10 kripto |
| `/fear` | Fear & Greed |

## 🔄 Yarim avtomatik savdo qanday ishlaydi?

```
1. /goldtrade yozing
         ↓
2. Bot 9 strategiya tahlil qiladi
         ↓
3. Telegram da taklif keladi:
   ✅ HA — Savdoga kir
   ❌ YO'Q — O'tkazib yubor
         ↓
4. "HA" bosasiz → MT5 ga order yuboriladi
         ↓
5. SL/TP avtomatik o'rnatiladi
         ↓
6. Natija kelganda xabar beradi
```

## ⚠️ Muhim eslatmalar
- Demo hisob bilan sinab ko'ring!
- Minimal balans: $100 (0.01 lot)
- Risk: har savdoda balansning 1%
- Bu ta'lim maqsadida — o'z xavfingizda foydalaning
