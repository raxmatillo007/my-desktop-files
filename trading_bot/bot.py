"""
📊 Kripto Signal Boti — Python + python-telegram-bot
Manbalar: Binance API + CoinGecko API + TradingView Webhook
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

from signals import get_binance_signal, get_coingecko_data, format_signal_message
from webhook_server import start_webhook_server

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(","))) if os.getenv("ADMIN_IDS") else []

# Obunachi bazasi (produksiyada PostgreSQL/Redis ishlating)
subscribers = set()
watchlist = {}  # user_id -> [symbols]


# ─────────────────────────────────────────
# KOMANDALAR
# ─────────────────────────────────────────

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    subscribers.add(user.id)

    keyboard = [
        [InlineKeyboardButton("📈 Signal olish", callback_data="signal"),
         InlineKeyboardButton("💰 Narxlar", callback_data="prices")],
        [InlineKeyboardButton("📊 Tahlil", callback_data="analysis"),
         InlineKeyboardButton("⭐ Kuzatuv ro'yxati", callback_data="watchlist")],
        [InlineKeyboardButton("⚙️ Sozlamalar", callback_data="settings"),
         InlineKeyboardButton("ℹ️ Yordam", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"👋 Salom, {user.first_name}!\n\n"
        "📊 *Kripto Signal Botiga xush kelibsiz!*\n\n"
        "Men sizga quyidagilarni taqdim etaman:\n"
        "• 🔴🟢 Real vaqt savdo signallari\n"
        "• 📉 Texnik tahlil (RSI, MACD, MA)\n"
        "• 💹 Binance & CoinGecko narxlari\n"
        "• 🔔 TradingView webhook signallari\n"
        "• ⭐ Shaxsiy kuzatuv ro'yxati\n\n"
        "Quyidagi menyudan tanlang 👇",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def help_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Komandalar ro'yxati:*\n\n"
        "/start — Bosh menyu\n"
        "/signal `BTC` — BTC signali\n"
        "/price `ETH` — ETH narxi\n"
        "/analyze `SOL` — SOL tahlili\n"
        "/watch `BNB` — BNB kuzatuvga qo'shish\n"
        "/watchlist — Kuzatuv ro'yxatim\n"
        "/alert `BTC 70000` — Narx ogohlantirish\n"
        "/top10 — Top 10 kriptolar\n"
        "/fear — Fear & Greed indeksi\n\n"
        "💡 *Misol:* `/signal BTCUSDT`",
        parse_mode="Markdown"
    )


async def signal_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Bitta aktiv uchun signal"""
    symbol = ctx.args[0].upper() if ctx.args else "BTCUSDT"
    if not symbol.endswith("USDT"):
        symbol += "USDT"

    msg = await update.message.reply_text(f"⏳ {symbol} tahlil qilinmoqda...")

    try:
        signal_data = await get_binance_signal(symbol)
        text = format_signal_message(signal_data)
        await msg.edit_text(text, parse_mode="Markdown")
    except Exception as e:
        await msg.edit_text(f"❌ Xatolik: {symbol} ma'lumoti topilmadi.\nTo'g'ri format: `/signal BTCUSDT`")
        logger.error(f"Signal error for {symbol}: {e}")


async def price_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Joriy narx"""
    symbol = ctx.args[0].upper() if ctx.args else "BTC"
    coin_id = symbol.lower()

    msg = await update.message.reply_text(f"⏳ {symbol} narxi yuklanmoqda...")

    try:
        data = await get_coingecko_data(coin_id)
        price = data["market_data"]["current_price"]["usd"]
        change_24h = data["market_data"]["price_change_percentage_24h"]
        change_7d = data["market_data"]["price_change_percentage_7d"]
        volume = data["market_data"]["total_volume"]["usd"]
        market_cap = data["market_data"]["market_cap"]["usd"]

        emoji = "📈" if change_24h > 0 else "📉"
        sign = "+" if change_24h > 0 else ""

        await msg.edit_text(
            f"{emoji} *{symbol}/USDT*\n\n"
            f"💵 Narx: `${price:,.2f}`\n"
            f"24s: `{sign}{change_24h:.2f}%`\n"
            f"7k: `{'+' if change_7d > 0 else ''}{change_7d:.2f}%`\n"
            f"📦 Hajm (24s): `${volume:,.0f}`\n"
            f"🏦 Bozor qiymati: `${market_cap:,.0f}`\n\n"
            f"🔗 [CoinGecko]({data.get('links', {}).get('homepage', [''])[0]})",
            parse_mode="Markdown"
        )
    except Exception as e:
        await msg.edit_text(f"❌ {symbol} topilmadi. CoinGecko ID ni tekshiring.")
        logger.error(f"Price error: {e}")


async def analyze_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Chuqur texnik tahlil"""
    symbol = ctx.args[0].upper() if ctx.args else "BTCUSDT"
    if not symbol.endswith("USDT"):
        symbol += "USDT"

    msg = await update.message.reply_text(f"🔍 {symbol} chuqur tahlil qilinmoqda...\n⏳ 5-10 soniya kuting.")

    try:
        data = await get_binance_signal(symbol, detailed=True)
        text = format_signal_message(data, detailed=True)
        await msg.edit_text(text, parse_mode="Markdown")
    except Exception as e:
        await msg.edit_text(f"❌ Tahlil xatosi: {e}")


async def top10_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Top 10 kriptolar"""
    msg = await update.message.reply_text("⏳ Top 10 yuklanmoqda...")

    import aiohttp
    async with aiohttp.ClientSession() as session:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 10,
            "page": 1,
            "price_change_percentage": "24h"
        }
        async with session.get(url, params=params) as resp:
            coins = await resp.json()

    lines = ["🏆 *Top 10 Kripto (24s)*\n"]
    for i, coin in enumerate(coins, 1):
        change = coin["price_change_percentage_24h"] or 0
        emoji = "🟢" if change > 0 else "🔴"
        lines.append(
            f"{i}. {emoji} *{coin['symbol'].upper()}* — `${coin['current_price']:,.2f}` "
            f"({'+' if change > 0 else ''}{change:.2f}%)"
        )

    await msg.edit_text("\n".join(lines), parse_mode="Markdown")


async def fear_greed_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Fear & Greed indeksi"""
    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.alternative.me/fng/") as resp:
            data = await resp.json()

    value = int(data["data"][0]["value"])
    classification = data["data"][0]["value_classification"]

    if value <= 25:
        emoji, bar = "😱", "🔴🔴🔴🔴🔴"
    elif value <= 45:
        emoji, bar = "😨", "🟠🟠🟠⬜⬜"
    elif value <= 55:
        emoji, bar = "😐", "🟡🟡🟡🟡⬜"
    elif value <= 75:
        emoji, bar = "😏", "🟢🟢🟢🟢⬜"
    else:
        emoji, bar = "🤑", "🟢🟢🟢🟢🟢"

    warning = ""
    if value <= 25:
        warning = "\n⚠️ Ekstremal qo'rquv — Potensial xarid imkoniyati!"
    elif value >= 75:
        warning = "\n🚨 Ekstremal ochko'zlik — Ehtiyot bo'ling!"

    await update.message.reply_text(
        f"{emoji} *Fear & Greed Indeksi*\n\n"
        f"Qiymat: `{value}/100`\n"
        f"Holat: *{classification}*\n\n"
        f"{bar}{warning}",
        parse_mode="Markdown"
    )


async def watch_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Kuzatuv ro'yxatiga qo'shish"""
    user_id = update.effective_user.id
    symbol = ctx.args[0].upper() if ctx.args else None

    if not symbol:
        await update.message.reply_text("❌ Format: `/watch BTCUSDT`", parse_mode="Markdown")
        return

    if not symbol.endswith("USDT"):
        symbol += "USDT"

    if user_id not in watchlist:
        watchlist[user_id] = []

    if symbol not in watchlist[user_id]:
        if len(watchlist[user_id]) >= 10:
            await update.message.reply_text("❌ Maksimal 10 ta aktiv kuzatish mumkin.")
            return
        watchlist[user_id].append(symbol)
        await update.message.reply_text(f"✅ *{symbol}* kuzatuv ro'yxatiga qo'shildi!", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"ℹ️ {symbol} allaqachon ro'yxatda.")


async def watchlist_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Kuzatuv ro'yxatini ko'rish"""
    user_id = update.effective_user.id
    symbols = watchlist.get(user_id, [])

    if not symbols:
        await update.message.reply_text(
            "📋 Kuzatuv ro'yxatingiz bo'sh.\n`/watch BTCUSDT` bilan qo'shing.",
            parse_mode="Markdown"
        )
        return

    msg = await update.message.reply_text("⏳ Ro'yxat yangilanmoqda...")
    lines = ["⭐ *Kuzatuv ro'yxatingiz:*\n"]

    for sym in symbols:
        try:
            data = await get_binance_signal(sym)
            change = data.get("change_24h", 0)
            price = data.get("price", 0)
            emoji = "🟢" if change > 0 else "🔴"
            lines.append(f"{emoji} *{sym}*: `${price:,.2f}` ({'+' if change>0 else ''}{change:.2f}%)")
        except:
            lines.append(f"⚠️ {sym}: ma'lumot yo'q")

    keyboard = [[InlineKeyboardButton("🔄 Yangilash", callback_data="refresh_watchlist")]]
    await msg.edit_text(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ─────────────────────────────────────────
# INLINE TUGMALAR
# ─────────────────────────────────────────

async def button_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "signal":
        keyboard = [
            [InlineKeyboardButton("BTC", callback_data="sig_BTCUSDT"),
             InlineKeyboardButton("ETH", callback_data="sig_ETHUSDT"),
             InlineKeyboardButton("BNB", callback_data="sig_BNBUSDT")],
            [InlineKeyboardButton("SOL", callback_data="sig_SOLUSDT"),
             InlineKeyboardButton("XRP", callback_data="sig_XRPUSDT"),
             InlineKeyboardButton("ADA", callback_data="sig_ADAUSDT")],
        ]
        await query.edit_message_text(
            "📊 *Qaysi aktiv uchun signal?*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data.startswith("sig_"):
        symbol = query.data[4:]
        await query.edit_message_text(f"⏳ {symbol} tahlil qilinmoqda...")
        try:
            data = await get_binance_signal(symbol)
            text = format_signal_message(data)
            keyboard = [[InlineKeyboardButton("🔄 Yangilash", callback_data=f"sig_{symbol}"),
                         InlineKeyboardButton("📋 Chuqur tahlil", callback_data=f"deep_{symbol}")]]
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception as e:
            await query.edit_message_text(f"❌ Xatolik: {e}")

    elif query.data.startswith("deep_"):
        symbol = query.data[5:]
        await query.edit_message_text(f"🔍 {symbol} chuqur tahlil...")
        try:
            data = await get_binance_signal(symbol, detailed=True)
            text = format_signal_message(data, detailed=True)
            await query.edit_message_text(text, parse_mode="Markdown")
        except Exception as e:
            await query.edit_message_text(f"❌ Xatolik: {e}")

    elif query.data == "prices":
        await top10_command(update, ctx)

    elif query.data == "help":
        await query.edit_message_text(
            "📖 Komandalar: /signal, /price, /analyze, /top10, /fear, /watch, /watchlist",
            parse_mode="Markdown"
        )


# ─────────────────────────────────────────
# AVTOMATIK SIGNALLAR (Scheduler)
# ─────────────────────────────────────────

async def send_daily_signals(app: Application):
    """Har kuni ertalab 9:00 da signal yuborish"""
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

    for user_id in subscribers:
        try:
            lines = ["🌅 *Kunlik Signal Hisoboti*\n"]
            for sym in symbols:
                data = await get_binance_signal(sym)
                signal = data.get("signal", "HOLD")
                price = data.get("price", 0)
                emoji = "🟢" if signal == "BUY" else ("🔴" if signal == "SELL" else "🟡")
                lines.append(f"{emoji} *{sym}*: `${price:,.2f}` — **{signal}**")

            await app.bot.send_message(
                chat_id=user_id,
                text="\n".join(lines),
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Daily signal error for {user_id}: {e}")


async def send_watchlist_updates(app: Application):
    """Har 4 soatda kuzatuv ro'yxati yangilanishi"""
    for user_id, symbols in watchlist.items():
        if not symbols:
            continue
        try:
            lines = ["🔔 *Kuzatuv Yangilanishi*\n"]
            for sym in symbols:
                data = await get_binance_signal(sym)
                change = data.get("change_24h", 0)
                price = data.get("price", 0)
                signal = data.get("signal", "HOLD")
                if abs(change) > 3 or signal != "HOLD":  # Muhim o'zgarishlarda xabar
                    emoji = "🚨" if abs(change) > 5 else "⚠️"
                    lines.append(f"{emoji} *{sym}*: `${price:,.2f}` ({change:+.2f}%) — {signal}")

            if len(lines) > 1:
                await app.bot.send_message(chat_id=user_id, text="\n".join(lines), parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Watchlist update error: {e}")


# ─────────────────────────────────────────
# ASOSIY ISHGA TUSHIRISH
# ─────────────────────────────────────────

def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN .env faylida yo'q!")

    app = Application.builder().token(BOT_TOKEN).build()

    # Komanda handlerlari
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("signal", signal_command))
    app.add_handler(CommandHandler("price", price_command))
    app.add_handler(CommandHandler("analyze", analyze_command))
    app.add_handler(CommandHandler("top10", top10_command))
    app.add_handler(CommandHandler("fear", fear_greed_command))
    app.add_handler(CommandHandler("watch", watch_command))
    app.add_handler(CommandHandler("watchlist", watchlist_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    # Scheduler — avtomatik signallar
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_daily_signals, "cron", hour=9, minute=0, args=[app])
    scheduler.add_job(send_watchlist_updates, "interval", hours=4, args=[app])
    scheduler.start()

    # TradingView webhook serveri alohida thread da
    import threading
    webhook_thread = threading.Thread(
        target=start_webhook_server,
        args=(app, subscribers),
        daemon=True
    )
    webhook_thread.start()

    logger.info("✅ Bot ishga tushdi!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
