"""
Cálculo de Stop Loss y Take Profit basados en ATR.
"""

import logging

logger = logging.getLogger(__name__)


def calculate_sl_tp(
    price: float,
    direction: str,
    atr: float,
    sl_mult: float,
    tp_mult: float,
    digits: int,
) -> tuple:
    """
    Calcula SL y TP a partir del precio de entrada y el ATR.

    direction : "BUY" o "SELL"
    sl_mult   : multiplicador de ATR para el Stop Loss
    tp_mult   : multiplicador de ATR para el Take Profit
    digits    : dígitos del símbolo para redondeo

    Retorna (sl, tp) redondeados.
    """
    sl_dist = atr * sl_mult
    tp_dist = atr * tp_mult

    if direction == "BUY":
        sl = price - sl_dist
        tp = price + tp_dist
    else:  # SELL
        sl = price + sl_dist
        tp = price - tp_dist

    sl = round(sl, digits)
    tp = round(tp, digits)

    logger.debug(
        "SL/TP — Dir: %s | ATR: %.5f | SL: %.5f | TP: %.5f",
        direction, atr, sl, tp,
    )
    return sl, tp
