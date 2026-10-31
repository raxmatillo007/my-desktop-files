"""
mt5_trader.py — MetaTrader 5 ulanish va savdo moduli
Yarim avtomatik: Bot tahlil qiladi → Telegram da tasdiqlaysiz → MT5 ga order yuboriladi
"""

import MetaTrader5 as mt5
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

MT5_LOGIN    = int(os.getenv("MT5_LOGIN", "0"))
MT5_PASSWORD = os.getenv("MT5_PASSWORD", "")
MT5_SERVER   = os.getenv("MT5_SERVER", "")  # Masalan: "ICMarkets-Demo"

SYMBOL = "XAUUSD"


# ══════════════════════════════════════════════════════
# ULANISH
# ══════════════════════════════════════════════════════

def connect_mt5() -> bool:
    if not mt5.initialize():
        logger.error(f"MT5 initialize xatosi: {mt5.last_error()}")
        return False

    authorized = mt5.login(MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER)
    if not authorized:
        logger.error(f"MT5 login xatosi: {mt5.last_error()}")
        mt5.shutdown()
        return False

    info = mt5.account_info()
    logger.info(f"MT5 ulandi: {info.name} | Balans: ${info.balance:.2f} | Server: {info.server}")
    return True


def disconnect_mt5():
    mt5.shutdown()


def get_account_info() -> dict:
    if not connect_mt5():
        return {}
    info = mt5.account_info()
    result = {
        "login":    info.login,
        "name":     info.name,
        "balance":  round(info.balance, 2),
        "equity":   round(info.equity, 2),
        "margin":   round(info.margin, 2),
        "free_margin": round(info.margin_free, 2),
        "profit":   round(info.profit, 2),
        "leverage": info.leverage,
        "currency": info.currency,
        "server":   info.server,
    }
    disconnect_mt5()
    return result


def get_current_price() -> dict:
    if not connect_mt5():
        return {}
    tick = mt5.symbol_info_tick(SYMBOL)
    if tick is None:
        disconnect_mt5()
        return {}
    result = {
        "bid": round(tick.bid, 3),
        "ask": round(tick.ask, 3),
        "spread": round((tick.ask - tick.bid) * 100, 1),
        "time": datetime.fromtimestamp(tick.time).strftime("%H:%M:%S")
    }
    disconnect_mt5()
    return result


# ══════════════════════════════════════════════════════
# LOT HISOBLASH — Minimal balans uchun optimallashtirilgan
# ══════════════════════════════════════════════════════

def calculate_lot(balance: float, risk_pct: float, sl_points: float) -> float:
    """
    Balansga qarab xavfsiz lot hisoblash
    Minimal balans uchun: 0.01 lot (micro lot)
    risk_pct: kapitalning necha % xavf ostida (odatda 1-2%)
    """
    if balance <= 0 or sl_points <= 0:
        return 0.01

    risk_amount = balance * (risk_pct / 100)

    # XAUUSD: 1 lot = $100 per point (taxminan)
    # Minimal: 0.01 lot
    lot = round(risk_amount / (sl_points * 100), 2)

    # Chegaralar
    if lot < 0.01:
        lot = 0.01
    elif lot > 0.1 and balance < 500:
        lot = 0.05   # Kichik balans uchun maksimal
    elif lot > 1.0:
        lot = 1.0

    return lot


# ══════════════════════════════════════════════════════
# ORDER YUBORISH
# ══════════════════════════════════════════════════════

def place_order(
    direction: str,    # "BUY" yoki "SELL"
    lot: float,
    sl_price: float,
    tp_price: float,
    comment: str = "TradingBot"
) -> dict:
    """
    MT5 ga order yuborish
    Returns: {"success": bool, "order_id": int, "message": str}
    """
    if not connect_mt5():
        return {"success": False, "message": "MT5 ga ulanib bo'lmadi"}

    # Symbol tekshirish
    symbol_info = mt5.symbol_info(SYMBOL)
    if symbol_info is None:
        disconnect_mt5()
        return {"success": False, "message": f"{SYMBOL} topilmadi"}

    if not symbol_info.visible:
        mt5.symbol_select(SYMBOL, True)

    tick = mt5.symbol_info_tick(SYMBOL)
    if tick is None:
        disconnect_mt5()
        return {"success": False, "message": "Narx olishda xato"}

    # Narx va yo'nalish
    if direction == "BUY":
        order_type = mt5.ORDER_TYPE_BUY
        price      = tick.ask
    else:
        order_type = mt5.ORDER_TYPE_SELL
        price      = tick.bid

    # Deviation (slippage)
    deviation = 20

    request = {
        "action":     mt5.TRADE_ACTION_DEAL,
        "symbol":     SYMBOL,
        "volume":     lot,
        "type":       order_type,
        "price":      price,
        "sl":         sl_price,
        "tp":         tp_price,
        "deviation":  deviation,
        "magic":      234567,
        "comment":    comment,
        "type_time":  mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    disconnect_mt5()

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        error_msg = f"Order xatosi [{result.retcode}]: {result.comment}"
        logger.error(error_msg)
        return {"success": False, "message": error_msg, "retcode": result.retcode}

    logger.info(f"Order muvaffaqiyatli: #{result.order} {direction} {lot} {SYMBOL} @ {price}")
    return {
        "success":    True,
        "order_id":   result.order,
        "price":      price,
        "lot":        lot,
        "direction":  direction,
        "sl":         sl_price,
        "tp":         tp_price,
        "message":    f"✅ Order #{result.order} ochildi"
    }


def close_position(ticket: int) -> dict:
    """Ochiq pozitsiyani yopish"""
    if not connect_mt5():
        return {"success": False, "message": "MT5 ga ulanib bo'lmadi"}

    positions = mt5.positions_get(ticket=ticket)
    if not positions:
        disconnect_mt5()
        return {"success": False, "message": f"Pozitsiya #{ticket} topilmadi"}

    pos = positions[0]
    tick = mt5.symbol_info_tick(pos.symbol)

    if pos.type == mt5.ORDER_TYPE_BUY:
        order_type = mt5.ORDER_TYPE_SELL
        price = tick.bid
    else:
        order_type = mt5.ORDER_TYPE_BUY
        price = tick.ask

    request = {
        "action":   mt5.TRADE_ACTION_DEAL,
        "symbol":   pos.symbol,
        "volume":   pos.volume,
        "type":     order_type,
        "position": ticket,
        "price":    price,
        "deviation": 20,
        "magic":    234567,
        "comment":  "Bot yopdi",
    }

    result = mt5.order_send(request)
    disconnect_mt5()

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        return {"success": False, "message": f"Yopishda xato [{result.retcode}]: {result.comment}"}

    return {"success": True, "message": f"✅ Pozitsiya #{ticket} yopildi", "price": price}


def get_open_positions() -> list:
    """Barcha ochiq pozitsiyalar"""
    if not connect_mt5():
        return []

    positions = mt5.positions_get(symbol=SYMBOL)
    disconnect_mt5()

    if positions is None:
        return []

    result = []
    for p in positions:
        result.append({
            "ticket":    p.ticket,
            "type":      "BUY" if p.type == 0 else "SELL",
            "lot":       p.volume,
            "open_price": round(p.price_open, 3),
            "current_price": round(p.price_current, 3),
            "sl":        round(p.sl, 3),
            "tp":        round(p.tp, 3),
            "profit":    round(p.profit, 2),
            "open_time": datetime.fromtimestamp(p.time).strftime("%H:%M:%S"),
            "comment":   p.comment,
        })
    return result


def get_trade_history(days: int = 7) -> list:
    """Oxirgi savdo tarixi"""
    if not connect_mt5():
        return []

    from datetime import timedelta
    date_from = datetime.now() - timedelta(days=days)
    date_to   = datetime.now()

    deals = mt5.history_deals_get(date_from, date_to)
    disconnect_mt5()

    if deals is None:
        return []

    result = []
    for d in deals:
        if d.symbol == SYMBOL and d.entry in [0, 1]:
            result.append({
                "ticket": d.order,
                "type":   "BUY" if d.type == 0 else "SELL",
                "lot":    d.volume,
                "price":  round(d.price, 3),
                "profit": round(d.profit, 2),
                "time":   datetime.fromtimestamp(d.time).strftime("%Y-%m-%d %H:%M"),
            })
    return result[-20:]  # Oxirgi 20 ta
