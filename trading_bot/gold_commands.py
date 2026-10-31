"""
gold_commands.py — Bot uchun Gold komandalar va scheduler
bot.py ga shu modulni import qiling
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, Application
import logging
from gold_analyzer import analyze_gold, format_gold_message

logger = logging.getLogger(__name__)

# Foydalanuvchi sozlamalari (produksiyada DB ga saqlang)
gold_subscribers = set()   # Gold signallariga obuna bo'lganlar
gold_alerts = {}           # user_id -> {"above": price, "below": price}
last_gold_signal = {}      # Oxirgi signal (takrorlanmaslik uchun)


# ──────────────────────────────────────────────
# KOMANDALAR
# ──────────────────────────────────────────────

async def gold_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """/gold — To'liq Gold tahlili"""
    msg = await update.message.reply_text(
        "⏳ *XAU/USD tahlil qilinmoqda...*\n"
        "9 ta strategiya tekshirilmoqda, iltimos kuting...",
        parse_mode="Markdown"
    )
    try:
        data = await analyze_gold("5min")
        text = format_gold_message(data)

        keyboard = [
            [InlineKeyboardButton("🔄 Yangilash", callback_data="gold_refresh"),
             InlineKeyboardButton("⏱️ 15m Tahlil", callback_data="gold_15m")],
            [InlineKeyboardButton("🔔 Obuna", callback_data="gold_subscribe"),
             InlineKeyboardButton("📊 Faqat signal", callback_data="gold_signal_only")],
        ]
        await msg.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        await msg.edit_text(
            f"❌ Xatolik: {e}\n\n"
            "💡 `.env` faylda `TWELVE_DATA_KEY` borligini tekshiring.\n"
            "Bepul kalit: https://twelvedata.com"
        )
        logger.error(f"Gold command error: {e}")


async def gold_signal_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """/goldsignal — Faqat signal va savdo rejasi (qisqacha)"""
    msg = await update.message.reply_text("⏳ Signal tekshirilmoqda...")
    try:
        data = await analyze_gold("5min")
        if not data["confirmed"]:
            await msg.edit_text(
                f"🟡 *XAU/USD — Signal yo'q*\n\n"
                f"💵 Narx: `${data['price']:,.3f}`\n"
                f"📊 Ball: `{data['total_score']}/{data['max_score']}`\n"
                f"✅ Tasdiqlagan: `{data['confirming_count']}/9` strategiya\n\n"
                f"⏳ Bozor signal bermaydi, kuting...\n"
                f"Trend: {data['trend']}",
                parse_mode="Markdown"
            )
        else:
            text = (
                f"🥇 *XAU/USD SIGNAL*\n\n"
                f"💵 `${data['price']:,.3f}` | {data['trend']}\n"
                f"🎯 *{data['signal']}* — {data['strength']}\n"
                f"📊 Ishonch: `{data['confidence']}` ({data['confirming_count']}/9)\n\n"
                f"🔵 Kirish: `${data['entry']:,.3f}`\n"
                f"🛑 SL: `${data['stop_loss']:,.3f}`\n"
                f"🎯 TP1: `${data['tp1']:,.3f}`\n"
                f"🎯 TP2: `${data['tp2']:,.3f}`\n"
                f"🎯 TP3: `${data['tp3']:,.3f}`\n"
                f"⚖️ R/R: `1:{data['rr_ratio']}`\n\n"
                f"🕯️ {data['pattern']}"
            )
            await msg.edit_text(text, parse_mode="Markdown")
    except Exception as e:
        await msg.edit_text(f"❌ Xatolik: {e}")


async def gold_subscribe_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """/goldsubscribe — Avtomatik signallarga obuna"""
    user_id = update.effective_user.id
    if user_id in gold_subscribers:
        gold_subscribers.discard(user_id)
        await update.message.reply_text(
            "🔕 Gold signallaridan obuna bekor qilindi.\n"
            "Qayta ulash: /goldsubscribe"
        )
    else:
        gold_subscribers.add(user_id)
        await update.message.reply_text(
            "✅ *Gold signallariga obuna bo'ldingiz!*\n\n"
            "Har 5 daqiqada tahlil qilinadi.\n"
            "Signal TASDIQLANGANDA sizga avtomatik yuboriladi.\n\n"
            "Bekor qilish: /goldsubscribe (qayta bosing)",
            parse_mode="Markdown"
        )


async def gold_alert_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """/goldalert 2050 2100 — Narx ogohlantirish"""
    args = ctx.args
    if len(args) < 1:
        await update.message.reply_text(
            "📌 Format:\n"
            "`/goldalert 2050` — narx $2050 ga tegsa xabar\n"
            "`/goldalert 2050 2100` — past va yuqori chegara",
            parse_mode="Markdown"
        )
        return

    user_id = update.effective_user.id
    try:
        below = float(args[0]) if len(args) >= 1 else None
        above = float(args[1]) if len(args) >= 2 else None
        gold_alerts[user_id] = {"below": below, "above": above}
        await update.message.reply_text(
            f"🔔 *Ogohlantirish o'rnatildi:*\n"
            f"{'⬇️ Past chegara: $' + str(below) if below else ''}\n"
            f"{'⬆️ Yuqori chegara: $' + str(above) if above else ''}",
            parse_mode="Markdown"
        )
    except ValueError:
        await update.message.reply_text("❌ Narx noto'g'ri formatda. Misol: `/goldalert 2050`")


# ──────────────────────────────────────────────
# INLINE TUGMALAR
# ──────────────────────────────────────────────

async def gold_button_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "gold_refresh":
        await query.edit_message_text("⏳ Yangilanmoqda...", parse_mode="Markdown")
        try:
            data = await analyze_gold("5min")
            text = format_gold_message(data)
            keyboard = [
                [InlineKeyboardButton("🔄 Yangilash", callback_data="gold_refresh"),
                 InlineKeyboardButton("⏱️ 15m", callback_data="gold_15m")],
                [InlineKeyboardButton("🔔 Obuna", callback_data="gold_subscribe"),
                 InlineKeyboardButton("📊 Qisqa", callback_data="gold_signal_only")],
            ]
            await query.edit_message_text(text, parse_mode="Markdown",
                                          reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception as e:
            await query.edit_message_text(f"❌ {e}")

    elif query.data == "gold_15m":
        await query.edit_message_text("⏳ 15m tahlil qilinmoqda...")
        try:
            data = await analyze_gold("15min")
            text = format_gold_message(data)
            keyboard = [[InlineKeyboardButton("🔄", callback_data="gold_refresh"),
                         InlineKeyboardButton("5m ga qayt", callback_data="gold_refresh")]]
            await query.edit_message_text(text, parse_mode="Markdown",
                                          reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception as e:
            await query.edit_message_text(f"❌ {e}")

    elif query.data == "gold_subscribe":
        user_id = query.from_user.id
        if user_id in gold_subscribers:
            gold_subscribers.discard(user_id)
            await query.answer("🔕 Obuna bekor qilindi", show_alert=True)
        else:
            gold_subscribers.add(user_id)
            await query.answer("✅ Gold signallariga obuna bo'ldingiz!", show_alert=True)

    elif query.data == "gold_signal_only":
        try:
            data = await analyze_gold("5min")
            if not data["confirmed"]:
                await query.answer("🟡 Hozircha signal yo'q, kuting...", show_alert=True)
            else:
                text = (f"🎯 {data['signal']} | 💵 ${data['price']:,.3f}\n"
                        f"SL: ${data['stop_loss']:,.3f} | TP1: ${data['tp1']:,.3f}")
                await query.answer(text, show_alert=True)
        except Exception as e:
            await query.answer(f"❌ {e}", show_alert=True)


# ──────────────────────────────────────────────
# AVTOMATIK SIGNAL SCHEDULER
# ──────────────────────────────────────────────

async def auto_gold_scanner(app: Application):
    """
    Har 5 daqiqada Gold skanerlash.
    Faqat TASDIQLANGAN signal bo'lsa yuboriladi.
    Bir xil signal qayta-qayta yuborilmaydi.
    """
    if not gold_subscribers:
        return

    try:
        data = await analyze_gold("5min")

        if not data["confirmed"]:
            return  # Signal yo'q — jim turish

        signal_key = f"{data['signal']}_{int(data['price'])}"

        # Oldingi signal bilan bir xil bo'lsa yuborma
        for user_id in list(gold_subscribers):
            if last_gold_signal.get(user_id) == signal_key:
                continue

            try:
                text = format_gold_message(data)
                text = "🔔 *AVTOMATIK SIGNAL!*\n\n" + text
                keyboard = [[
                    InlineKeyboardButton("🔄 Yangilash", callback_data="gold_refresh")
                ]]
                await app.bot.send_message(
                    chat_id=user_id,
                    text=text,
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                last_gold_signal[user_id] = signal_key

            except Exception as e:
                logger.error(f"Auto signal error for {user_id}: {e}")

    except Exception as e:
        logger.error(f"Gold scanner error: {e}")


async def check_gold_price_alerts(app: Application):
    """Narx ogohlantirishi tekshiruvi — har daqiqada"""
    if not gold_alerts:
        return
    try:
        data = await analyze_gold("5min")
        price = data["price"]

        for user_id, alert in list(gold_alerts.items()):
            triggered = False
            msg = f"🔔 *Gold Narx Ogohlantirishi!*\n💵 Joriy narx: `${price:,.3f}`\n"

            if alert.get("below") and price <= alert["below"]:
                msg += f"⬇️ Narx ${alert['below']} dan tushdi!"
                triggered = True
            elif alert.get("above") and price >= alert["above"]:
                msg += f"⬆️ Narx ${alert['above']} dan oshdi!"
                triggered = True

            if triggered:
                await app.bot.send_message(chat_id=user_id, text=msg, parse_mode="Markdown")
                del gold_alerts[user_id]  # Bir marta ogohlantir

    except Exception as e:
        logger.error(f"Alert check error: {e}")
