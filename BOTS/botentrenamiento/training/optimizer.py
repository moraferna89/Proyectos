"""
Optimización de hiperparámetros con Optuna.
Prueba N combinaciones de parámetros y guarda la mejor en best_params.json.
También actualiza config.py con los valores óptimos encontrados.
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path

import numpy as np
import optuna
import pandas as pd
from xgboost import XGBClassifier

from config import MODEL_PATH, WALKFORWARD_FOLDS, MIN_SHARPE, MIN_SAMPLES, MIN_TRADES, SIGNAL_THRESHOLD
from features.indicators import FEATURE_COLUMNS
from training.evaluator import compute_metrics, threshold_predict

logger = logging.getLogger(__name__)

PROGRESS_PATH    = MODEL_PATH.parent / "optuna_progress.json"
BEST_PARAMS_PATH = MODEL_PATH.parent / "best_params.json"
STUDY_DB_PATH    = MODEL_PATH.parent / "optuna_study.db"
TRIALS_PATH      = MODEL_PATH.parent / "optuna_trials.json"
HISTORY_PATH     = MODEL_PATH.parent / "metrics_history.json"
CONFIG_PATH      = Path(__file__).resolve().parent.parent / "config.py"

optuna.logging.set_verbosity(optuna.logging.WARNING)


def run_optimization(df_raw: pd.DataFrame, n_trials: int = 50) -> dict:
    """
    Corre N trials nuevos de Optuna sobre los datos OHLCV crudos.
    El estudio persiste en SQLite — nunca repite combinaciones ya probadas.
    Retorna el mejor dict de parámetros encontrado hasta ahora.
    """
    STUDY_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    storage = f"sqlite:///{STUDY_DB_PATH}"

    study = optuna.create_study(
        study_name="trading_bot",
        direction="maximize",
        storage=storage,
        load_if_exists=True,          # retoma el estudio anterior si existe
        sampler=optuna.samplers.TPESampler(seed=42),
    )

    trials_done  = len(study.trials)
    total_after  = trials_done + n_trials
    best_so_far  = study.best_value if study.best_trials else 0.0
    best_p_so_far = study.best_params if study.best_trials else {}

    logger.info(
        "=== Optimización iniciada — %d trials nuevos (ya probados: %d, total: %d) ===",
        n_trials, trials_done, total_after,
    )
    _save_progress(trials_done, total_after, best_so_far, best_p_so_far, "running")

    def _callback(study, trial):
        best = study.best_value if study.best_trials else 0.0
        current = len(study.trials)
        _save_progress(current, total_after, best, study.best_params, "running")
        _save_trial(trial)
        logger.info(
            "Trial %d/%d — Sharpe: %.4f | Mejor: %.4f",
            current, total_after,
            trial.value if trial.value is not None else 0.0,
            best,
        )

    study.optimize(
        lambda trial: _objective(trial, df_raw),
        n_trials=n_trials,
        callbacks=[_callback],
        show_progress_bar=False,
    )

    best_params = study.best_params
    best_sharpe = study.best_value

    logger.info("Optimización completada — Mejor Sharpe: %.4f (sobre %d trials totales)",
                best_sharpe, len(study.trials))
    logger.info("Mejores parámetros: %s", best_params)

    _save_best_params(best_params, best_sharpe)
    _save_progress(len(study.trials), total_after, best_sharpe, best_params, "completed")
    apply_best_params_to_config(best_params)

    return best_params


def _objective(trial: optuna.Trial, df_raw: pd.DataFrame) -> float:
    """Función objetivo scalping: horizontes cortos y umbrales pequeños (1-3 pips)."""
    ema_fast = trial.suggest_int("EMA_FAST", 3, 15)
    ema_slow = trial.suggest_int("EMA_SLOW", ema_fast + 5, 40)

    params = {
        "LABEL_HORIZON":    trial.suggest_int("LABEL_HORIZON", 1, 5),
        "LABEL_THRESHOLD":  trial.suggest_float("LABEL_THRESHOLD", 0.00008, 0.0003),
        "RSI_PERIOD":       trial.suggest_int("RSI_PERIOD", 5, 14),
        "EMA_FAST":         ema_fast,
        "EMA_SLOW":         ema_slow,
        "BB_PERIOD":        trial.suggest_int("BB_PERIOD", 5, 20),
        "n_estimators":     trial.suggest_int("n_estimators", 100, 400),
        "max_depth":        trial.suggest_int("max_depth", 2, 5),
        "learning_rate":    trial.suggest_float("learning_rate", 0.02, 0.15, log=True),
        "subsample":        trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
        "reg_lambda":       trial.suggest_float("reg_lambda", 0.5, 10.0, log=True),
    }

    try:
        df = _build_dataset(df_raw.copy(), params)
        if df is None or len(df) < 500:
            trial.set_user_attr("n_samples", 0)
            return 0.0
        trial.set_user_attr("n_samples", len(df))
        wf = _walkforward_metrics(df, params)
        if not wf:
            return 0.0
        for k, v in wf.items():
            trial.set_user_attr(k, round(float(v), 6))
        sharpe = wf.get("sharpe", 0.0)
        return float(sharpe) if np.isfinite(sharpe) else 0.0
    except Exception as exc:
        logger.debug("Trial %d fallido: %s", trial.number, exc)
        trial.set_user_attr("n_samples", 0)
        return 0.0


def _build_dataset(df: pd.DataFrame, params: dict) -> pd.DataFrame:
    """Calcula indicadores + etiquetas con los parámetros del trial."""
    df = _compute_indicators(df, params)
    df = _compute_labels(df, params)
    df = df.dropna().reset_index(drop=True)
    df["label"] = df["label"].astype(int)
    return df if len(df) >= 300 else None


def _compute_indicators(df: pd.DataFrame, params: dict) -> pd.DataFrame:
    rsi_p   = params["RSI_PERIOD"]
    ema_f   = params["EMA_FAST"]
    ema_s   = params["EMA_SLOW"]
    bb_p    = params["BB_PERIOD"]

    # RSI
    delta    = df["close"].diff()
    avg_gain = delta.clip(lower=0).ewm(alpha=1/rsi_p, adjust=False).mean()
    avg_loss = (-delta.clip(upper=0)).ewm(alpha=1/rsi_p, adjust=False).mean()
    df["rsi"] = 100 - (100 / (1 + avg_gain / avg_loss.replace(0, np.nan)))

    # MACD (períodos fijos estándar)
    e12 = df["close"].ewm(span=12, adjust=False).mean()
    e26 = df["close"].ewm(span=26, adjust=False).mean()
    macd = e12 - e26
    df["macd"]        = macd
    df["macd_signal"] = macd.ewm(span=9, adjust=False).mean()
    df["macd_hist"]   = df["macd"] - df["macd_signal"]

    # EMA
    df["ema_fast"]  = df["close"].ewm(span=ema_f, adjust=False).mean()
    df["ema_slow"]  = df["close"].ewm(span=ema_s, adjust=False).mean()
    df["ema_cross"] = df["ema_fast"] - df["ema_slow"]

    # Bollinger Bands
    mid   = df["close"].rolling(bb_p).mean()
    std   = df["close"].rolling(bb_p).std()
    upper = mid + 2.0 * std
    lower = mid - 2.0 * std
    width = upper - lower
    df["bb_upper"] = upper
    df["bb_mid"]   = mid
    df["bb_lower"] = lower
    df["bb_width"] = width
    df["bb_pct"]   = (df["close"] - lower) / width.replace(0, np.nan)

    # ATR
    prev  = df["close"].shift(1)
    tr    = pd.concat([df["high"] - df["low"],
                       (df["high"] - prev).abs(),
                       (df["low"]  - prev).abs()], axis=1).max(axis=1)
    df["atr"]     = tr.ewm(alpha=1/14, adjust=False).mean()
    df["atr_pct"] = df["atr"] / df["close"]

    # Volumen relativo
    vol_ma = df["volume"].rolling(20).mean()
    df["vol_ratio"] = df["volume"] / vol_ma.replace(0, np.nan)

    return df


def _compute_labels(df: pd.DataFrame, params: dict) -> pd.DataFrame:
    horizon   = params["LABEL_HORIZON"]
    threshold = params["LABEL_THRESHOLD"]
    future    = df["close"].shift(-horizon)
    ret       = (future - df["close"]) / df["close"]
    df["label"] = np.select(
        [ret > threshold, ret < -threshold], [1, 2], default=0
    ).astype(float)
    df.loc[df.index[-horizon:], "label"] = float("nan")
    return df


def _walkforward_metrics(df: pd.DataFrame, params: dict) -> dict:
    """Walk-forward con máximo 3 folds; retorna promedio de todas las métricas."""
    n          = len(df)
    folds      = min(WALKFORWARD_FOLDS, 3)
    fold_size  = n // (folds + 1)
    all_m      = []

    xgb_p = {
        "objective":        "multi:softprob",
        "num_class":        3,
        "n_estimators":     params["n_estimators"],
        "max_depth":        params["max_depth"],
        "learning_rate":    params["learning_rate"],
        "subsample":        params["subsample"],
        "colsample_bytree": params["colsample_bytree"],
        "reg_lambda":       params["reg_lambda"],
        "random_state":     42,
        "n_jobs":           -1,
        "eval_metric":      "mlogloss",
    }

    for i in range(1, folds + 1):
        train_end = fold_size * i
        val_end   = fold_size * (i + 1) if i < folds else n
        train     = df.iloc[:train_end]
        val       = df.iloc[train_end:val_end]

        if len(train) < 50 or len(val) < 20:
            continue

        model = XGBClassifier(**xgb_p)
        model.fit(train[FEATURE_COLUMNS], train["label"], verbose=False)
        preds   = threshold_predict(model, val[FEATURE_COLUMNS].values, SIGNAL_THRESHOLD, min_trades=6000)
        metrics = compute_metrics(val, preds, timeframe="M5")
        if metrics["n_trades"] < 6000:  # scalping: mínimo proporcional a 18k en OOS completo
            return {}
        all_m.append(metrics)

    if not all_m:
        return {}
    return {k: float(np.mean([m[k] for m in all_m])) for k in all_m[0]}


def apply_best_params_to_config(params: dict) -> None:
    """Escribe los mejores parámetros encontrados en config.py."""
    if not CONFIG_PATH.exists():
        logger.warning("config.py no encontrado en %s", CONFIG_PATH)
        return

    with open(CONFIG_PATH, encoding="utf-8") as f:
        content = f.read()

    # Parámetros de nivel superior
    top_level = {
        "RSI_PERIOD":      params.get("RSI_PERIOD"),
        "EMA_FAST":        params.get("EMA_FAST"),
        "EMA_SLOW":        params.get("EMA_SLOW"),
        "BB_PERIOD":       params.get("BB_PERIOD"),
        "LABEL_HORIZON":   params.get("LABEL_HORIZON"),
        "LABEL_THRESHOLD": params.get("LABEL_THRESHOLD"),
    }
    for var, val in top_level.items():
        if val is not None:
            content = re.sub(
                rf"^({re.escape(var)}\s*=\s*)[\d.]+",
                rf"\g<1>{val}",
                content,
                flags=re.MULTILINE,
            )

    # Parámetros dentro de XGBOOST_PARAMS
    xgb_updates = {
        "n_estimators":     params.get("n_estimators"),
        "max_depth":        params.get("max_depth"),
        "learning_rate":    params.get("learning_rate"),
        "subsample":        params.get("subsample"),
        "colsample_bytree": params.get("colsample_bytree"),
        "reg_lambda":       params.get("reg_lambda"),
    }
    for key, val in xgb_updates.items():
        if val is not None:
            rounded = round(val, 6) if isinstance(val, float) else val
            content = re.sub(
                rf'("{re.escape(key)}"\s*:\s*)[\d.]+',
                rf"\g<1>{rounded}",
                content,
            )

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info("config.py actualizado con los mejores parámetros de Optuna.")


def _save_progress(current: int, total: int, best_sharpe: float,
                   best_params: dict, status: str) -> None:
    PROGRESS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_PATH, "w") as f:
        json.dump({
            "current_trial": current,
            "total_trials":  total,
            "best_sharpe":   round(best_sharpe, 4),
            "best_params":   best_params,
            "status":        status,
            "updated_at":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }, f, indent=2)


def _save_best_params(params: dict, sharpe: float) -> None:
    BEST_PARAMS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(BEST_PARAMS_PATH, "w") as f:
        json.dump({
            **params,
            "sharpe":   round(sharpe, 4),
            "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }, f, indent=2)
    logger.info("Mejores parámetros guardados en %s", BEST_PARAMS_PATH)


def _save_trial(trial) -> None:
    """Guarda el resultado del trial en optuna_trials.json y, si pasa umbrales, en el historial."""
    sharpe    = trial.value if trial.value is not None else 0.0
    n_samples = trial.user_attrs.get("n_samples", 0)
    n_trades  = trial.user_attrs.get("n_trades", 0)
    passes    = sharpe >= MIN_SHARPE and n_samples >= MIN_SAMPLES and n_trades >= MIN_TRADES

    record = {
        "trial":      trial.number,
        "sharpe":     round(float(sharpe), 4),
        "n_samples":  int(n_samples),
        "passes":     passes,
        "params":     {k: (round(v, 6) if isinstance(v, float) else v)
                       for k, v in trial.params.items()},
        "timestamp":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    TRIALS_PATH.parent.mkdir(parents=True, exist_ok=True)
    trials = []
    if TRIALS_PATH.exists():
        try:
            with open(TRIALS_PATH) as f:
                trials = json.load(f)
        except Exception:
            trials = []
    # Evitar duplicados por número de trial
    trials = [t for t in trials if t.get("trial") != trial.number]
    trials.append(record)
    with open(TRIALS_PATH, "w") as f:
        json.dump(trials, f, indent=2)

    if passes:
        _save_trial_to_history(trial)


def _save_trial_to_history(trial) -> None:
    """Guarda un trial que pasó umbrales en metrics_history.json para el dashboard."""
    sharpe = round(float(trial.value or 0.0), 4)
    p      = trial.params

    record = {
        "trial_number":  trial.number,
        "sharpe":        sharpe,
        "win_rate":      round(trial.user_attrs.get("win_rate", 0.0), 4),
        "max_drawdown":  round(trial.user_attrs.get("max_drawdown", 0.0), 4),
        "profit_factor": round(trial.user_attrs.get("profit_factor", 0.0), 4),
        "n_trades":      int(trial.user_attrs.get("n_trades", 0)),
        "n_samples":     int(trial.user_attrs.get("n_samples", 0)),
        "wf_sharpe":     sharpe,
        "wf_win_rate":   round(trial.user_attrs.get("win_rate", 0.0), 4),
        "model_saved":   False,
        "source":        "trial",
        "reason":        f"trial #{trial.number} pasó umbrales — solo optimización",
        "run_at":        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "params": {
            "SYMBOL":          "EURUSD",
            "TIMEFRAME":       "M5",
            "LABEL_HORIZON":   p.get("LABEL_HORIZON"),
            "LABEL_THRESHOLD": round(p.get("LABEL_THRESHOLD", 0), 8),
            "RSI_PERIOD":      p.get("RSI_PERIOD"),
            "EMA_FAST":        p.get("EMA_FAST"),
            "EMA_SLOW":        p.get("EMA_SLOW"),
            "max_depth":       p.get("max_depth"),
            "learning_rate":   round(p.get("learning_rate", 0), 6),
        },
    }

    history = []
    if HISTORY_PATH.exists():
        try:
            with open(HISTORY_PATH) as f:
                history = json.load(f)
        except Exception:
            history = []
    # Evitar duplicados por número de trial
    history = [h for h in history if not (
        h.get("source") == "trial" and h.get("trial_number") == trial.number
    )]
    history.append(record)
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=2)
    logger.info("Trial #%d guardado en historial (Sharpe: %.4f).", trial.number, sharpe)
