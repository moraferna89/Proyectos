"""
Gestión del ciclo de vida de posiciones:
  - Revisar posiciones abiertas
  - Cerrar si hay señal contraria
  - Abrir nueva posición si la señal lo indica
"""

import logging
from datetime import datetime
from typing import Optional

import MetaTrader5 as mt5
import pandas as pd

from config import SYMBOL, TIMEFRAME, LOT_SIZE, SL_ATR_MULT, TP_ATR_MULT, MAX_POSITIONS
from data.mt5_connector import (
    get_open_positions, open_position, close_position,
    get_symbol_info, get_deal_by_position,
)
from execution.risk import calculate_sl_tp
from execution.tracker import save_trade, update_trade_close

logger = logging.getLogger(__name__)


def manage_positions(
    signal: str,
    buy_p: float,
    sell_p: float,
    df: pd.DataFrame,
) -> str:
    """
    Pipeline de gestión de posiciones por cada nueva barra:
      1. Verifica posiciones abiertas.
      2. Cierra si la señal es contraria.
      3. Abre nueva posición si no hay ninguna y la señal es BUY/SELL.

    Retorna la acción tomada: "opened" | "closed" | "reversed" | "held" | "error"
    """
    last        = df.iloc[-1]
    atr         = float(last["atr"])
    action_done = None

    open_positions = get_open_positions(SYMBOL)

    # ── 1. Gestionar posición(es) existente(s) ────────────────────────────────
    for pos in open_positions:
        pos_dir = "BUY" if pos.type == mt5.POSITION_TYPE_BUY else "SELL"
        opposite = (pos_dir == "BUY" and signal == "SELL") or \
                   (pos_dir == "SELL" and signal == "BUY")

        if opposite:
            logger.info(
                "Señal contraria (%s) — cerrando posición %s (ticket %d)",
                signal, pos_dir, pos.ticket,
            )
            ok = _close_and_record(pos)
            if ok:
                action_done = "closed"

    # ── 2. Abrir nueva posición si hay señal y no hay límite alcanzado ────────
    open_positions = get_open_positions(SYMBOL)   # refrescar tras posible cierre

    if signal in ("BUY", "SELL") and len(open_positions) < MAX_POSITIONS:
        info   = get_symbol_info(SYMBOL)
        price  = info["ask"] if signal == "BUY" else info["bid"]
        sl, tp = calculate_sl_tp(price, signal, atr, SL_ATR_MULT, TP_ATR_MULT, info["digits"])
        confidence = buy_p if signal == "BUY" else sell_p

        ticket = open_position(SYMBOL, signal, LOT_SIZE, sl, tp)
        if ticket:
            _record_open(ticket, signal, price, sl, tp, confidence, last)
            action_done = "reversed" if action_done == "closed" else "opened"
        else:
            action_done = "error"

    return action_done or "held"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _close_and_record(position) -> bool:
    """Cierra la posición en MT5 y actualiza el registro en SQLite."""
    ok = close_position(position)
    if not ok:
        return False

    deal = get_deal_by_position(position.ticket)
    if deal:
        close_price = deal["close_price"]
        close_time  = deal["close_time"]
        profit      = deal["profit"]
    else:
        close_price = position.price_current
        close_time  = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        profit      = position.profit
        logger.warning(
            "No se pudo obtener deal de cierre para ticket %d. Usando datos en memoria.",
            position.ticket,
        )

    pips = _calc_pips(position.symbol, position.type, position.price_open, close_price)
    update_trade_close(position.ticket, close_price, close_time, profit, pips)
    return True


def _record_open(ticket, direction, price, sl, tp, confidence, bar: pd.Series) -> None:
    """Inserta el registro de apertura de posición en SQLite."""
    bar_time = bar["time"]
    if hasattr(bar_time, "strftime"):
        open_time = bar_time.strftime("%Y-%m-%d %H:%M:%S")
    else:
        open_time = str(bar_time)

    trade = {
        "ticket":      ticket,
        "symbol":      SYMBOL,
        "timeframe":   TIMEFRAME,
        "open_time":   open_time,
        "close_time":  None,
        "direction":   direction,
        "open_price":  price,
        "close_price": None,
        "sl":          sl,
        "tp":          tp,
        "volume":      LOT_SIZE,
        "profit":      None,
        "pips":        None,
        "signal":      direction,
        "confidence":  round(confidence, 4),
        "rsi":         round(float(bar.get("rsi",         0)), 4),
        "macd":        round(float(bar.get("macd",        0)), 6),
        "macd_signal": round(float(bar.get("macd_signal", 0)), 6),
        "ema_fast":    round(float(bar.get("ema_fast",    0)), 5),
        "ema_slow":    round(float(bar.get("ema_slow",    0)), 5),
        "bb_upper":    round(float(bar.get("bb_upper",    0)), 5),
        "bb_lower":    round(float(bar.get("bb_lower",    0)), 5),
        "atr":         round(float(bar.get("atr",         0)), 6),
        "vol_ratio":   round(float(bar.get("vol_ratio",   0)), 4),
    }
    save_trade(trade)


def _calc_pips(symbol: str, pos_type: int, open_price: float, close_price: float) -> float:
    """Calcula pips ganados/perdidos."""
    pip = 0.01 if "JPY" in symbol else 0.0001
    if pos_type == mt5.POSITION_TYPE_BUY:
        return round((close_price - open_price) / pip, 1)
    return round((open_price - close_price) / pip, 1)
