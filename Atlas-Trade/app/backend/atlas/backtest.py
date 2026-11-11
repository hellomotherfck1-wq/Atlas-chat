"""Historical, fee-aware Binance Spot paper backtest. Never submits exchange orders."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

import httpx

from .engine import analyze_klines

BASE = "https://data-api.binance.vision"
INTERVAL_MS = 15 * 60 * 1000
FEE = 0.001
SLIPPAGE = 0.0005
INITIAL_BALANCE = 10_000.0
RISK_FRACTION = 0.01
MAX_OPEN = 3


async def _history(client: httpx.AsyncClient, symbol: str, start_ms: int, end_ms: int):
    rows = []
    cursor = start_ms
    while cursor < end_ms:
        response = await client.get(
            f"{BASE}/api/v3/klines",
            params={"symbol": symbol, "interval": "15m", "startTime": cursor,
                    "endTime": end_ms, "limit": 1000},
            timeout=30,
        )
        response.raise_for_status()
        batch = response.json()
        if not batch:
            break
        rows.extend(batch)
        next_cursor = int(batch[-1][6]) + 1
        if next_cursor <= cursor:
            break
        cursor = next_cursor
        if len(batch) < 1000:
            break
    return rows


async def run_backtest(days: int = 90, symbol_limit: int = 10):
    """Run one shared-equity portfolio simulation on the most liquid USDT spot pairs."""
    if not 1 <= days <= 180:
        raise ValueError("days must be between 1 and 180")
    if not 1 <= symbol_limit <= 20:
        raise ValueError("symbol_limit must be between 1 and 20")

    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)
    start_ms, end_ms = int(start.timestamp() * 1000), int(end.timestamp() * 1000)

    async with httpx.AsyncClient() as client:
        info, tickers = await asyncio.gather(
            client.get(f"{BASE}/api/v3/exchangeInfo", timeout=30),
            client.get(f"{BASE}/api/v3/ticker/24hr", timeout=30),
        )
        info.raise_for_status()
        tickers.raise_for_status()
        excluded = {"USDC", "USDT", "BUSD", "FDUSD", "TUSD", "USDP", "DAI"}
        allowed = {
            item["symbol"] for item in info.json()["symbols"]
            if item["status"] == "TRADING" and item["isSpotTradingAllowed"]
            and item["quoteAsset"] == "USDT"
            and item["baseAsset"] not in excluded
            and not item["baseAsset"].endswith(("UP", "DOWN", "BULL", "BEAR"))
        }
        ranked = sorted(
            (item for item in tickers.json()
             if item["symbol"] in allowed and float(item["quoteVolume"]) >= 10_000_000),
            key=lambda item: float(item["quoteVolume"]), reverse=True,
        )[:symbol_limit]
        symbols = [item["symbol"] for item in ranked]
        if not symbols:
            raise RuntimeError("No eligible USDT Spot symbols found")

        semaphore = asyncio.Semaphore(5)

        async def get_one(symbol):
            async with semaphore:
                return symbol, await _history(client, symbol, start_ms, end_ms)

        results = await asyncio.gather(*(get_one(symbol) for symbol in symbols), return_exceptions=True)

    histories = {}
    errors = []
    for item in results:
        if isinstance(item, Exception):
            errors.append(str(item)[:160])
            continue
        symbol, candles = item
        if len(candles) >= 100:
            histories[symbol] = candles
        else:
            errors.append(f"{symbol}: insufficient history ({len(candles)} candles)")

    if not histories:
        raise RuntimeError("Historical candles could not be downloaded: " + "; ".join(errors[:3]))

    # Merge all symbols by candle open time. At each timestamp, exits are processed
    # before new entries; a signal from the prior closed candle enters at this open.
    timeline = {}
    for symbol, candles in histories.items():
        for index in range(60, len(candles)):
            timeline.setdefault(int(candles[index][0]), []).append((symbol, index))

    balance = INITIAL_BALANCE
    open_positions = {}
    trades = []
    daily_pnl = {}
    weekly_pnl = {}
    peak = INITIAL_BALANCE
    max_drawdown = 0.0

    def close_position(symbol, raw_exit, timestamp, reason):
        nonlocal balance, peak, max_drawdown
        position = open_positions.pop(symbol)
        exit_price = raw_exit * (1 - SLIPPAGE)
        exit_fee = exit_price * position["quantity"] * FEE
        pnl = ((exit_price - position["entry"]) * position["quantity"]
               - position["entry_fee"] - exit_fee)
        balance += pnl
        day_key = datetime.fromtimestamp(timestamp / 1000, timezone.utc).date().isoformat()
        week_key = (datetime.fromtimestamp(timestamp / 1000, timezone.utc).date()
                    - timedelta(days=datetime.fromtimestamp(timestamp / 1000, timezone.utc).weekday())).isoformat()
        daily_pnl[day_key] = daily_pnl.get(day_key, 0.0) + pnl
        weekly_pnl[week_key] = weekly_pnl.get(week_key, 0.0) + pnl
        peak = max(peak, balance)
        if peak > 0:
            max_drawdown = max(max_drawdown, (peak - balance) / peak * 100)
        trades.append({
            "symbol": symbol, "entry_time": position["time"], "exit_time": timestamp,
            "entry": round(position["entry"], 8), "exit": round(exit_price, 8),
            "quantity": round(position["quantity"], 8), "pnl": round(pnl, 4),
            "return_pct": round(pnl / max(position["entry"] * position["quantity"], 1e-9) * 100, 4),
            "reason": reason,
        })

    for timestamp in sorted(timeline):
        batch = timeline[timestamp]

        # Process stop/target exits for every open position using this candle.
        for symbol in list(open_positions):
            candles = histories[symbol]
            index = next((i for s, i in batch if s == symbol), None)
            if index is None:
                continue
            bar = candles[index]
            low, high = float(bar[3]), float(bar[2])
            position = open_positions[symbol]
            # Conservative assumption if stop and target are both touched in one candle.
            if low <= position["stop"]:
                close_position(symbol, position["stop"], timestamp, "STOP")
            elif high >= position["target"]:
                close_position(symbol, position["target"], timestamp, "TARGET")

        day = datetime.fromtimestamp(timestamp / 1000, timezone.utc).date()
        day_key = day.isoformat()
        week_key = (day - timedelta(days=day.weekday())).isoformat()
        loss_brake = (daily_pnl.get(day_key, 0.0) <= -INITIAL_BALANCE * 0.03
                      or weekly_pnl.get(week_key, 0.0) <= -INITIAL_BALANCE * 0.07)

        # Generate signals from candles closed before this bar; fill at this bar's open.
        if not loss_brake:
            for symbol, index in batch:
                if symbol in open_positions or len(open_positions) >= MAX_OPEN:
                    continue
                candles = histories[symbol]
                signal = analyze_klines(candles[max(0, index - 60):index], symbol)
                if signal.get("decision") != "AL":
                    continue
                stop = float(signal["stop"])
                raw_entry = float(candles[index][1])
                entry = raw_entry * (1 + SLIPPAGE)
                if stop >= entry:
                    continue
                equity = balance
                risk_cash = equity * RISK_FRACTION
                quantity = risk_cash / max(entry - stop, entry * 0.001)
                entry_fee = entry * quantity * FEE
                committed = entry * quantity + entry_fee
                used = sum(p["entry"] * p["quantity"] + p["entry_fee"] for p in open_positions.values())
                if committed > max(0.0, equity - used):
                    continue
                open_positions[symbol] = {
                    "entry": entry, "stop": stop, "target": float(signal["target"]),
                    "quantity": quantity, "entry_fee": entry_fee, "time": timestamp,
                }


    # Mark all remaining positions closed at the final available close.
    for symbol in list(open_positions):
        last = histories[symbol][-1]
        close_position(symbol, float(last[4]), int(last[6]), "TEST_END")

    pnls = [trade["pnl"] for trade in trades]
    wins = sum(pnl > 0 for pnl in pnls)
    losses = sum(pnl < 0 for pnl in pnls)
    gross_profit = sum(pnl for pnl in pnls if pnl > 0)
    gross_loss = abs(sum(pnl for pnl in pnls if pnl < 0))
    return {
        "status": "completed",
        "mode": "historical_paper_backtest",
        "exchange": "Binance Spot",
        "interval": "15m",
        "requested_days": days,
        "symbols_requested": symbol_limit,
        "symbols_tested": sorted(histories),
        "candle_count": sum(len(rows) for rows in histories.values()),
        "from": start.isoformat(),
        "to": end.isoformat(),
        "initial_balance": INITIAL_BALANCE,
        "final_balance": round(balance, 2),
        "net_pnl": round(balance - INITIAL_BALANCE, 2),
        "return_pct": round((balance / INITIAL_BALANCE - 1) * 100, 2),
        "trade_count": len(trades),
        "wins": wins,
        "losses": losses,
        "win_rate_pct": round(wins / len(trades) * 100, 2) if trades else None,
        "profit_factor": round(gross_profit / gross_loss, 3) if gross_loss else (None if not gross_profit else "infinity"),
        "max_drawdown_pct": round(max_drawdown, 2),
        "fees_and_slippage": {"fee_rate_each_side": FEE, "slippage_rate_each_side": SLIPPAGE},
        "assumptions": [
            "Signals use only fully closed candles; entries fill at the next candle open.",
            "If stop and target are both touched in one candle, stop is assumed first.",
            "Open positions are closed at the final candle close.",
            "Historical universe is today's most liquid USDT Spot pairs; delisted and past-universe survivorship is not modeled.",
        ],
        "data_warnings": errors,
        "trades": trades[-200:],
    }
