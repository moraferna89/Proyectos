"""
Conexión a MetaTrader 5, descarga de barras en tiempo real
y gestión de órdenes (abrir / cerrar posiciones).
"""

import logging
import time as _time
from datetime import datetime
from typing import Optional

import MetaTrader5 as mt5
import pandas as pd

from config import SYMBOL, TIMEFRAME, WARMUP_BARS, MAGIC_NUMBER

logger = logging.getLogger(__name__)

_TIMEFRAME_MAP = {
    "M1":  mt5.TIMEFRAME_M1,
    "M5":  mt5.TIMEFRAME_M5,
    "M15": mt5.TIMEFRAME_M15,
    "M30": mt5.TIMEFRAME_M30,
    "H1":  mt5.TIMEFRAME_H1,
    "H4":  mt5.TIMEFRAME_H4,
    "D1":  mt5.TIMEFRAME_D1,
}


def connect() -> bool:
    """Inicializa la conexión con MT5. Retorna True si fue exitosa."""
    if not mt5.initialize():
        logger.error("No se pudo inicializar MT5: %s", mt5.last_error())
        return False
    info = mt5.terminal_info()
    logger.info("MT5 conectado — build %s, cuenta: %s", info.build, mt5.account_info().login)
    return True


def disconnect() -> None:
    """Cierra la conexión con MT5."""
    mt5.shutdown()
    logger.info("MT5 desconectado.")


def get_latest_bars(
    symbol: str = SYMBOL,
    timeframe: str = TIMEFRAME,
    bars: int = WARMUP_BARS,
) -> pd.DataFrame:
    """
    Descarga las últimas `bars` velas CERRADAS de MT5.
    Empieza desde pos=1 para excluir la vela actual (aún abierta).
    Retorna DataFrame con columnas: time, open, high, low, close, volume.
    """
    tf = _TIMEFRAME_MAP.get(timeframe)
    if tf is None:
        raise ValueError(f"Timeframe '{timeframe}' no soportado.")

    # pos=1 excluye la vela actual (incompleta)
    rates = mt5.copy_rates_from_pos(symbol, tf, 1, bars)
    if rates is None or len(rates) == 0:
        raise RuntimeError(f"No se pudieron obtener datos de MT5: {mt5.last_error()}")

    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    df = df.rename(columns={"tick_volume": "volume"})
    df = df[["time", "open", "high", "low", "close", "volume"]].copy()
    df = df.sort_values("time").reset_index(drop=True)

    logger.debug("Barras descargadas: %d | Última: %s", len(df), df["time"].iloc[-1])
    return df


def get_symbol_info(symbol: str = SYMBOL) -> dict:
    """Retorna precio actual, punto, dígitos y spread del símbolo."""
    info = mt5.symbol_info(symbol)
    if info is None:
        raise RuntimeError(f"No se pudo obtener info de {symbol}: {mt5.last_error()}")
    return {
        "point":  info.point,
        "digits": info.digits,
        "spread": info.spread,
        "bid":    info.bid,
        "ask":    info.ask,
    }


def get_open_positions(symbol: str = SYMBOL) -> list:
    """Retorna las posiciones abiertas por este bot (filtradas por MAGIC_NUMBER)."""
    positions = mt5.positions_get(symbol=symbol)
    if positions is None:
        return []
    return [p for p in positions if p.magic == MAGIC_NUMBER]


def open_position(
    symbol: str,
    direction: str,
    lot: float,
    sl: float,
    tp: float,
    comment: str = "exec_bot",
) -> Optional[int]:
    """
    Abre una posición BUY o SELL a mercado.
    Retorna el ticket si fue exitosa, None si falló.
    """
    info = mt5.symbol_info(symbol)
    if info is None:
        logger.error("Symbol info no disponible para %s", symbol)
        return None

    if not info.visible:
        if not mt5.symbol_select(symbol, True):
            logger.error("No se pudo seleccionar el símbolo %s", symbol)
            return None

    order_type = mt5.ORDER_TYPE_BUY if direction == "BUY" else mt5.ORDER_TYPE_SELL
    price      = info.ask if direction == "BUY" else info.bid

    request = {
        "action":       mt5.TRADE_ACTION_DEAL,
        "symbol":       symbol,
        "volume":       lot,
        "type":         order_type,
        "price":        price,
        "sl":           round(sl, info.digits),
        "tp":           round(tp, info.digits),
        "deviation":    10,
        "magic":        MAGIC_NUMBER,
        "comment":      comment,
        "type_time":    mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        logger.error(
            "Error al abrir %s: %s (código %d)", direction, result.comment, result.retcode
        )
        return None

    logger.info(
        "Posición abierta — Dir: %s | Ticket: %d | Precio: %.5f | SL: %.5f | TP: %.5f",
        direction, result.order, price, sl, tp,
    )
    return result.order


def close_position(position) -> bool:
    """
    Cierra una posición abierta por su objeto de posición.
    Retorna True si el cierre fue exitoso.
    """
    symbol     = position.symbol
    info       = mt5.symbol_info(symbol)
    order_type = mt5.ORDER_TYPE_SELL if position.type == mt5.POSITION_TYPE_BUY \
                 else mt5.ORDER_TYPE_BUY
    price      = info.bid if order_type == mt5.ORDER_TYPE_SELL else info.ask

    request = {
        "action":       mt5.TRADE_ACTION_DEAL,
        "symbol":       symbol,
        "volume":       position.volume,
        "type":         order_type,
        "position":     position.ticket,
        "price":        price,
        "deviation":    10,
        "magic":        MAGIC_NUMBER,
        "comment":      "exec_bot_close",
        "type_time":    mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        logger.error(
            "Error al cerrar posición %d: %s (código %d)",
            position.ticket, result.comment, result.retcode,
        )
        return False

    logger.info(
        "Posición cerrada — Ticket: %d | Precio cierre: %.5f",
        position.ticket, price,
    )
    return True


def get_deal_by_position(position_id: int) -> Optional[dict]:
    """
    Recupera el último deal de cierre de una posición desde el historial de MT5.
    Espera hasta 2 segundos para que MT5 procese el cierre.
    """
    for _ in range(4):
        _time.sleep(0.5)
        deals = mt5.history_deals_get(position=position_id)
        if deals and len(deals) >= 2:   # el primero es apertura, el último es cierre
            d = deals[-1]
            return {
                "close_price": d.price,
                "close_time":  datetime.fromtimestamp(d.time).strftime("%Y-%m-%d %H:%M:%S"),
                "profit":      d.profit,
            }
    return None


def get_account_balance() -> float:
    """Retorna el balance actual de la cuenta."""
    info = mt5.account_info()
    return info.balance if info else 0.0
