"""
webhook_server.py — TradingView signallarini qabul qilish
Flask orqali HTTP server
"""

from flask import Flask, request, jsonify
import asyncio
import logging
import os

logger = logging.getLogger(__name__)

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "my_secret_token")

app_flask = Flask(__name__)

_tg_app = None
_subscribers = set()


def start_webhook_server(tg_app, subscribers, port: int = 8080):
    global _tg_app, _subscribers
    _tg_app = tg_app
    _subscribers = subscribers
    logger.info(f"🌐 Webhook server port {port} da ishga tushdi")
    app_flask.run(host="0.0.0.0", port=port, debug=False)


@app_flask.route("/webhook", methods=["POST"])
def tradingview_webhook():
    """
    TradingView Alert formati:
    {
      "secret": "my_secret_token",
      "symbol": "BTCUSDT",
      "signal": "BUY",
      "price": "68500",
      "message": "RSI oversold + MACD bullish cross"
    }
    """
    data = request.json
    if not data:
        return jsonify({"error": "JSON kerak"}), 400

    # Secret tekshirish
    if data.get("secret") != WEBHOOK_SECRET:
        logger.warning("Webhook: noto'g'ri secret!")
        return jsonify({"error": "Ruxsat yo'q"}), 403

    symbol  = data.get("symbol", "UNKNOWN")
    signal  = data.get("signal", "UNKNOWN").upper()
    price   = data.get("price", "N/A")
    message = data.get("message", "")
    timeframe = data.get("timeframe", "")

    # Emoji
    if signal == "BUY":
        emoji = "🟢"
    elif signal == "SELL":
        emoji = "🔴"
    else:
        emoji = "🟡"

    text = (
        f"🔔 *TradingView Signal!*\n\n"
        f"{emoji} *{signal}* — `{symbol}`\n"
        f"💵 Narx: `${float(price):,.4f}`\n"
        f"⏱️ Timeframe: `{timeframe}`\n"
        f"📝 {message}\n\n"
        f"⚠️ _Ta'lim maqsadida_"
    )

    # Barcha obunachilaringga yuborish
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def send_all():
        for user_id in list(_subscribers):
            try:
                await _tg_app.bot.send_message(
                    chat_id=user_id,
                    text=text,
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.error(f"Webhook yuborish xatosi {user_id}: {e}")

    loop.run_until_complete(send_all())
    loop.close()

    logger.info(f"Webhook signal yuborildi: {symbol} {signal} @ {price}")
    return jsonify({"status": "ok", "sent_to": len(_subscribers)}), 200


@app_flask.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "running", "subscribers": len(_subscribers)}), 200


@app_flask.route("/", methods=["GET"])
def index():
    return jsonify({
        "bot": "Kripto Signal Bot",
        "webhook": "/webhook (POST)",
        "health": "/health (GET)"
    }), 200
