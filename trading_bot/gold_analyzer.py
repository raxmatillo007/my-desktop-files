"""
🥇 gold_analyzer.py — XAUUSD Scalping Tahlil Motori
Strategiyalar: Price Action + Multi-timeframe + News + Konfluens tizimi
Barcha signal TASDIQLANMAGAN bo'lsa chiqmaydi
"""

import aiohttp
import numpy as np
from datetime import datetime, timezone
import os

ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "demo")
NEWS_API_KEY      = os.getenv("NEWS_API_KEY", "")


# ══════════════════════════════════════════════════════
# 1. MA'LUMOT OLISH — TWELVE DATA (XAUUSD uchun)
# ══════════════════════════════════════════════════════

async def fetch_ohlcv(interval: str = "5min", outputsize: int = 200) -> dict:
    """
    Twelve Data API — XAUUSD real OHLCV
    Bepul plan: 800 so'rov/kun
    """
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": "XAU/USD",
        "interval": interval,
        "outputsize": outputsize,
        "apikey": os.getenv("TWELVE_DATA_KEY", "demo"),
        "format": "JSON"
    }
    async with aiohttp.ClientSession() as s:
        async with s.get(url, params=params) as r:
            data = await r.json()

    if "values" not in data:
        raise ValueError(f"Twelve Data xatosi: {data.get('message', 'Noma'lum')}")

    values = data["values"]
    closes  = [float(v["close"])  for v in reversed(values)]
    highs   = [float(v["high"])   for v in reversed(values)]
    lows    = [float(v["low"])    for v in reversed(values)]
    opens   = [float(v["open"])   for v in reversed(values)]
    volumes = [float(v.get("volume", 0)) for v in reversed(values)]
    times   = [v["datetime"]      for v in reversed(values)]

    return {
        "closes": closes, "highs": highs,
        "lows": lows, "opens": opens,
        "volumes": volumes, "times": times
    }


async def fetch_gold_news() -> list:
    """So'nggi Gold yangiliklari"""
    results = []
    if not NEWS_API_KEY:
        return [{"title": "News API kaliti yo'q (.env ga NEWS_API_KEY qo'shing)", "sentiment": "neutral"}]

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "gold XAU price market",
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 5,
        "apiKey": NEWS_API_KEY
    }
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, params=params) as r:
                data = await r.json()
        for article in data.get("articles", [])[:5]:
            title = article.get("title", "")
            sentiment = classify_news_sentiment(title)
            results.append({"title": title[:80], "sentiment": sentiment})
    except Exception as e:
        results.append({"title": f"Yangilik olishda xato: {e}", "sentiment": "neutral"})

    return results


def classify_news_sentiment(text: str) -> str:
    text_lower = text.lower()
    bullish_words = ["rise", "rally", "surge", "gain", "high", "bullish", "buy",
                     "demand", "safe haven", "inflation", "war", "crisis", "fed cut"]
    bearish_words = ["fall", "drop", "decline", "crash", "sell", "bearish",
                     "rate hike", "dollar strong", "risk-on", "low", "plunge"]
    b = sum(1 for w in bullish_words if w in text_lower)
    s = sum(1 for w in bearish_words if w in text_lower)
    if b > s:   return "bullish"
    elif s > b: return "bearish"
    return "neutral"


# ══════════════════════════════════════════════════════
# 2. TEXNIK INDIKATORLAR
# ══════════════════════════════════════════════════════

def ema(data: list, span: int) -> list:
    k = 2 / (span + 1)
    result = [data[0]]
    for p in data[1:]:
        result.append(p * k + result[-1] * (1 - k))
    return result


def calc_rsi(closes: list, period: int = 14) -> float:
    arr = np.array(closes)
    d = np.diff(arr)
    g = np.where(d > 0, d, 0.0)
    l = np.where(d < 0, -d, 0.0)
    ag = np.mean(g[-period:])
    al = np.mean(l[-period:])
    if al == 0: return 100.0
    return round(100 - 100 / (1 + ag / al), 2)


def calc_macd(closes: list) -> tuple:
    e12 = ema(closes, 12)
    e26 = ema(closes, 26)
    macd_line   = [e12[i] - e26[i] for i in range(len(closes))]
    signal_line = ema(macd_line, 9)
    histogram   = [macd_line[i] - signal_line[i] for i in range(len(macd_line))]
    return (round(macd_line[-1], 4),
            round(signal_line[-1], 4),
            round(histogram[-1], 4),
            round(histogram[-2], 4))   # oldingi histogram (divergence uchun)


def calc_bollinger(closes: list, period: int = 20, mult: float = 2.0) -> tuple:
    arr = np.array(closes[-period:])
    mid = np.mean(arr)
    std = np.std(arr)
    return round(mid + mult * std, 3), round(mid, 3), round(mid - mult * std, 3)


def calc_stochastic(highs, lows, closes, k=14, d=3) -> tuple:
    h14 = max(highs[-k:])
    l14 = min(lows[-k:])
    if h14 == l14: return 50.0, 50.0
    k_val = round((closes[-1] - l14) / (h14 - l14) * 100, 2)
    k_series = []
    for i in range(d):
        idx = -(d - i)
        hh = max(highs[idx - k: idx])
        ll = min(lows[idx - k: idx])
        if hh != ll:
            k_series.append((closes[idx] - ll) / (hh - ll) * 100)
    d_val = round(np.mean(k_series) if k_series else k_val, 2)
    return k_val, d_val


def calc_atr(highs, lows, closes, period=14) -> float:
    trs = []
    for i in range(1, len(closes)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i-1]),
            abs(lows[i] - closes[i-1])
        )
        trs.append(tr)
    return round(np.mean(trs[-period:]), 4)


def calc_vwap(highs, lows, closes, volumes) -> float:
    typical = [(highs[i] + lows[i] + closes[i]) / 3 for i in range(len(closes))]
    cum_tp_vol = sum(typical[i] * volumes[i] for i in range(len(closes)))
    cum_vol    = sum(volumes)
    if cum_vol == 0: return closes[-1]
    return round(cum_tp_vol / cum_vol, 3)


def find_pivot_levels(highs, lows, closes, lookback=20) -> dict:
    recent_h = highs[-lookback:]
    recent_l = lows[-lookback:]
    resistance1 = round(max(recent_h), 3)
    support1    = round(min(recent_l), 3)
    pivot       = round((resistance1 + support1 + closes[-2]) / 3, 3)
    r2 = round(pivot + (resistance1 - support1), 3)
    s2 = round(pivot - (resistance1 - support1), 3)
    return {
        "R2": r2, "R1": resistance1,
        "Pivot": pivot,
        "S1": support1, "S2": s2
    }


def detect_candlestick_pattern(opens, highs, lows, closes) -> str:
    o, h, l, c = opens[-1], highs[-1], lows[-1], closes[-1]
    po, ph, pl, pc = opens[-2], highs[-2], lows[-2], closes[-2]
    body  = abs(c - o)
    range_ = h - l
    if range_ == 0: return "Doji"

    # Hammer
    lower_wick = min(o, c) - l
    upper_wick = h - max(o, c)
    if lower_wick > body * 2 and upper_wick < body * 0.5:
        return "🔨 Hammer (Bullish)"

    # Shooting Star
    if upper_wick > body * 2 and lower_wick < body * 0.5:
        return "⭐ Shooting Star (Bearish)"

    # Engulfing
    if c > o and pc > po and c > po and o < pc:
        return "🟢 Bullish Engulfing"
    if c < o and pc < po and c < po and o > pc:
        return "🔴 Bearish Engulfing"

    # Doji
    if body < range_ * 0.1:
        return "〰️ Doji (Noaniqlik)"

    return "—"


def detect_trend(closes, short=20, long=50) -> str:
    if len(closes) < long:
        return "Ma'lumot yetarli emas"
    ma_s = np.mean(closes[-short:])
    ma_l = np.mean(closes[-long:])
    price = closes[-1]
    if price > ma_s > ma_l:
        return "📈 Kuchli Bullish"
    elif price > ma_s and ma_s < ma_l:
        return "🔼 Zaif Bullish"
    elif price < ma_s < ma_l:
        return "📉 Kuchli Bearish"
    elif price < ma_s and ma_s > ma_l:
        return "🔽 Zaif Bearish"
    return "↔️ Sideways"


# ══════════════════════════════════════════════════════
# 3. STRATEGIYALAR — HAR BIRI ALOHIDA BALL BERADI
# ══════════════════════════════════════════════════════

def strategy_rsi_extreme(rsi_5m, rsi_15m) -> dict:
    """Strategiya 1: RSI Oversold/Overbought + Multi-TF tasdiqi"""
    score = 0
    reasons = []
    if rsi_5m < 30 and rsi_15m < 40:
        score = 2
        reasons = [f"RSI(5m)={rsi_5m} — oversold", f"RSI(15m)={rsi_15m} — tasdiqlaydi"]
    elif rsi_5m > 70 and rsi_15m > 60:
        score = -2
        reasons = [f"RSI(5m)={rsi_5m} — overbought", f"RSI(15m)={rsi_15m} — tasdiqlaydi"]
    elif rsi_5m < 35:
        score = 1
        reasons = [f"RSI(5m)={rsi_5m} — past zona"]
    elif rsi_5m > 65:
        score = -1
        reasons = [f"RSI(5m)={rsi_5m} — yuqori zona"]
    return {"name": "RSI Extreme", "score": score, "reasons": reasons}


def strategy_macd_cross(macd, signal, hist, prev_hist) -> dict:
    """Strategiya 2: MACD Kesishuv + Histogram kuchayishi"""
    score = 0
    reasons = []
    if macd > signal and hist > 0 and prev_hist < 0:
        score = 2
        reasons = ["MACD bullish kesishuv (yangi)", f"Histogram: {prev_hist:.4f}→{hist:.4f}"]
    elif macd < signal and hist < 0 and prev_hist > 0:
        score = -2
        reasons = ["MACD bearish kesishuv (yangi)", f"Histogram: {prev_hist:.4f}→{hist:.4f}"]
    elif macd > signal and hist > prev_hist:
        score = 1
        reasons = [f"MACD bullish momentum kuchaymoqda"]
    elif macd < signal and hist < prev_hist:
        score = -1
        reasons = [f"MACD bearish momentum kuchaymoqda"]
    return {"name": "MACD Cross", "score": score, "reasons": reasons}


def strategy_bollinger_bounce(price, bb_upper, bb_middle, bb_lower) -> dict:
    """Strategiya 3: Bollinger Band qaytish (mean reversion)"""
    score = 0
    reasons = []
    band_width = bb_upper - bb_lower
    pos = (price - bb_lower) / band_width if band_width > 0 else 0.5

    if price <= bb_lower * 1.001:
        score = 2
        reasons = [f"Narx pastki bandda (${price:.2f} ≤ ${bb_lower:.2f})", "Mean reversion imkoniyati"]
    elif price >= bb_upper * 0.999:
        score = -2
        reasons = [f"Narx yuqori bandda (${price:.2f} ≥ ${bb_upper:.2f})", "Qaytish ehtimoli yuqori"]
    elif pos < 0.3:
        score = 1
        reasons = [f"Narx bandning pastki qismida ({pos*100:.0f}%)"]
    elif pos > 0.7:
        score = -1
        reasons = [f"Narx bandning yuqori qismida ({pos*100:.0f}%)"]
    return {"name": "Bollinger Bounce", "score": score, "reasons": reasons}


def strategy_stochastic(k, d) -> dict:
    """Strategiya 4: Stochastic Oscillator"""
    score = 0
    reasons = []
    if k < 20 and d < 20 and k > d:
        score = 2
        reasons = [f"Stoch K={k} D={d} — oversold + bullish kesishuv"]
    elif k > 80 and d > 80 and k < d:
        score = -2
        reasons = [f"Stoch K={k} D={d} — overbought + bearish kesishuv"]
    elif k < 25:
        score = 1
        reasons = [f"Stoch K={k} — oversold zona"]
    elif k > 75:
        score = -1
        reasons = [f"Stoch K={k} — overbought zona"]
    return {"name": "Stochastic", "score": score, "reasons": reasons}


def strategy_vwap(price, vwap) -> dict:
    """Strategiya 5: VWAP nisbati"""
    score = 0
    reasons = []
    diff_pct = (price - vwap) / vwap * 100

    if price > vwap and diff_pct < 0.3:
        score = 1
        reasons = [f"Narx VWAP ustida (${vwap:.2f}), yaqin — kuchli zona"]
    elif price < vwap and diff_pct > -0.3:
        score = -1
        reasons = [f"Narx VWAP ostida (${vwap:.2f}), yaqin — zaif zona"]
    elif price > vwap:
        score = 1
        reasons = [f"Narx VWAP dan yuqori — bullish bias"]
    else:
        score = -1
        reasons = [f"Narx VWAP dan past — bearish bias"]
    return {"name": "VWAP", "score": score, "reasons": reasons}


def strategy_support_resistance(price, levels: dict) -> dict:
    """Strategiya 6: Kalit daraja bounce"""
    score = 0
    reasons = []
    for name, level in levels.items():
        diff = abs(price - level) / level * 100
        if diff < 0.1:
            if "S" in name:
                score += 2
                reasons.append(f"Narx {name} ({level}) support darajasida — qaytish kuchli")
            elif "R" in name:
                score -= 2
                reasons.append(f"Narx {name} ({level}) resistance darajasida — qarshilik kuchli")
            elif name == "Pivot":
                reasons.append(f"Narx Pivot ({level}) darajasida — kuzatish kerak")
    if not reasons:
        nearest = min(levels.items(), key=lambda x: abs(price - x[1]))
        reasons.append(f"Eng yaqin daraja: {nearest[0]}={nearest[1]}")
    return {"name": "Support/Resistance", "score": score, "reasons": reasons}


def strategy_candlestick(pattern: str) -> dict:
    """Strategiya 7: Shamdon naqshlari"""
    score = 0
    reasons = []
    if "Bullish" in pattern or "Hammer" in pattern:
        score = 1
        reasons = [f"Shamdon: {pattern}"]
    elif "Bearish" in pattern or "Shooting" in pattern:
        score = -1
        reasons = [f"Shamdon: {pattern}"]
    elif "Doji" in pattern:
        reasons = [f"Shamdon: {pattern} — noaniqlik, kuting"]
    return {"name": "Candlestick Pattern", "score": score, "reasons": reasons}


def strategy_news_sentiment(news: list) -> dict:
    """Strategiya 8: Yangilik tahlili"""
    b = sum(1 for n in news if n["sentiment"] == "bullish")
    s = sum(1 for n in news if n["sentiment"] == "bearish")
    score = 0
    reasons = []
    if b > s:
        score = 1
        reasons = [f"Yangiliklar: {b} bullish, {s} bearish — ijobiy muhit"]
    elif s > b:
        score = -1
        reasons = [f"Yangiliklar: {b} bullish, {s} bearish — salbiy muhit"]
    else:
        reasons = ["Yangiliklar neytral"]
    return {"name": "News Sentiment", "score": score, "reasons": reasons}


def strategy_trend_alignment(trend: str, signal_direction: str) -> dict:
    """Strategiya 9: Trend yo'nalishi mosligini tekshirish"""
    score = 0
    reasons = []
    is_bullish_trend = "Bullish" in trend
    is_bearish_trend = "Bearish" in trend
    if signal_direction == "BUY" and is_bullish_trend:
        score = 2
        reasons = [f"Signal trend bilan mos: {trend} + BUY — kuchli tasdiqlash"]
    elif signal_direction == "SELL" and is_bearish_trend:
        score = 2
        reasons = [f"Signal trend bilan mos: {trend} + SELL — kuchli tasdiqlash"]
    elif signal_direction == "BUY" and is_bearish_trend:
        score = -1
        reasons = [f"⚠️ Counter-trend savdo: {trend} + BUY — xavfli!"]
    elif signal_direction == "SELL" and is_bullish_trend:
        score = -1
        reasons = [f"⚠️ Counter-trend savdo: {trend} + SELL — xavfli!"]
    return {"name": "Trend Alignment", "score": score, "reasons": reasons}


# ══════════════════════════════════════════════════════
# 4. ASOSIY TAHLIL FUNKSIYASI
# ══════════════════════════════════════════════════════

async def analyze_gold(timeframe: str = "5min") -> dict:
    """
    To'liq XAUUSD tahlili:
    - 5m va 15m multi-timeframe
    - 9 ta strategiya konfluens tizimi
    - Yangiliklar tasdiqi
    - Aniq kirish/chiqish + eslatma vaqtlari
    """
    # Ma'lumot olish
    data_5m  = await fetch_ohlcv("5min",  150)
    data_15m = await fetch_ohlcv("15min", 100)
    news     = await fetch_gold_news()

    c5  = data_5m["closes"]
    h5  = data_5m["highs"]
    l5  = data_5m["lows"]
    o5  = data_5m["opens"]
    v5  = data_5m["volumes"]
    c15 = data_15m["closes"]

    price = c5[-1]

    # ── Indikatorlar ──
    rsi_5m  = calc_rsi(c5,  14)
    rsi_15m = calc_rsi(c15, 14)
    macd, macd_sig, hist, prev_hist = calc_macd(c5)
    bb_u, bb_m, bb_l = calc_bollinger(c5)
    stoch_k, stoch_d = calc_stochastic(h5, l5, c5)
    atr    = calc_atr(h5, l5, c5)
    vwap   = calc_vwap(h5, l5, c5, v5)
    levels = find_pivot_levels(h5, l5, c5)
    pattern = detect_candlestick_pattern(o5, h5, l5, c5)
    trend   = detect_trend(c5)
    ma20    = round(np.mean(c5[-20:]), 3)
    ma50    = round(np.mean(c5[-50:]), 3)

    # ── 9 ta strategiya ──
    s1 = strategy_rsi_extreme(rsi_5m, rsi_15m)
    s2 = strategy_macd_cross(macd, macd_sig, hist, prev_hist)
    s3 = strategy_bollinger_bounce(price, bb_u, bb_m, bb_l)
    s4 = strategy_stochastic(stoch_k, stoch_d)
    s5 = strategy_vwap(price, vwap)
    s6 = strategy_support_resistance(price, levels)
    s7 = strategy_candlestick(pattern)
    s8 = strategy_news_sentiment(news)

    all_strategies = [s1, s2, s3, s4, s5, s6, s7, s8]

    # ── Dastlabki yo'nalish ──
    raw_score = sum(s["score"] for s in all_strategies)
    direction = "BUY" if raw_score > 0 else "SELL" if raw_score < 0 else "HOLD"

    # ── Trend alignment tasdiqi ──
    s9 = strategy_trend_alignment(trend, direction)
    all_strategies.append(s9)
    total_score = raw_score + s9["score"]
    max_score   = 18  # maksimal mumkin ball

    # ── KONFLUENS TEKSHIRUVI ──
    # Signal chiqishi uchun KAMIDA 5 strategiya tasdiqlashi kerak
    confirming = [s for s in all_strategies if (s["score"] > 0 and direction == "BUY") or
                                                (s["score"] < 0 and direction == "SELL")]
    confirmed = len(confirming) >= 5

    # ── Signal kuchi ──
    pct = abs(total_score) / max_score * 100
    if pct >= 60:
        strength = "💪 KUCHLI"
        confidence = f"{min(int(pct), 92)}%"
    elif pct >= 35:
        strength = "✅ O'RTA"
        confidence = f"{min(int(pct), 75)}%"
    else:
        strength = "⚠️ ZAIF"
        confidence = f"{min(int(pct), 50)}%"

    # Signal — TASDIQ bo'lmasa HOLD
    if not confirmed or abs(total_score) < 3:
        final_signal = "🟡 KUTING"
        confirmed    = False
    elif direction == "BUY":
        final_signal = "🟢 XARID (BUY)"
    else:
        final_signal = "🔴 SOTUV (SELL)"

    # ── TP / SL hisoblash (ATR asosida) ──
    if direction == "BUY":
        entry      = round(price, 3)
        stop_loss  = round(price - atr * 1.5, 3)
        tp1        = round(price + atr * 1.5, 3)
        tp2        = round(price + atr * 2.5, 3)
        tp3        = round(price + atr * 4.0, 3)
        invalidation = stop_loss
    else:
        entry      = round(price, 3)
        stop_loss  = round(price + atr * 1.5, 3)
        tp1        = round(price - atr * 1.5, 3)
        tp2        = round(price - atr * 2.5, 3)
        tp3        = round(price - atr * 4.0, 3)
        invalidation = stop_loss

    risk   = abs(entry - stop_loss)
    reward = abs(entry - tp1)
    rr     = round(reward / risk, 2) if risk > 0 else 0

    # ── Eslatma vaqtlari ──
    now = datetime.now()
    reminders = [
        f"⏰ TP1 kuzatuvi: {atr*1.5:.2f}$ harakat bo'lganda",
        f"⏰ SL tekshiruvi: har 5 daqiqada",
        f"⏰ Pozitsiyadan chiqish: {int(atr*60/price*100)} daqiqa ichida (siqilish bo'lmasa)"
    ]

    return {
        "symbol":        "XAU/USD (Gold)",
        "price":         price,
        "timestamp":     now.strftime("%Y-%m-%d %H:%M:%S"),
        "timeframe":     timeframe,
        "signal":        final_signal,
        "confirmed":     confirmed,
        "strength":      strength,
        "confidence":    confidence,
        "total_score":   total_score,
        "max_score":     max_score,
        "direction":     direction,

        # Indikatorlar
        "rsi_5m":        rsi_5m,
        "rsi_15m":       rsi_15m,
        "macd":          macd,
        "macd_signal":   macd_sig,
        "histogram":     hist,
        "bb_upper":      bb_u,
        "bb_middle":     bb_m,
        "bb_lower":      bb_l,
        "stoch_k":       stoch_k,
        "stoch_d":       stoch_d,
        "atr":           atr,
        "vwap":          vwap,
        "ma20":          ma20,
        "ma50":          ma50,
        "trend":         trend,
        "pattern":       pattern,
        "levels":        levels,

        # Savdo rejasi
        "entry":         entry,
        "stop_loss":     stop_loss,
        "tp1":           tp1,
        "tp2":           tp2,
        "tp3":           tp3,
        "rr_ratio":      rr,
        "invalidation":  invalidation,
        "risk_usd":      round(risk, 3),

        # Strategiyalar
        "strategies":    all_strategies,
        "confirming_count": len(confirming),
        "reminders":     reminders,

        # Yangiliklar
        "news":          news,
    }


# ══════════════════════════════════════════════════════
# 5. XABAR FORMATLASH
# ══════════════════════════════════════════════════════

def format_gold_message(d: dict) -> str:
    confirmed_badge = "✅ TASDIQLANGAN" if d["confirmed"] else "❌ TASDIQLANMAGAN — KUTING"

    lines = [
        f"🥇 *XAU/USD — GOLD TAHLILI*",
        f"🕐 {d['timestamp']} | ⏱️ {d['timeframe']}",
        f"",
        f"💵 Narx: `${d['price']:,.3f}`",
        f"📊 Trend: {d['trend']}",
        f"",
        f"━━━━━━━━━━━━━━━━━━━━━━",
        f"🎯 *SIGNAL: {d['signal']}*",
        f"🔐 Tasdiqlash: *{confirmed_badge}*",
        f"💪 Kuch: {d['strength']} | Ishonch: `{d['confidence']}`",
        f"📊 Ball: `{d['total_score']}/{d['max_score']}`",
        f"✅ Tasdiqlagan strategiyalar: `{d['confirming_count']}/9`",
        f"",
        f"━━━━━━━━━━━━━━━━━━━━━━",
        f"📐 *INDIKATORLAR:*",
        f"• RSI (5m):  `{d['rsi_5m']}` {'🔴' if d['rsi_5m']>70 else '🟢' if d['rsi_5m']<30 else '🟡'}",
        f"• RSI (15m): `{d['rsi_15m']}` {'🔴' if d['rsi_15m']>70 else '🟢' if d['rsi_15m']<30 else '🟡'}",
        f"• MACD:      `{d['macd']}` | Signal: `{d['macd_signal']}`",
        f"• Histogram: `{d['histogram']}` {'📈' if d['histogram']>0 else '📉'}",
        f"• Stoch K/D: `{d['stoch_k']}/{d['stoch_d']}` {'🟢' if d['stoch_k']<20 else '🔴' if d['stoch_k']>80 else '🟡'}",
        f"• ATR:       `{d['atr']}`",
        f"• VWAP:      `${d['vwap']:,.3f}` {'✅' if d['price']>d['vwap'] else '❌'}",
        f"• MA20:      `${d['ma20']:,.3f}` {'✅' if d['price']>d['ma20'] else '❌'}",
        f"• MA50:      `${d['ma50']:,.3f}` {'✅' if d['price']>d['ma50'] else '❌'}",
        f"",
        f"🕯️ Shamdon: `{d['pattern']}`",
        f"",
        f"━━━━━━━━━━━━━━━━━━━━━━",
        f"🏔️ *KALIT DARAJALAR:*",
        f"• R2: `${d['levels']['R2']:,.3f}`",
        f"• R1: `${d['levels']['R1']:,.3f}`",
        f"• Pivot: `${d['levels']['Pivot']:,.3f}`",
        f"• S1: `${d['levels']['S1']:,.3f}`",
        f"• S2: `${d['levels']['S2']:,.3f}`",
        f"",
        f"• Bollinger: `${d['bb_lower']:,.3f}` — `${d['bb_upper']:,.3f}`",
    ]

    # Savdo rejasi — faqat tasdiqlanganlar uchun
    if d["confirmed"]:
        lines += [
            f"",
            f"━━━━━━━━━━━━━━━━━━━━━━",
            f"💼 *SAVDO REJASI:*",
            f"",
            f"🔵 Kirish: `${d['entry']:,.3f}`",
            f"🛑 Stop-Loss: `${d['stop_loss']:,.3f}` (risk: ${d['risk_usd']})",
            f"",
            f"🎯 TP1: `${d['tp1']:,.3f}` (1:1)",
            f"🎯 TP2: `${d['tp2']:,.3f}` (1:1.7)",
            f"🎯 TP3: `${d['tp3']:,.3f}` (1:2.7)",
            f"",
            f"⚖️ Risk/Reward: `1:{d['rr_ratio']}`",
            f"💰 Pozitsiya hajmi: Kapitalning `1-2%`",
            f"🚫 Bekor bo'lish: Narx `${d['invalidation']:,.3f}` ga tegsa",
        ]
    else:
        lines += [
            f"",
            f"━━━━━━━━━━━━━━━━━━━━━━",
            f"⏳ *SAVDO REJASI YO'Q*",
            f"Signal hali yetarlicha kuchli emas.",
            f"Kamida 5 strategiya tasdiqlaganda signal beriladi.",
        ]

    # Strategiyalar ro'yxati
    lines += [
        f"",
        f"━━━━━━━━━━━━━━━━━━━━━━",
        f"🧠 *STRATEGIYALAR TAHLILI:*",
    ]
    for s in d["strategies"]:
        if s["score"] > 0:
            icon = "✅"
        elif s["score"] < 0:
            icon = "❌"
        else:
            icon = "🟡"
        reason = s["reasons"][0] if s["reasons"] else "—"
        lines.append(f"{icon} *{s['name']}* ({s['score']:+d}): _{reason}_")

    # Yangiliklar
    lines += [
        f"",
        f"━━━━━━━━━━━━━━━━━━━━━━",
        f"📰 *SO'NGGI YANGILIKLAR:*",
    ]
    for n in d["news"][:3]:
        sent_icon = "🟢" if n["sentiment"]=="bullish" else "🔴" if n["sentiment"]=="bearish" else "⚪"
        lines.append(f"{sent_icon} _{n['title']}_")

    # Eslatmalar
    if d["confirmed"]:
        lines += [
            f"",
            f"━━━━━━━━━━━━━━━━━━━━━━",
            f"🔔 *ESLATMALAR:*",
        ]
        for r in d["reminders"]:
            lines.append(r)

    lines += [
        f"",
        f"━━━━━━━━━━━━━━━━━━━━━━",
        f"⚠️ _Bu tahlil ta'lim maqsadida._",
        f"_Savdoga kirishdan oldin o'z tadqiqotingizni o'tkazing._"
    ]

    return "\n".join(lines)
