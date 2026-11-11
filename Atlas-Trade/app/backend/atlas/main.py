from __future__ import annotations
import asyncio, json, os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import httpx
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from .engine import analyze_klines
from .store import connect, init_db

BASE = "https://data-api.binance.vision"
FEE = float(os.getenv("ATLAS_FEE_RATE", "0.001"))
SLIPPAGE = float(os.getenv("ATLAS_SLIPPAGE_RATE", "0.0005"))
MAX_OPEN = 3
RISK_FRACTION = 0.01
SCAN_LOCK = asyncio.Lock()
LAST_SCAN = None
STATUS = "starting"

async def fetch_universe(client):
    info, tickers = await asyncio.gather(
        client.get(f"{BASE}/api/v3/exchangeInfo", timeout=20),
        client.get(f"{BASE}/api/v3/ticker/24hr", timeout=20))
    info.raise_for_status(); tickers.raise_for_status()
    allowed = {s["symbol"] for s in info.json()["symbols"]
               if s["status"] == "TRADING" and s["isSpotTradingAllowed"]
               and s["quoteAsset"] == "USDT" and not s["baseAsset"].endswith(("UP","DOWN","BULL","BEAR"))
               and s["baseAsset"] not in {"USDC","USDT","BUSD","FDUSD","TUSD","USDP","DAI"}}
    ranked = [t for t in tickers.json() if t["symbol"] in allowed and float(t["quoteVolume"]) >= 10_000_000]
    return [t["symbol"] for t in sorted(ranked, key=lambda x: float(x["quoteVolume"]), reverse=True)[:50]]

def record_signal(item, candle_key):
    with connect() as db:
        db.execute("""INSERT OR IGNORE INTO signals
        (symbol,decision,price,entry,stop,target,rsi,volume_ratio,rr,reason,agents,candle_key)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
        (item["symbol"],item["decision"],item.get("price"),item.get("entry"),item.get("stop"),
         item.get("target"),item.get("rsi"),item.get("volume_ratio"),item.get("rr"),
         item["reason"],json.dumps(item.get("agents",{}),ensure_ascii=False),candle_key))
        row = db.execute("SELECT id FROM signals WHERE candle_key=?", (candle_key,)).fetchone()
        if item["decision"] == "AL" and row:
            open_count = db.execute("SELECT COUNT(*) FROM trades WHERE status='OPEN'").fetchone()[0]
            balance = float(db.execute("SELECT value FROM meta WHERE key='initial_balance'").fetchone()[0])
            equity = balance + (db.execute("SELECT COALESCE(SUM(pnl),0) FROM trades WHERE status='CLOSED'").fetchone()[0])
            risk_cash = equity * RISK_FRACTION
            qty = risk_cash / max(item["entry"] - item["stop"], item["entry"] * 0.001)
            cost = qty * item["entry"] * (1 + SLIPPAGE + FEE)
            cash_used = db.execute("SELECT COALESCE(SUM(quantity*entry),0) FROM trades WHERE status='OPEN'").fetchone()[0]
            if open_count < MAX_OPEN and cost <= max(0, equity - cash_used) and db.execute("SELECT 1 FROM trades WHERE signal_id=?", (row["id"],)).fetchone() is None:
                db.execute("""INSERT INTO trades(signal_id,symbol,entry,stop,target,quantity,entry_fee,status)
                VALUES(?,?,?,?,?,?,?,'OPEN')""",
                (row["id"],item["symbol"],item["entry"]*(1+SLIPPAGE),item["stop"],item["target"],qty,qty*item["entry"]*FEE))

def update_trades(prices):
    with connect() as db:
        rows = db.execute("SELECT * FROM trades WHERE status='OPEN'").fetchall()
        for t in rows:
            candles = prices.get(t["symbol"])
            if not candles: continue
            # Use last fully closed candle (the API response includes one live candle).
            bar = candles[-2]
            low, high = float(bar[3]), float(bar[2])
            exit_price = t["stop"] if low <= t["stop"] else (t["target"] if high >= t["target"] else None)
            if exit_price is None: continue
            exit_price *= (1-SLIPPAGE)
            fee = exit_price * t["quantity"] * FEE
            pnl = (exit_price-t["entry"])*t["quantity"] - t["entry_fee"] - fee
            db.execute("""UPDATE trades SET exit=?,exit_fee=?,pnl=?,status='CLOSED',closed_at=CURRENT_TIMESTAMP WHERE id=?""",
                       (exit_price,fee,pnl,t["id"]))

async def scan_once():
    global LAST_SCAN, STATUS
    if SCAN_LOCK.locked(): return
    async with SCAN_LOCK:
        STATUS = "scanning"
        try:
            async with httpx.AsyncClient() as client:
                symbols = await fetch_universe(client)
                sem = asyncio.Semaphore(8)
                async def get_one(symbol):
                    async with sem:
                        try:
                            r = await client.get(f"{BASE}/api/v3/klines",params={"symbol":symbol,"interval":"15m","limit":60},timeout=15)
                            r.raise_for_status()
                            return symbol, r.json()
                        except Exception: return symbol, None
                results = await asyncio.gather(*(get_one(s) for s in symbols))
            prices = {s:k for s,k in results if k}
            update_trades(prices)
            for symbol, candles in results:
                if not candles: continue
                # Candle close timestamp from the latest fully closed candle.
                candle_key = f"{symbol}:{candles[-2][6]}"
                record_signal(analyze_klines(candles,symbol), candle_key)
            LAST_SCAN = datetime.now(timezone.utc).isoformat()
            STATUS = "ok"
        except Exception as exc:
            STATUS = f"error: {str(exc)[:180]}"

async def scheduler():
    while True:
        await scan_once()
        await asyncio.sleep(900)

@asynccontextmanager
async def lifespan(app):
    global STATUS
    init_db()
    task = asyncio.create_task(scheduler())
    yield
    task.cancel()
    try: await task
    except asyncio.CancelledError: pass

app = FastAPI(title="Atlas Spot Paper API", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=os.getenv("ATLAS_CORS","*").split(","), allow_methods=["*"], allow_headers=["*"])

@app.get("/api/health")
def health():
    return {"status":STATUS,"last_scan":LAST_SCAN,"mode":"paper","exchange":"Binance Spot","interval_minutes":15,"live_orders_enabled":False}

@app.post("/api/scan")
async def manual_scan():
    await scan_once()
    return health()

@app.get("/api/signals")
def signals(limit: int = Query(100, ge=1, le=500)):
    with connect() as db:
        rows = db.execute("SELECT * FROM signals ORDER BY id DESC LIMIT ?",(limit,)).fetchall()
    return [{**dict(r),"agents":json.loads(r["agents"] or "{}")} for r in rows]

@app.get("/api/portfolio")
def portfolio():
    with connect() as db:
        balance = float(db.execute("SELECT value FROM meta WHERE key='initial_balance'").fetchone()[0])
        closed = db.execute("SELECT COALESCE(SUM(pnl),0) FROM trades WHERE status='CLOSED'").fetchone()[0]
        opened = db.execute("SELECT * FROM trades WHERE status='OPEN'").fetchall()
        return {"initial_balance":balance,"realized_pnl":closed,"equity":balance+closed,
                "return_pct":closed/balance*100,"open_trades":[dict(x) for x in opened],
                "closed_trades":db.execute("SELECT * FROM trades WHERE status='CLOSED' ORDER BY id DESC LIMIT 100").fetchall().__iter__().__next__() if False else [dict(x) for x in db.execute("SELECT * FROM trades WHERE status='CLOSED' ORDER BY id DESC LIMIT 100").fetchall()]}

@app.get("/api/performance")
def performance(period: str = "all"):
    with connect() as db:
        where = "" if period=="all" else "AND closed_at >= datetime('now', ?)"
        arg = {"7d":"-7 days","30d":"-30 days","90d":"-90 days"}.get(period)
        rows = db.execute("SELECT * FROM trades WHERE status='CLOSED' "+where, (() if arg is None else (arg,))).fetchall()
    pnls = [float(r["pnl"] or 0) for r in rows]
    wins = sum(x>0 for x in pnls); losses = sum(x<0 for x in pnls)
    gross_win=sum(x for x in pnls if x>0); gross_loss=abs(sum(x for x in pnls if x<0))
    return {"trade_count":len(rows),"net_pnl":sum(pnls),"return_pct":sum(pnls)/10000*100,
            "win_rate":wins/len(rows)*100 if rows else None,
            "profit_factor":gross_win/gross_loss if gross_loss else (None if not gross_win else "infinity"),
            "average_pnl":sum(pnls)/len(rows) if rows else None,"wins":wins,"losses":losses,
            "sample_warning":len(rows)<20,"trades":[dict(r) for r in rows]}

@app.get("/api/agents")
def agents():
    names=["Tarayıcı","Haberci","Giriş-Çıkış","Şüpheci","Risk","Günlükçü"]
    with connect() as db:
        rows=db.execute("SELECT agents,COUNT(*) n FROM signals GROUP BY agents").fetchall()
    counts={n:0 for n in names}
    for row in rows:
        data=json.loads(row["agents"] or "{}")
        for name in names:
            if name in data: counts[name]+=row["n"]
    return [{"name":n,"evaluations":counts[n],"pnl":None,"note":"Rol değerlendirmesi; bağımsız işlem PnL'si atfedilmez"} for n in names]
