"""
trade_confirm.py — Yarim avtomatik savdo tizimi
1. Bot tahlil qiladi
2. Telegram da "TASDIQLASH / BEKOR" tugmalari ko'rinadi
3. Siz "HA" desangiz → MT5 ga avtomatik order yuboriladi
4. "YO'Q" desangiz → o'tkazib yuboriladi
"""

import json
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, Application

from gold_analyzer import analyze_gold, format_gold_message
from mt5_trader import (
    place_order, close_position, get_open_positions,
    get_account_info, calculate_lot, get_trade_history
)

logger = logging.getLogger(__name__)

# Kutayotgan tasdiqlar: {callback_key: trade_data}
pending_trades = {}


# ══════════════════════════════════════════════════════
# TAHLIL + TAKLIF YUBORISH
# ══════════════════════════════════════════════════════

async def send_trade_proposal(app: Application, user_id: int):
    """
    Gold tahlil qilib, foydalanuvchiga tasdiqlash uchun yuborish
    """
    try:
        # Hisob ma'lumotlari
        account = get_account_info()
        if not account:
            await app.bot.send_message(
                chat_id=user_id,
                text="❌ MT5 ga ulanib bo'lmadi. Hisobingizni tekshiring."
            )
            return

        balance = account["balance"]

        # Tahlil
        data = await analyze_gold("5min")

        if not data["confirmed"]:
            await app.bot.send_message(
                chat_id=user_id,
                text=(
                    f"🟡 *Signal yo'q — Kuting*\n\n"
                    f"💵 XAU/USD: `${data['price']:,.3f}`\n"
                    f"📊 Ball: `{data['total_score']}/{data['max_score']}`\n"
                    f"✅ Tasdiqlagan: `{data['confirming_count']}/9`\n\n"
                    f"Kamida 5 strategiya tasdiqlaganda taklif yuboriladi."
                ),
                parse_mode="Markdown"
            )
            return

        # Lot hisoblash (balansning 1% xavf)
        sl_points = abs(data["price"] - data["stop_loss"])
        lot = calculate_lot(balance, risk_pct=1.0, sl_points=sl_points)

        # Kutilgan foyda/zarar
        risk_usd   = round(lot * sl_points * 100, 2)
        reward_usd = round(risk_usd * data["rr_ratio"], 2)

        direction = "BUY" if "BUY" in data["signal"] else "SELL"

        # Callback key (noyob)
        key = f"trade_{user_id}_{int(datetime.now().timestamp())}"
        pending_trades[key] = {
            "direction": direction,
            "lot":       lot,
            "entry":     data["entry"],
            "sl":        data["stop_loss"],
            "tp":        data["tp1"],
            "tp2":       data["tp2"],
            "tp3":       data["tp3"],
            "signal_data": {
                "score":       data["total_score"],
                "confidence":  data["confidence"],
                "confirming":  data["confirming_count"],
                "trend":       data["trend"],
                "pattern":     data["pattern"],
            }
        }

        direction_emoji = "🟢" if direction == "BUY" else "🔴"

        proposal_text = (
            f"🔔 *SAVDO TAKLIFI — TASDIQLANG!*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🥇 *XAU/USD (Gold)*\n"
            f"{direction_emoji} Yo'nalish: *{direction}*\n"
            f"💵 Kirish narxi: `${data['entry']:,.3f}`\n\n"
            f"🛑 Stop-Loss: `${data['stop_loss']:,.3f}`\n"
            f"🎯 TP1: `${data['tp1']:,.3f}`\n"
            f"🎯 TP2: `${data['tp2']:,.3f}`\n"
            f"🎯 TP3: `${data['tp3']:,.3f}`\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💼 *Lot:* `{lot}` (Balansning 1% xavfi)\n"
            f"📉 Maksimal zarar: `${risk_usd}`\n"
            f"📈 Kutilgan foyda (TP1): `${reward_usd}`\n"
            f"⚖️ Risk/Reward: `1:{data['rr_ratio']}`\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 *Tahlil natijalari:*\n"
            f"• Ball: `{data['total_score']}/{data['max_score']}`\n"
            f"• Ishonch: `{data['confidence']}`\n"
            f"• Tasdiqlagan: `{data['confirming_count']}/9` strategiya\n"
            f"• Trend: {data['trend']}\n"
            f"• Shamdon: {data['pattern']}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 *Hisob:* `${balance:,.2f}` | Leverage: `1:{account['leverage']}`\n\n"
            f"⏳ *30 soniya ichida javob bering!*"
        )

        keyboard = [
            [
                InlineKeyboardButton("✅ HA — Savdoga kir", callback_data=f"confirm_{key}"),
                InlineKeyboardButton("❌ YO'Q — O'tkazib yubor", callback_data=f"reject_{key}"),
            ],
            [
                InlineKeyboardButton("📊 To'liq tahlil ko'rish", callback_data="gold_refresh"),
            ]
        ]

        await app.bot.send_message(
            chat_id=user_id,
            text=proposal_text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    except Exception as e:
        logger.error(f"Trade proposal error: {e}")
        await app.bot.send_message(
            chat_id=user_id,
            text=f"❌ Tahlilda xato: {e}"
        )


# ══════════════════════════════════════════════════════
# TASDIQLASH / BEKOR QILISH HANDLER
# ══════════════════════════════════════════════════════

async def trade_callback_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # ── TASDIQLASH ──
    if data.startswith("confirm_"):
        key = data[8:]
        trade = pending_trades.get(key)

        if not trade:
            await query.edit_message_text("⏰ Muddati o'tdi yoki allaqachon bajarildi.")
            return

        del pending_trades[key]

        await query.edit_message_text(
            f"⏳ Order MT5 ga yuborilmoqda...\n"
            f"{trade['direction']} {trade['lot']} lot @ ${trade['entry']:,.3f}"
        )

        result = place_order(
            direction=trade["direction"],
            lot=trade["lot"],
            sl_price=trade["sl"],
            tp_price=trade["tp"],
            comment=f"TBot_{trade['signal_data']['confidence']}"
        )

        if result["success"]:
            # Ochiq pozitsiyani saqlash
            ctx.bot_data.setdefault("open_orders", {})[result["order_id"]] = {
                **trade,
                "order_id":  result["order_id"],
                "open_time": datetime.now().strftime("%H:%M:%S"),
                "open_price": result["price"],
                "user_id":   query.from_user.id,
            }

            keyboard = [[
                InlineKeyboardButton(
                    f"🚫 Pozitsiyani yop #{result['order_id']}",
                    callback_data=f"close_{result['order_id']}"
                )
            ]]

            await query.edit_message_text(
                f"✅ *ORDER OCHILDI!*\n\n"
                f"🎫 Ticket: `#{result['order_id']}`\n"
                f"{'🟢' if trade['direction']=='BUY' else '🔴'} {trade['direction']} "
                f"`{trade['lot']}` lot\n"
                f"💵 Kirish: `${result['price']:,.3f}`\n"
                f"🛑 SL: `${trade['sl']:,.3f}`\n"
                f"🎯 TP1: `${trade['tp']:,.3f}`\n\n"
                f"📲 Natija kelganda xabar beraman!",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await query.edit_message_text(
                f"❌ *Order yuborishda xato!*\n\n"
                f"`{result['message']}`\n\n"
                f"MT5 da ulanishni tekshiring.",
                parse_mode="Markdown"
            )

    # ── BEKOR QILISH ──
    elif data.startswith("reject_"):
        key = data[7:]
        trade = pending_trades.pop(key, None)
        direction = trade["direction"] if trade else "—"
        await query.edit_message_text(
            f"❌ *Savdo o'tkazib yuborildi*\n\n"
            f"Yo'nalish: {direction}\n"
            f"Keyingi signal kelganda yana xabar beraman. 👍",
            parse_mode="Markdown"
        )

    # ── POZITSIYANI YOP ──
    elif data.startswith("close_"):
        ticket = int(data[6:])
        await query.edit_message_text(f"⏳ Pozitsiya #{ticket} yopilmoqda...")
        result = close_position(ticket)

        if result["success"]:
            await query.edit_message_text(
                f"✅ *Pozitsiya yopildi!*\n\n"
                f"🎫 Ticket: `#{ticket}`\n"
                f"💵 Yopilish narxi: `${result.get('price', 0):,.3f}`\n\n"
                f"Natijani /history dan ko'ring.",
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text(
                f"❌ Yopishda xato: `{result['message']}`",
                parse_mode="Markdown"
            )


# ══════════════════════════════════════════════════════
# KOMANDALAR
# ══════════════════════════════════════════════════════

async def account_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """/account — MT5 hisob ma'lumotlari"""
    info = get_account_info()
    if not info:
        await update.message.reply_text("❌ MT5 ga ulanib bo'lmadi. `.env` ni tekshiring.")
        return

    profit_emoji = "📈" if info["profit"] >= 0 else "📉"
    await update.message.reply_text(
        f"💼 *MT5 Hisob Ma'lumotlari*\n\n"
        f"👤 Ism: `{info['name']}`\n"
        f"🔢 Login: `{info['login']}`\n"
        f"🌐 Server: `{info['server']}`\n\n"
        f"💰 Balans: `${info['balance']:,.2f}`\n"
        f"📊 Kapital: `${info['equity']:,.2f}`\n"
        f"🔒 Margin: `${info['margin']:,.2f}`\n"
        f"✅ Erkin margin: `${info['free_margin']:,.2f}`\n"
        f"{profit_emoji} Joriy foyda: `${info['profit']:,.2f}`\n"
        f"⚡ Leverage: `1:{info['leverage']}`\n"
        f"💱 Valyuta: `{info['currency']}`",
        parse_mode="Markdown"
    )


async def positions_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """/positions — Ochiq pozitsiyalar"""
    positions = get_open_positions()

    if not positions:
        await update.message.reply_text(
            "📋 *Ochiq pozitsiyalar yo'q*\n\n"
            "Yangi signal uchun /goldtrade yozing.",
            parse_mode="Markdown"
        )
        return

    total_profit = sum(p["profit"] for p in positions)
    lines = [f"📂 *Ochiq pozitsiyalar ({len(positions)} ta):*\n"]

    keyboard_buttons = []
    for p in positions:
        emoji = "🟢" if p["type"] == "BUY" else "🔴"
        profit_emoji = "📈" if p["profit"] >= 0 else "📉"
        lines.append(
            f"{emoji} *#{p['ticket']}* — {p['type']} `{p['lot']}` lot\n"
            f"   Kirish: `${p['open_price']:,.3f}` | Hozir: `${p['current_price']:,.3f}`\n"
            f"   SL: `${p['sl']:,.3f}` | TP: `${p['tp']:,.3f}`\n"
            f"   {profit_emoji} Foyda: `${p['profit']:,.2f}` | {p['open_time']}\n"
        )
        keyboard_buttons.append([
            InlineKeyboardButton(
                f"🚫 #{p['ticket']} yop",
                callback_data=f"close_{p['ticket']}"
            )
        ])

    total_emoji = "📈" if total_profit >= 0 else "📉"
    lines.append(f"\n{total_emoji} *Jami foyda: `${total_profit:,.2f}`*")

    await update.message.reply_text(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard_buttons) if keyboard_buttons else None
    )


async def history_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """/history — Oxirgi 7 kunlik savdolar"""
    trades = get_trade_history(days=7)

    if not trades:
        await update.message.reply_text("📋 So'nggi 7 kunda savdo yo'q.")
        return

    total = sum(t["profit"] for t in trades)
    wins  = sum(1 for t in trades if t["profit"] > 0)
    losses = len(trades) - wins
    win_rate = round(wins / len(trades) * 100) if trades else 0

    lines = [
        f"📊 *Savdo Tarixi (7 kun)*\n",
        f"📈 Jami: `{len(trades)}` ta savdo",
        f"✅ G'alaba: `{wins}` | ❌ Zarar: `{losses}`",
        f"🎯 Win Rate: `{win_rate}%`",
        f"{'📈' if total>=0 else '📉'} Jami foyda: `${total:,.2f}`\n",
        f"━━━━━━━━━━━━━━━━━━━━━━",
    ]

    for t in reversed(trades[-10:]):
        emoji = "✅" if t["profit"] > 0 else "❌"
        d_emoji = "🟢" if t["type"] == "BUY" else "🔴"
        lines.append(
            f"{emoji} {d_emoji} {t['type']} | `${t['price']:,.3f}` | "
            f"{'+'if t['profit']>0 else ''}{t['profit']:.2f}$ | {t['time']}"
        )

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def goldtrade_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """/goldtrade — Gold tahlil va savdo taklifi"""
    user_id = update.effective_user.id
    await update.message.reply_text("⏳ Gold tahlil qilinmoqda, iltimos kuting...")
    await send_trade_proposal(ctx.application, user_id)
