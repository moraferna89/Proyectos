"""
Lectura de operaciones pasadas desde la base de datos SQLite compartida.
"""

import logging
import sqlite3
from pathlib import Path

import pandas as pd

from config import DB_PATH

logger = logging.getLogger(__name__)


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Abre y retorna una conexión SQLite."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_trades_table(db_path: Path = DB_PATH) -> None:
    """Crea la tabla trades si no existe (primera ejecución)."""
    conn = get_connection(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket          INTEGER,
            symbol          TEXT,
            timeframe       TEXT,
            open_time       TEXT,
            close_time      TEXT,
            direction       TEXT,        -- BUY / SELL
            open_price      REAL,
            close_price     REAL,
            sl              REAL,
            tp              REAL,
            volume          REAL,
            profit          REAL,
            pips            REAL,
            signal          TEXT,        -- BUY / SELL / HOLD
            confidence      REAL,
            rsi             REAL,
            macd            REAL,
            macd_signal     REAL,
            ema_fast        REAL,
            ema_slow        REAL,
            bb_upper        REAL,
            bb_lower        REAL,
            atr             REAL,
            vol_ratio       REAL,
            created_at      TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()
    logger.debug("Tabla 'trades' verificada/creada en %s", db_path)


def load_trades(
    symbol: str = None,
    limit: int = None,
    db_path: Path = DB_PATH,
) -> pd.DataFrame:
    """
    Carga operaciones desde SQLite.
    Filtra por símbolo si se indica. Limita resultados si se indica.
    Retorna DataFrame vacío si no hay datos.
    """
    ensure_trades_table(db_path)
    conn = get_connection(db_path)

    query = "SELECT * FROM trades"
    params = []

    if symbol:
        query += " WHERE symbol = ?"
        params.append(symbol)

    query += " ORDER BY open_time ASC"

    if limit:
        query += f" LIMIT {int(limit)}"

    try:
        df = pd.read_sql_query(query, conn, params=params)
        logger.info("Cargadas %d operaciones desde SQLite.", len(df))
    except Exception as exc:
        logger.error("Error leyendo trades de SQLite: %s", exc)
        df = pd.DataFrame()
    finally:
        conn.close()

    return df


def save_trade(trade: dict, db_path: Path = DB_PATH) -> None:
    """
    Inserta un registro de operación en la tabla trades.
    `trade` es un dict con las claves de la tabla.
    """
    ensure_trades_table(db_path)
    conn = get_connection(db_path)

    columns = ", ".join(trade.keys())
    placeholders = ", ".join(["?"] * len(trade))
    values = list(trade.values())

    try:
        conn.execute(f"INSERT INTO trades ({columns}) VALUES ({placeholders})", values)
        conn.commit()
        logger.debug("Trade guardado: ticket=%s, profit=%.2f", trade.get("ticket"), trade.get("profit"))
    except Exception as exc:
        logger.error("Error guardando trade en SQLite: %s", exc)
    finally:
        conn.close()


def get_trade_count(db_path: Path = DB_PATH) -> int:
    """Retorna el número total de operaciones almacenadas."""
    ensure_trades_table(db_path)
    conn = get_connection(db_path)
    cursor = conn.execute("SELECT COUNT(*) FROM trades")
    count = cursor.fetchone()[0]
    conn.close()
    return count
