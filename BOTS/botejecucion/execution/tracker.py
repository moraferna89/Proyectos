"""
Registra operaciones en la base de datos SQLite compartida con botentrenamiento.
El esquema de la tabla es idéntico al de botentrenamiento/data/db_reader.py.
"""

import logging
import sqlite3

from config import DB_PATH

logger = logging.getLogger(__name__)


def ensure_trades_table() -> None:
    """Crea la tabla trades si no existe (primera ejecución)."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket          INTEGER,
            symbol          TEXT,
            timeframe       TEXT,
            open_time       TEXT,
            close_time      TEXT,
            direction       TEXT,
            open_price      REAL,
            close_price     REAL,
            sl              REAL,
            tp              REAL,
            volume          REAL,
            profit          REAL,
            pips            REAL,
            signal          TEXT,
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
    logger.debug("Tabla 'trades' verificada en %s", DB_PATH)


def save_trade(trade: dict) -> None:
    """Inserta un registro de operación (apertura) en SQLite."""
    ensure_trades_table()
    conn = sqlite3.connect(DB_PATH)
    columns      = ", ".join(trade.keys())
    placeholders = ", ".join(["?"] * len(trade))
    values       = list(trade.values())
    try:
        conn.execute(
            f"INSERT INTO trades ({columns}) VALUES ({placeholders})", values
        )
        conn.commit()
        logger.debug(
            "Trade guardado: ticket=%s | dir=%s",
            trade.get("ticket"), trade.get("direction"),
        )
    except Exception as exc:
        logger.error("Error guardando trade: %s", exc)
    finally:
        conn.close()


def update_trade_close(ticket: int, close_price: float, close_time: str,
                       profit: float, pips: float) -> None:
    """Actualiza los campos de cierre de un trade ya abierto."""
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("""
            UPDATE trades SET
                close_time  = ?,
                close_price = ?,
                profit      = ?,
                pips        = ?
            WHERE ticket = ?
        """, (close_time, close_price, profit, pips, ticket))
        conn.commit()
        logger.info(
            "Trade actualizado: ticket=%d | profit=%.2f | pips=%.1f",
            ticket, profit, pips,
        )
    except Exception as exc:
        logger.error("Error actualizando trade %d: %s", ticket, exc)
    finally:
        conn.close()


def get_stats() -> dict:
    """Estadísticas básicas de los trades cerrados en la BD."""
    ensure_trades_table()
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.execute("""
            SELECT
                COUNT(*)                                      AS total,
                SUM(CASE WHEN profit > 0 THEN 1 ELSE 0 END)  AS wins,
                SUM(profit)                                   AS total_profit,
                AVG(profit)                                   AS avg_profit,
                MAX(profit)                                   AS best_trade,
                MIN(profit)                                   AS worst_trade
            FROM trades
            WHERE close_time IS NOT NULL
        """)
        row = cur.fetchone()
        total = row[0] or 0
        wins  = row[1] or 0
        return {
            "total_trades": total,
            "wins":         wins,
            "losses":       total - wins,
            "win_rate":     round(wins / total, 4) if total > 0 else 0.0,
            "total_profit": round(row[2] or 0, 2),
            "avg_profit":   round(row[3] or 0, 2),
            "best_trade":   round(row[4] or 0, 2),
            "worst_trade":  round(row[5] or 0, 2),
        }
    except Exception as exc:
        logger.error("Error obteniendo stats: %s", exc)
        return {}
    finally:
        conn.close()


def get_recent_trades(limit: int = 20) -> list:
    """Retorna los últimos N trades cerrados (más reciente primero)."""
    ensure_trades_table()
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.execute("""
            SELECT ticket, direction, open_time, close_time,
                   open_price, close_price, profit, pips, confidence
            FROM trades
            WHERE close_time IS NOT NULL
            ORDER BY close_time DESC
            LIMIT ?
        """, (limit,))
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]
    except Exception as exc:
        logger.error("Error leyendo trades recientes: %s", exc)
        return []
    finally:
        conn.close()
