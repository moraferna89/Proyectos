"""
Conexión a MetaTrader 5 y descarga de datos OHLCV históricos.
"""

import logging
from datetime import datetime

import MetaTrader5 as mt5
import pandas as pd

from config import SYMBOL, TIMEFRAME, BARS

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


_CHUNK_SIZE = 50_000  # máximo seguro por llamada a MT5


def get_ohlcv(
    symbol: str = SYMBOL,
    timeframe: str = TIMEFRAME,
    bars: int = BARS,
) -> pd.DataFrame:
    """
    Descarga `bars` velas históricas de MT5 en chunks de 50 000 para evitar
    el límite silencioso del broker. Retorna DataFrame con columnas:
    time, open, high, low, close, volume.
    """
    tf = _TIMEFRAME_MAP.get(timeframe)
    if tf is None:
        raise ValueError(f"Timeframe '{timeframe}' no soportado. Opciones: {list(_TIMEFRAME_MAP)}")

    logger.info("Descargando %d velas de %s %s en chunks de %d...",
                bars, symbol, timeframe, _CHUNK_SIZE)

    chunks = []
    downloaded = 0
    start_pos = 0

    while downloaded < bars:
        to_fetch = min(_CHUNK_SIZE, bars - downloaded)
        rates = mt5.copy_rates_from_pos(symbol, tf, start_pos, to_fetch)

        if rates is None or len(rates) == 0:
            error = mt5.last_error()
            if downloaded == 0:
                logger.error("Error al obtener datos de MT5: %s", error)
                raise RuntimeError(f"MT5 copy_rates_from_pos falló: {error}")
            logger.warning("No hay más datos disponibles en el broker tras %d velas.", downloaded)
            break

        chunks.append(pd.DataFrame(rates))
        fetched = len(rates)
        downloaded += fetched
        start_pos += fetched
        logger.info("  chunk %d/%d — %d velas acumuladas",
                    len(chunks), -(-bars // _CHUNK_SIZE), downloaded)

        if fetched < to_fetch:
            logger.warning("Broker devolvió %d en lugar de %d — datos agotados.", fetched, to_fetch)
            break

    df = pd.concat(chunks, ignore_index=True)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    df = df.rename(columns={"tick_volume": "volume"})
    df = df[["time", "open", "high", "low", "close", "volume"]].copy()
    df = df.drop_duplicates(subset="time").sort_values("time").reset_index(drop=True)

    logger.info("Total descargado: %d velas. Rango: %s → %s",
                len(df), df["time"].iloc[0], df["time"].iloc[-1])
    return df


def get_ohlcv_range(
    symbol: str = SYMBOL,
    timeframe: str = TIMEFRAME,
    date_from: datetime = None,
    date_to: datetime = None,
) -> pd.DataFrame:
    """Descarga velas entre dos fechas específicas."""
    tf = _TIMEFRAME_MAP.get(timeframe)
    if tf is None:
        raise ValueError(f"Timeframe '{timeframe}' no soportado.")

    date_to = date_to or datetime.utcnow()
    logger.info("Descargando velas de %s %s desde %s hasta %s", symbol, timeframe, date_from, date_to)

    rates = mt5.copy_rates_range(symbol, tf, date_from, date_to)

    if rates is None or len(rates) == 0:
        raise RuntimeError(f"MT5 copy_rates_range falló: {mt5.last_error()}")

    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    df = df.rename(columns={"tick_volume": "volume"})
    df = df[["time", "open", "high", "low", "close", "volume"]].copy()
    df = df.sort_values("time").reset_index(drop=True)

    logger.info("Descargadas %d velas.", len(df))
    return df
