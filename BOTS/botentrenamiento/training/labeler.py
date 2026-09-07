"""
Generación de etiquetas BUY / SELL / HOLD para el entrenamiento supervisado.

Lógica:
  - Miramos el retorno del precio N períodos hacia adelante (LABEL_HORIZON).
  - Si el retorno > +LABEL_THRESHOLD  → BUY  (1)
  - Si el retorno < -LABEL_THRESHOLD  → SELL (2)
  - En caso contrario                 → HOLD (0)

Las etiquetas se calculan sin filtrar ninguna fila: la columna 'label' tendrá
NaN en las últimas LABEL_HORIZON filas (no hay futuro disponible), que se
eliminan en dataset.py.
"""

import logging

import pandas as pd

from config import LABEL_HORIZON, LABEL_THRESHOLD

logger = logging.getLogger(__name__)

LABEL_MAP = {0: "HOLD", 1: "BUY", 2: "SELL"}
LABEL_REVERSE = {"HOLD": 0, "BUY": 1, "SELL": 2}


def add_labels(df: pd.DataFrame) -> pd.DataFrame:
    """
    Añade la columna 'label' (0=HOLD, 1=BUY, 2=SELL) al DataFrame.
    El DataFrame debe tener columna 'close'.
    Retorna copia del DataFrame con la columna añadida.
    Las últimas LABEL_HORIZON filas tendrán NaN y deben eliminarse después.
    """
    df = df.copy()

    future_close = df["close"].shift(-LABEL_HORIZON)
    pct_return = (future_close - df["close"]) / df["close"]

    conditions = [
        pct_return > LABEL_THRESHOLD,
        pct_return < -LABEL_THRESHOLD,
    ]
    choices = [1, 2]  # BUY, SELL

    import numpy as np
    df["label"] = pd.Series(
        __import__("numpy").select(conditions, choices, default=0),
        index=df.index,
    ).astype(float)

    # Las últimas N filas no tienen futuro → NaN
    df.loc[df.index[-LABEL_HORIZON:], "label"] = float("nan")

    counts = df["label"].value_counts().to_dict()
    logger.info(
        "Etiquetas generadas — HOLD: %d | BUY: %d | SELL: %d | NaN: %d",
        counts.get(0.0, 0),
        counts.get(1.0, 0),
        counts.get(2.0, 0),
        df["label"].isna().sum(),
    )
    return df


def label_distribution(df: pd.DataFrame) -> dict:
    """Retorna distribución porcentual de etiquetas (sin NaN)."""
    valid = df["label"].dropna()
    total = len(valid)
    if total == 0:
        return {}
    return {
        LABEL_MAP[int(k)]: round(v / total * 100, 2)
        for k, v in valid.value_counts().items()
    }
