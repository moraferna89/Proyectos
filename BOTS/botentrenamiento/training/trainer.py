"""
Entrenamiento del modelo XGBoost con validación walk-forward.
Solo guarda el modelo nuevo si supera al anterior en datos OOS.
"""

import logging
from pathlib import Path
from typing import Optional

import joblib
import numpy as np
import pandas as pd
from xgboost import XGBClassifier

from config import XGBOOST_PARAMS, MODEL_PATH, MIN_SHARPE, MIN_WIN_RATE, MAX_DRAWDOWN, MIN_TRADES, MIN_SAMPLES, WALKFORWARD_FOLDS, TIMEFRAME, SIGNAL_THRESHOLD
from training.dataset import walkforward_splits, get_X_y, train_test_split
from training.evaluator import compute_metrics, threshold_predict

logger = logging.getLogger(__name__)


def train(df: pd.DataFrame) -> Optional[XGBClassifier]:
    """
    Ejecuta el pipeline completo de entrenamiento:
      1. Walk-forward validation para estimar rendimiento real.
      2. Entrena modelo final sobre todos los datos de train.
      3. Evalúa en test OOS.
      4. Compara con modelo anterior (si existe).
      5. Guarda si supera al anterior.

    Retorna el modelo entrenado si fue guardado, None si no superó al anterior.
    """
    logger.info("=== Iniciando entrenamiento ===")

    train_df, test_df = train_test_split(df)

    # ── Walk-forward validation ────────────────────────────────────────────────
    logger.info("Walk-forward validation con %d folds...", WALKFORWARD_FOLDS)
    wf_metrics = _walkforward_eval(train_df)
    logger.info(
        "Walk-forward promedio — Sharpe: %.3f | Win rate: %.3f | Drawdown: %.3f",
        wf_metrics["sharpe"], wf_metrics["win_rate"], wf_metrics["max_drawdown"],
    )

    # ── Entrenamiento final sobre todo el set de train ─────────────────────────
    model = _fit_model(train_df)

    # ── Evaluación en OOS (test set) ───────────────────────────────────────────
    X_test, y_test = get_X_y(test_df)
    preds = threshold_predict(model, X_test, SIGNAL_THRESHOLD, min_trades=MIN_TRADES)
    oos_metrics = compute_metrics(test_df, preds, timeframe=TIMEFRAME)
    oos_metrics["n_samples"] = len(train_df)   # muestras usadas en entrenamiento

    logger.info(
        "OOS — Sharpe: %.3f | Win rate: %.3f | Drawdown: %.3f | Profit factor: %.3f | Muestras: %d",
        oos_metrics["sharpe"], oos_metrics["win_rate"],
        oos_metrics["max_drawdown"], oos_metrics["profit_factor"],
        oos_metrics["n_samples"],
    )

    # ── Verificar si supera umbrales mínimos ──────────────────────────────────
    if not _passes_minimum_thresholds(oos_metrics):
        logger.warning("El modelo NO supera los umbrales mínimos. No se guarda.")
        _save_last_run(oos_metrics, wf_metrics, saved=False, reason="no pasó umbrales mínimos")
        return None

    # ── Comparar con modelo anterior ──────────────────────────────────────────
    if not _beats_previous_model(model, test_df, oos_metrics):
        logger.warning("El modelo NO supera al anterior en OOS. No se guarda.")
        _save_last_run(oos_metrics, wf_metrics, saved=False, reason="no superó al modelo anterior")
        return None

    # ── Guardar modelo ────────────────────────────────────────────────────────
    _save_model(model, oos_metrics)
    _save_last_run(oos_metrics, wf_metrics, saved=True, reason="modelo guardado")
    return model


def _fit_model(df: pd.DataFrame) -> XGBClassifier:
    """Entrena XGBoost sobre el DataFrame dado."""
    X, y = get_X_y(df)
    params = {k: v for k, v in XGBOOST_PARAMS.items() if k != "use_label_encoder"}
    model = XGBClassifier(**params)
    model.fit(X, y, verbose=False)
    logger.info("Modelo entrenado con %d muestras, %d features.", len(X), X.shape[1])
    return model


def _walkforward_eval(df: pd.DataFrame) -> dict:
    """Ejecuta walk-forward y retorna métricas promedio."""
    all_metrics = []

    for fold_idx, (train_fold, val_fold) in enumerate(walkforward_splits(df), 1):
        model = _fit_model(train_fold)
        X_val, _ = get_X_y(val_fold)
        preds = threshold_predict(model, X_val, SIGNAL_THRESHOLD, min_trades=MIN_TRADES)
        metrics = compute_metrics(val_fold, preds, timeframe=TIMEFRAME)
        all_metrics.append(metrics)
        logger.debug(
            "Fold %d — Sharpe: %.3f | Win rate: %.3f",
            fold_idx, metrics["sharpe"], metrics["win_rate"],
        )

    if not all_metrics:
        return {"sharpe": 0.0, "win_rate": 0.0, "max_drawdown": 1.0, "profit_factor": 0.0}

    avg = {
        key: float(np.mean([m[key] for m in all_metrics]))
        for key in all_metrics[0]
    }
    return avg


def _passes_minimum_thresholds(metrics: dict) -> bool:
    """Verifica que el modelo supere los umbrales mínimos definidos en config."""
    ok = (
        metrics["sharpe"]            >= MIN_SHARPE   and
        metrics["win_rate"]          >= MIN_WIN_RATE  and
        metrics["max_drawdown"]      <= MAX_DRAWDOWN  and
        metrics["n_trades"]          >= MIN_TRADES    and
        metrics.get("n_samples", 0)  >= MIN_SAMPLES
    )
    if not ok:
        logger.warning(
            "Umbrales mínimos: Sharpe>=%.2f (%.3f) | WinRate>=%.2f (%.3f) | "
            "Drawdown<=%.2f (%.3f) | Trades>=%d (%d) | Muestras>=%d (%d)",
            MIN_SHARPE,   metrics["sharpe"],
            MIN_WIN_RATE, metrics["win_rate"],
            MAX_DRAWDOWN, metrics["max_drawdown"],
            MIN_TRADES,   metrics["n_trades"],
            MIN_SAMPLES,  metrics.get("n_samples", 0),
        )
    return ok


def _beats_previous_model(
    new_model: XGBClassifier,
    test_df: pd.DataFrame,
    new_metrics: dict,
) -> bool:
    """
    Carga el modelo anterior (si existe) y lo evalúa en el mismo test set.
    Retorna True si el nuevo modelo tiene mejor Sharpe Ratio.
    """
    if not MODEL_PATH.exists():
        logger.info("No existe modelo anterior. El nuevo modelo será guardado.")
        return True

    try:
        prev_model = joblib.load(MODEL_PATH)
        X_test, _ = get_X_y(test_df)
        prev_preds = threshold_predict(prev_model, X_test, SIGNAL_THRESHOLD, min_trades=MIN_TRADES)
        prev_metrics = compute_metrics(test_df, prev_preds, timeframe=TIMEFRAME)

        logger.info(
            "Modelo anterior OOS — Sharpe: %.3f | Win rate: %.3f",
            prev_metrics["sharpe"], prev_metrics["win_rate"],
        )

        if new_metrics["sharpe"] > prev_metrics["sharpe"]:
            logger.info(
                "Nuevo modelo supera al anterior en Sharpe: %.3f > %.3f",
                new_metrics["sharpe"], prev_metrics["sharpe"],
            )
            return True
        else:
            return False

    except Exception as exc:
        logger.warning("No se pudo cargar el modelo anterior (%s). Guardando el nuevo.", exc)
        return True


def _save_model(model: XGBClassifier, metrics: dict) -> None:
    """Serializa el modelo a disco y guarda métricas en JSON."""
    import json
    from datetime import datetime

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    metrics_path = MODEL_PATH.parent / "metrics.json"
    history_path = MODEL_PATH.parent / "metrics_history.json"

    record = {
        **metrics,
        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "params": _snapshot_config(),
    }

    # Guardar métricas del modelo actual
    with open(metrics_path, "w") as f:
        json.dump(record, f, indent=2)

    # Agregar al historial
    history = []
    if history_path.exists():
        with open(history_path) as f:
            history = json.load(f)
    history.append(record)
    with open(history_path, "w") as f:
        json.dump(history, f, indent=2)

    logger.info(
        "Modelo guardado en %s — Sharpe: %.3f | Win rate: %.3f | Drawdown: %.3f",
        MODEL_PATH, metrics["sharpe"], metrics["win_rate"], metrics["max_drawdown"],
    )


def _save_last_run(oos_metrics: dict, wf_metrics: dict, saved: bool, reason: str) -> None:
    """Guarda resultados del último entrenamiento y los agrega siempre al historial."""
    import json
    from datetime import datetime

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    last_run_path = MODEL_PATH.parent / "last_run.json"
    history_path  = MODEL_PATH.parent / "metrics_history.json"

    record = {
        **oos_metrics,
        "wf_sharpe":   round(wf_metrics.get("sharpe", 0), 4),
        "wf_win_rate": round(wf_metrics.get("win_rate", 0), 4),
        "model_saved": saved,
        "reason":      reason,
        "run_at":      datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "params":      _snapshot_config(),
    }

    # Siempre actualizar last_run
    with open(last_run_path, "w") as f:
        json.dump(record, f, indent=2)

    # Siempre agregar al historial (guardado o no)
    history = []
    if history_path.exists():
        with open(history_path) as f:
            history = json.load(f)
    history.append(record)
    with open(history_path, "w") as f:
        json.dump(history, f, indent=2)


def _snapshot_config() -> dict:
    """Captura los parámetros actuales de config para guardar junto al modelo."""
    import config as cfg
    return {
        "SYMBOL":           cfg.SYMBOL,
        "TIMEFRAME":        cfg.TIMEFRAME,
        "BARS":             cfg.BARS,
        "LABEL_HORIZON":    cfg.LABEL_HORIZON,
        "LABEL_THRESHOLD":  cfg.LABEL_THRESHOLD,
        "RSI_PERIOD":       cfg.RSI_PERIOD,
        "EMA_FAST":         cfg.EMA_FAST,
        "EMA_SLOW":         cfg.EMA_SLOW,
        "BB_PERIOD":        cfg.BB_PERIOD,
        "ATR_PERIOD":       cfg.ATR_PERIOD,
        "n_estimators":     cfg.XGBOOST_PARAMS.get("n_estimators"),
        "max_depth":        cfg.XGBOOST_PARAMS.get("max_depth"),
        "learning_rate":    cfg.XGBOOST_PARAMS.get("learning_rate"),
        "subsample":        cfg.XGBOOST_PARAMS.get("subsample"),
        "colsample_bytree": cfg.XGBOOST_PARAMS.get("colsample_bytree"),
        "reg_lambda":       cfg.XGBOOST_PARAMS.get("reg_lambda"),
    }
