"""Deterministic Binance Spot scanner. No exchange order endpoints are used."""
from __future__ import annotations
from math import isfinite

def ema(values: list[float], period: int) -> float:
    if len(values) < period:
        raise ValueError("not enough values")
    alpha = 2 / (period + 1)
    result = sum(values[:period]) / period
    for value in values[period:]:
        result = value * alpha + result * (1 - alpha)
    return result

def rsi(values: list[float], period: int = 14) -> float:
    if len(values) <= period:
        raise ValueError("not enough values")
    changes = [values[i] - values[i-1] for i in range(1, len(values))]
    gains = sum(max(x, 0) for x in changes[-period:]) / period
    losses = sum(max(-x, 0) for x in changes[-period:]) / period
    if losses == 0:
        return 100.0
    return 100 - 100 / (1 + gains / losses)

def analyze_klines(klines: list[list], symbol: str) -> dict:
    """Return a transparent rule-based signal using CLOSED candles only."""
    if len(klines) < 30:
        return {"symbol": symbol, "decision": "BEKLE", "reason": "Yeterli kapanmış mum yok"}
    closed = klines[:-1]  # Binance's last kline may still be forming.
    closes = [float(k[4]) for k in closed]
    highs = [float(k[2]) for k in closed]
    lows = [float(k[3]) for k in closed]
    volumes = [float(k[5]) for k in closed]
    price = closes[-1]
    avg_volume = sum(volumes[-21:-1]) / 20
    volume_ratio = volumes[-1] / avg_volume if avg_volume else 0
    trend = ema(closes, 20)
    strength = rsi(closes, 14)
    recent_low = min(lows[-14:])
    stop = recent_low * 0.998
    risk = price - stop
    target = price + 2 * risk if risk > 0 else price
    rr = (target - price) / risk if risk > 0 else 0
    valid = all(isfinite(x) for x in [price, trend, strength, volume_ratio, stop, target])
    buy = valid and price > trend and 50 <= strength <= 68 and volume_ratio >= 1.2 and rr >= 2
    return {
        "symbol": symbol, "decision": "AL" if buy else "BEKLE",
        "price": price, "entry": price, "stop": stop, "target": target,
        "rsi": round(strength, 2), "volume_ratio": round(volume_ratio, 2),
        "rr": round(rr, 2), "reason": "EMA20 üstü, RSI 50-68, hacim teyidi" if buy else "AL koşulları birlikte oluşmadı",
        "agents": {
            "Tarayıcı": "Trend ve hacim koşulları tarandı",
            "Haberci": "Harici haber kaynağı bağlı değil; katalizör doğrulanmadı",
            "Giriş-Çıkış": "Kapanmış mumlara göre giriş/stop/hedef hesaplandı",
            "Şüpheci": "Kural tabanlı koşullar değerlendirildi",
            "Risk": "Pozisyon ve portföy limitleri backend tarafından denetlenir",
            "Günlükçü": "Karar ve sonuç veritabanına kaydedilir"
        }
    }
