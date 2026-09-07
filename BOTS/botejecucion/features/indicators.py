"""
Cálculo de indicadores técnicos sobre un DataFrame OHLCV.
Implementación idéntica al botentrenamiento — mismos parámetros, mismos cálculos.
"""

import logging

import numpy as np
import pandas as pd

from config import (
    RSI_PERIOD, MACD_FAST, MACD_SLOW, MACD_SIGNAL,
    EMA_FAST, EMA_SLOW, BB_PERIOD, BB_STD,
    ATR_PERIOD, VOL_MA_PERIOD,
)

logger = logging.getLogger(__name__)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Recibe un DataFrame OHLCV y retorna el mismo con columnas de indicadores.
    Las filas con NaN al inicio (warm-up) se eliminan al final.
    """
    df = df.copy()

    _add_rsi(df)
    _add_macd(df)
    _add_ema(df)
    _add_bollinger(df)
    _add_atr(df)
    _add_volume_ratio(df)

    initial_len = len(df)
    df = df.dropna().reset_index(drop=True)
    dropped = initial_len - len(df)

    if dropped > 0:
        logger.debug("Eliminadas %d filas con NaN (warm-up).", dropped)

    logger.debug("Indicadores calculados. Filas: %d", len(df))
    return df


def _ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def _add_rsi(df: pd.DataFrame) -> None:
    delta    = df["close"].diff()
    gain     = delta.clip(lower=0)
    loss     = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / RSI_PERIOD, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / RSI_PERIOD, adjust=False).mean()
    rs       = avg_gain / avg_loss.replace(0, np.nan)
    df["rsi"] = 100 - (100 / (1 + rs))


def _add_macd(df: pd.DataFrame) -> None:
    ema_fast    = _ema(df["close"], MACD_FAST)
    ema_slow    = _ema(df["close"], MACD_SLOW)
    macd_line   = ema_fast - ema_slow
    signal_line = _ema(macd_line, MACD_SIGNAL)
    df["macd"]        = macd_line
    df["macd_signal"] = signal_line
    df["macd_hist"]   = macd_line - signal_line


def _add_ema(df: pd.DataFrame) -> None:
    df["ema_fast"]  = _ema(df["close"], EMA_FAST)
    df["ema_slow"]  = _ema(df["close"], EMA_SLOW)
    df["ema_cross"] = df["ema_fast"] - df["ema_slow"]


def _add_bollinger(df: pd.DataFrame) -> None:
    mid   = df["close"].rolling(BB_PERIOD).mean()
    std   = df["close"].rolling(BB_PERIOD).std()
    upper = mid + BB_STD * std
    lower = mid - BB_STD * std
    width = upper - lower
    df["bb_upper"] = upper
    df["bb_mid"]   = mid
    df["bb_lower"] = lower
    df["bb_width"] = width
    df["bb_pct"]   = (df["close"] - lower) / width.replace(0, np.nan)


def _add_atr(df: pd.DataFrame) -> None:
    prev_close = df["close"].shift(1)
    tr = pd.concat([
        df["high"] - df["low"],
        (df["high"] - prev_close).abs(),
        (df["low"]  - prev_close).abs(),
    ], axis=1).max(axis=1)
    df["atr"]     = tr.ewm(alpha=1 / ATR_PERIOD, adjust=False).mean()
    df["atr_pct"] = df["atr"] / df["close"]


def _add_volume_ratio(df: pd.DataFrame) -> None:
    vol_ma = df["volume"].rolling(window=VOL_MA_PERIOD).mean()
    df["vol_ratio"] = df["volume"] / vol_ma.replace(0, np.nan)


FEATURE_COLUMNS = [
    "rsi",
    "macd", "macd_signal", "macd_hist",
    "ema_fast", "ema_slow", "ema_cross",
    "bb_upper", "bb_mid", "bb_lower", "bb_width", "bb_pct",
    "atr", "atr_pct",
    "vol_ratio",
]
