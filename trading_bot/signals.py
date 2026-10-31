"""
📊 signals.py — Binance + CoinGecko tahlil moduli
RSI, MACD, MA, Bollinger Bands hisoblash
"""

import aiohttp
import numpy as np
from datetime import datetime


# ─────────────────────────────────────────
# BINANCE API
# ─────────────────────────────────────────

async def get_klines(symbol: str, interval: str = "1h", limit: int = 100):
    """Binance dan OHLCV ma'lumot olish"""
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            if resp.status != 200:
                raise ValueError(f"Binance xatosi: {resp.status}")
            data = await resp.json()

    closes = [float(k[4]) for k in data]
    highs  = [float(k[2]) for k in data]
    lows   = [float(k[3]) for k in data]
    volumes= [float(k[5]) for k in data]
    return closes, highs, lows, volumes


async def get_ticker_24h(symbol: str):
    """24 soatlik statistika"""
    url = "https://api.binance.com/api/v3/ticker/24hr"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params={"symbol": symbol}) as resp:
            return await resp.json()


# ─────────────────────────────────────────
# TEXNIK INDIKATORLAR
# ─────────────────────────────────────────

def calc_rsi(closes: list, period: int = 14) -> float:
    closes = np.array(closes)
    deltas = np.diff(closes)
    gains  = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)

    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])

    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)


def calc_macd(closes: list):
    closes = np.array(closes)

    def ema(data, span):
        k = 2 / (span + 1)
        result = [data[0]]
        for price in data[1:]:
            result.append(price * k + result[-1] * (1 - k))
        return np.array(result)

    ema12 = ema(closes, 12)
    ema26 = ema(closes, 26)
    macd_line  = ema12 - ema26
    signal_line = ema(macd_line, 9)
    histogram  = macd_line - signal_line

    return round(macd_line[-1], 4), round(signal_line[-1], 4), round(histogram[-1], 4)


def calc_bollinger(closes: list, period: int = 20):
    closes = np.array(closes[-period:])
    middle = np.mean(closes)
    std    = np.std(closes)
    upper  = middle + 2 * std
    lower  = middle - 2 * std
    return round(upper, 4), round(middle, 4), round(lower, 4)


def calc_moving_averages(closes: list):
    ma20  = round(np.mean(closes[-20:]), 4)
    ma50  = round(np.mean(closes[-50:]), 4)
    ma200 = round(np.mean(closes[-100:]), 4)  # 100 ta bilan taxminiy
    return ma20, ma50, ma200


def find_support_resistance(highs: list, lows: list, closes: list):
    """Oddiy support/resistance hisoblash"""
    recent_high = max(highs[-20:])
    recent_low  = min(lows[-20:])
    current     = closes[-1]

    resistance = round(recent_high, 2)
    support    = round(recent_low, 2)

    # Pivot point
    pivot = round((recent_high + recent_low + closes[-2]) / 3, 2)

    return support, resistance, pivot


def calc_volume_trend(volumes: list) -> str:
    avg_vol  = np.mean(volumes[-20:])
    last_vol = volumes[-1]
    ratio    = last_vol / avg_vol if avg_vol > 0 else 1

    if ratio > 1.5:
        return f"🔥 Yuqori ({ratio:.1f}x o'rtachadan)"
    elif ratio > 1.0:
        return f"📈 O'rtachadan yuqori ({ratio:.1f}x)"
    else:
        return f"📉 Past ({ratio:.1f}x)"


# ─────────────────────────────────────────
# SIGNAL GENERATOR
# ─────────────────────────────────────────

def generate_signal(rsi, macd, macd_signal, histogram, price, ma20, ma50, bb_upper, bb_lower) -> dict:
    """
    Ko'p indikator asosida signal yaratish
    Har indikator ball beradi: +1 bullish, -1 bearish, 0 neytral
    """
    score = 0
    reasons = []

    # RSI tahlili
    if rsi < 30:
        score += 2
        reasons.append("✅ RSI oversold (xarid imkoniyati)")
    elif rsi < 45:
        score += 1
        reasons.append("✅ RSI pastda (bullish zona)")
    elif rsi > 70:
        score -= 2
        reasons.append("❌ RSI overbought (sotish ehtimoli)")
    elif rsi > 55:
        score -= 1
        reasons.append("⚠️ RSI yuqorida (ehtiyot)")

    # MACD tahlili
    if macd > macd_signal and histogram > 0:
        score += 2
        reasons.append("✅ MACD bullish kesishuv")
    elif macd < macd_signal and histogram < 0:
        score -= 2
        reasons.append("❌ MACD bearish kesishuv")
    elif histogram > 0:
        score += 1
        reasons.append("✅ MACD histogram musbat")

    # Moving Average tahlili
    if price > ma50 > ma20:
        score += 1
        reasons.append("✅ Narx MA50 dan yuqori")
    elif price < ma50 and price < ma20:
        score -= 1
        reasons.append("❌ Narx MA lardan past")

    # Bollinger Bands
    if price <= bb_lower * 1.01:
        score += 1
        reasons.append("✅ Bollinger pastki bandda (potensial qaytish)")
    elif price >= bb_upper * 0.99:
        score -= 1
        reasons.append("❌ Bollinger yuqori bandda (potensial tushish)")

    # Signal qaror
    if score >= 3:
        signal = "🟢 BUY"
        strength = "Kuchli" if score >= 5 else "O'rta"
    elif score <= -3:
        signal = "🔴 SELL"
        strength = "Kuchli" if score <= -5 else "O'rta"
    else:
        signal = "🟡 HOLD"
        strength = "Neytral"

    return {
        "signal": signal,
        "strength": strength,
        "score": score,
        "max_score": 8,
        "reasons": reasons
    }


# ─────────────────────────────────────────
# ASOSIY FUNKSIYA
# ─────────────────────────────────────────

async def get_binance_signal(symbol: str, detailed: bool = False) -> dict:
    """To'liq signal va tahlil"""
    # 1h va 4h ma'lumot olish
    closes_1h, highs_1h, lows_1h, volumes_1h = await get_klines(symbol, "1h", 100)
    closes_4h, highs_4h, lows_4h, _          = await get_klines(symbol, "4h", 50)
    ticker = await get_ticker_24h(symbol)

    price      = float(ticker["lastPrice"])
    change_24h = float(ticker["priceChangePercent"])

    # Indikatorlar (1h)
    rsi_1h              = calc_rsi(closes_1h)
    macd, macd_sig, hist= calc_macd(closes_1h)
    bb_upper, bb_mid, bb_lower = calc_bollinger(closes_1h)
    ma20, ma50, ma200   = calc_moving_averages(closes_1h)
    support, resistance, pivot = find_support_resistance(highs_1h, lows_1h, closes_1h)
    vol_trend           = calc_volume_trend(volumes_1h)

    # 4h RSI
    rsi_4h = calc_rsi(closes_4h)

    # Signal
    sig = generate_signal(rsi_1h, macd, macd_sig, hist, price, ma20, ma50, bb_upper, bb_lower)

    # TP/SL hisoblash
    atr = np.mean([highs_1h[i] - lows_1h[i] for i in range(-14, 0)])
    if "BUY" in sig["signal"]:
        stop_loss  = round(price - atr * 1.5, 2)
        take_profit1 = round(price + atr * 2, 2)
        take_profit2 = round(price + atr * 3.5, 2)
        take_profit3 = round(resistance, 2)
    else:
        stop_loss  = round(price + atr * 1.5, 2)
        take_profit1 = round(price - atr * 2, 2)
        take_profit2 = round(price - atr * 3.5, 2)
        take_profit3 = round(support, 2)

    risk = abs(price - stop_loss)
    reward = abs(price - take_profit1)
    rr_ratio = round(reward / risk, 2) if risk > 0 else 0

    return {
        "symbol": symbol,
        "price": price,
        "change_24h": change_24h,
        "signal": sig["signal"],
        "strength": sig["strength"],
        "score": sig["score"],
        "reasons": sig["reasons"],
        "rsi_1h": rsi_1h,
        "rsi_4h": rsi_4h,
        "macd": macd,
        "macd_signal": macd_sig,
        "histogram": hist,
        "ma20": ma20,
        "ma50": ma50,
        "ma200": ma200,
        "bb_upper": bb_upper,
        "bb_middle": bb_mid,
        "bb_lower": bb_lower,
        "support": support,
        "resistance": resistance,
        "pivot": pivot,
        "volume_trend": vol_trend,
        "stop_loss": stop_loss,
        "take_profit1": take_profit1,
        "take_profit2": take_profit2,
        "take_profit3": take_profit3,
        "rr_ratio": rr_ratio,
        "detailed": detailed,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
    }


# ─────────────────────────────────────────
# COINGECKO
# ─────────────────────────────────────────

async def get_coingecko_data(coin_id: str) -> dict:
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    params = {"localization": "false", "tickers": "false", "community_data": "false"}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            if resp.status != 200:
                raise ValueError(f"CoinGecko xatosi: {resp.status} — '{coin_id}' topilmadi")
            return await resp.json()


# ─────────────────────────────────────────
# XABAR FORMATLASH
# ─────────────────────────────────────────

def format_signal_message(data: dict, detailed: bool = False) -> str:
    symbol   = data["symbol"]
    price    = data["price"]
    change   = data["change_24h"]
    signal   = data["signal"]
    strength = data["strength"]
    score    = data["score"]

    change_emoji = "📈" if change > 0 else "📉"
    change_str   = f"{'+' if change > 0 else ''}{change:.2f}%"

    lines = [
        f"📊 *{symbol} — Tahlil*",
        f"🕐 {data['timestamp']}",
        f"",
        f"💵 Narx: `${price:,.4f}` {change_emoji} `{change_str}` (24s)",
        f"",
        f"━━━━━━━━━━━━━━━━━━━━",
        f"🎯 *SIGNAL: {signal}* ({strength})",
        f"📊 Kuch: `{score}/8`",
        f"",
        f"📐 *Texnik indikatorlar:*",
        f"• RSI (1h): `{data['rsi_1h']}` {'🔴 Overbought' if data['rsi_1h']>70 else '🟢 Oversold' if data['rsi_1h']<30 else '🟡 Neytral'}",
        f"• RSI (4h): `{data['rsi_4h']}`",
        f"• MACD: `{data['macd']}` | Signal: `{data['macd_signal']}`",
        f"• Histogram: `{data['histogram']}` {'📈' if data['histogram']>0 else '📉'}",
        f"",
        f"📏 *Moving Averages:*",
        f"• MA20:  `${data['ma20']:,.2f}` {'✅' if price > data['ma20'] else '❌'}",
        f"• MA50:  `${data['ma50']:,.2f}` {'✅' if price > data['ma50'] else '❌'}",
        f"• MA200: `${data['ma200']:,.2f}` {'✅' if price > data['ma200'] else '❌'}",
        f"",
        f"📉 *Bollinger Bands:*",
        f"• Yuqori: `${data['bb_upper']:,.2f}`",
        f"• O'rta:  `${data['bb_middle']:,.2f}`",
        f"• Pastki: `${data['bb_lower']:,.2f}`",
        f"",
        f"🏔️ *Kalit darajalar:*",
        f"• Resistance: `${data['resistance']:,.2f}`",
        f"• Pivot:      `${data['pivot']:,.2f}`",
        f"• Support:    `${data['support']:,.2f}`",
        f"",
        f"📦 Hajm: {data['volume_trend']}",
    ]

    if "BUY" in signal or "SELL" in signal:
        lines += [
            f"",
            f"━━━━━━━━━━━━━━━━━━━━",
            f"💼 *Savdo rejasi:*",
            f"• 🔵 Entry: `${price:,.4f}`",
            f"• 🛑 Stop-Loss: `${data['stop_loss']:,.4f}`",
            f"• 🎯 TP1: `${data['take_profit1']:,.4f}`",
            f"• 🎯 TP2: `${data['take_profit2']:,.4f}`",
            f"• 🎯 TP3: `${data['take_profit3']:,.4f}`",
            f"• ⚖️ Risk/Reward: `1:{data['rr_ratio']}`",
            f"• 💰 Pozitsiya: Kapitalning `1-2%`",
        ]

    if detailed and data.get("reasons"):
        lines += [
            f"",
            f"━━━━━━━━━━━━━━━━━━━━",
            f"🧠 *Signal sabablari:*",
        ]
        for reason in data["reasons"]:
            lines.append(f"  {reason}")

    lines += [
        f"",
        f"━━━━━━━━━━━━━━━━━━━━",
        f"⚠️ _Bu tahlil ta'lim maqsadida._",
        f"_Har doim o'z tadqiqotingizni o'tkazing._"
    ]

    return "\n".join(lines)
