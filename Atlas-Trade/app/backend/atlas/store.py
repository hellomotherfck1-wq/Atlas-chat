from __future__ import annotations
import os, sqlite3
from pathlib import Path

DB_PATH = os.getenv("ATLAS_DB", str(Path(__file__).resolve().parents[1] / "atlas.db"))

def connect():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS signals (
          id INTEGER PRIMARY KEY, symbol TEXT NOT NULL, decision TEXT NOT NULL,
          price REAL, entry REAL, stop REAL, target REAL, rsi REAL, volume_ratio REAL,
          rr REAL, reason TEXT, agents TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
          candle_key TEXT UNIQUE
        );
        CREATE TABLE IF NOT EXISTS trades (
          id INTEGER PRIMARY KEY, signal_id INTEGER UNIQUE, symbol TEXT NOT NULL,
          entry REAL NOT NULL, stop REAL NOT NULL, target REAL NOT NULL,
          quantity REAL NOT NULL, entry_fee REAL NOT NULL, exit REAL,
          exit_fee REAL DEFAULT 0, pnl REAL, status TEXT NOT NULL DEFAULT 'OPEN',
          opened_at TEXT DEFAULT CURRENT_TIMESTAMP, closed_at TEXT
        );
        CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        """)
        db.execute("INSERT OR IGNORE INTO meta(key,value) VALUES('initial_balance','10000')")
