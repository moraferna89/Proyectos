"""
Carga el modelo entrenado y genera señales para la última barra cerrada.
"""

import logging
from typing import Tuple

import joblib
import pandas as pd

from config import MODEL_PATH, SIGNAL_THRESHOLD
from features.indicators import FEATURE_COLUMNS

logger = logging.getLogger(__name__)


def load_model():
    """
    Carga el modelo XGBoost desde disco.
    Lanza FileNotFoundError si el modelo no existe (no se ha entrenado aún).
    """
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Modelo no encontrado en {MODEL_PATH}. "
            "Ejecuta el botentrenamiento primero."
        )
    model = joblib.load(MODEL_PATH)
    logger.info("Modelo cargado desde %s", MODEL_PATH)
    return model


def predict_last_bar(model, df: pd.DataFrame) -> Tuple[str, float, float]:
    """
    Genera señal para la última barra del DataFrame.

    Retorna (señal, prob_buy, prob_sell)
      señal: "BUY", "SELL" o "HOLD"
      prob_buy, prob_sell: probabilidades del modelo [0..1]

    Lógica idéntica a threshold_predict() del botentrenamiento.
    """
    if len(df) == 0:
        return "HOLD", 0.0, 0.0

    missing = [c for c in FEATURE_COLUMNS if c not in df.columns]
    if missing:
        logger.error("Columnas de features faltantes: %s", missing)
        return "HOLD", 0.0, 0.0

    last_bar = df[FEATURE_COLUMNS].iloc[[-1]]
    proba    = model.predict_proba(last_bar)[0]   # [P(HOLD), P(BUY), P(SELL)]

    hold_p = float(proba[0])
    buy_p  = float(proba[1])
    sell_p = float(proba[2])

    signal = "HOLD"
    if buy_p >= SIGNAL_THRESHOLD and buy_p > sell_p:
        signal = "BUY"
    elif sell_p >= SIGNAL_THRESHOLD and sell_p > buy_p:
        signal = "SELL"

    logger.debug(
        "Predicción — Señal: %s | P(BUY): %.4f | P(SELL): %.4f | P(HOLD): %.4f",
        signal, buy_p, sell_p, hold_p,
    )
    return signal, buy_p, sell_p


def get_model_mtime() -> float:
    """Retorna el timestamp de modificación del archivo de modelo (0 si no existe)."""
    return MODEL_PATH.stat().st_mtime if MODEL_PATH.exists() else 0.0
