"""
Preparación del dataset final para entrenamiento.

Responsabilidades:
  - Combinar OHLCV + indicadores + etiquetas en un único DataFrame limpio.
  - Split temporal (nunca aleatorio) en train / test OOS.
  - Exponer los splits de walk-forward validation.
"""

import logging
from typing import Generator, Tuple

import numpy as np
import pandas as pd

from config import TRAIN_RATIO, WALKFORWARD_FOLDS, LABEL_HORIZON
from features.indicators import FEATURE_COLUMNS

logger = logging.getLogger(__name__)


def build_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Recibe el DataFrame con indicadores y etiquetas ya calculadas.
    Elimina filas con NaN (warm-up + últimas N sin etiqueta).
    Retorna DataFrame limpio con features + label.
    """
    required = FEATURE_COLUMNS + ["label", "close", "time"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Columnas faltantes en el DataFrame: {missing}")

    df = df.dropna(subset=FEATURE_COLUMNS + ["label"]).copy()
    df["label"] = df["label"].astype(int)
    df = df.sort_values("time").reset_index(drop=True)

    logger.info("Dataset construido: %d filas, %d features.", len(df), len(FEATURE_COLUMNS))
    _log_class_balance(df)
    return df


def train_test_split(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split temporal en train / test.
    El test set siempre es el bloque más reciente (no hay mezcla aleatoria).
    """
    split_idx = int(len(df) * TRAIN_RATIO)
    train = df.iloc[:split_idx].copy()
    test  = df.iloc[split_idx:].copy()

    logger.info(
        "Train/Test split — Train: %d filas (%s → %s) | Test: %d filas (%s → %s)",
        len(train), train["time"].iloc[0], train["time"].iloc[-1],
        len(test),  test["time"].iloc[0],  test["time"].iloc[-1],
    )
    return train, test


def walkforward_splits(
    df: pd.DataFrame,
    n_folds: int = WALKFORWARD_FOLDS,
) -> Generator[Tuple[pd.DataFrame, pd.DataFrame], None, None]:
    """
    Genera n_folds splits walk-forward sobre el DataFrame completo.

    Esquema expanding window:
      Fold 1: train=[0..t1]         val=[t1..t2]
      Fold 2: train=[0..t2]         val=[t2..t3]
      ...
      Fold N: train=[0..t(N)]       val=[t(N)..end]

    Siempre se entrena sobre todo lo pasado hasta ese punto.
    """
    n = len(df)
    fold_size = n // (n_folds + 1)

    for i in range(1, n_folds + 1):
        train_end = fold_size * i
        val_end   = fold_size * (i + 1) if i < n_folds else n

        train = df.iloc[:train_end].copy()
        val   = df.iloc[train_end:val_end].copy()

        if len(train) == 0 or len(val) == 0:
            logger.warning("Fold %d vacío, omitiendo.", i)
            continue

        logger.debug(
            "Fold %d/%d — Train: %d filas | Val: %d filas",
            i, n_folds, len(train), len(val),
        )
        yield train, val


def get_X_y(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """Extrae features (X) y etiquetas (y) del DataFrame."""
    X = df[FEATURE_COLUMNS].copy()
    y = df["label"].copy()
    return X, y


def _log_class_balance(df: pd.DataFrame) -> None:
    counts = df["label"].value_counts().sort_index()
    total  = len(df)
    from training.labeler import LABEL_MAP
    parts = [f"{LABEL_MAP.get(int(k), k)}: {v} ({v/total*100:.1f}%)" for k, v in counts.items()]
    logger.info("Balance de clases — %s", " | ".join(parts))
