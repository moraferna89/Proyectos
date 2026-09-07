"""
Métricas financieras para evaluar el rendimiento del modelo.

Métricas calculadas:
  - Sharpe Ratio (anualizado, asumiendo retornos por barra)
  - Drawdown máximo
  - Win rate
  - Profit factor
  - Total de operaciones simuladas
"""

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Factor de anualización según timeframe (aprox. barras por año)
ANNUALIZATION = {
    "M1":  525600,
    "M5":  105120,
    "M15": 35040,
    "M30": 17520,
    "H1":  8760,
    "H4":  2190,
    "D1":  252,
}


def threshold_predict(model, X: np.ndarray, threshold: float,
                      min_trades: int = 0) -> np.ndarray:
    """
    Predice clase con umbral de confianza en lugar de argmax (>50%).

    Si min_trades > 0, baja el umbral automáticamente (hasta un floor de 0.15)
    para garantizar al menos min_trades señales, tomando siempre las más
    confiables primero.  `threshold` actúa como techo: nunca se sube.
    """
    proba  = model.predict_proba(X)             # (n, 3): [P(HOLD), P(BUY), P(SELL)]
    buy_p  = proba[:, 1]
    sell_p = proba[:, 2]

    if min_trades > 0:
        floor      = 0.15
        max_signal = np.maximum(buy_p, sell_p)  # mejor prob de señal por barra
        candidates = max_signal[max_signal >= floor]
        if len(candidates) >= min_trades:
            # umbral exacto para obtener min_trades señales
            auto_thr = float(np.sort(candidates)[::-1][min_trades - 1])
        else:
            auto_thr = floor                    # datos insuficientes, usar floor
        threshold = min(threshold, auto_thr)    # nunca sube el umbral original

    preds    = np.zeros(len(X), dtype=int)      # default: HOLD
    buy_sig  = buy_p  >= threshold
    sell_sig = sell_p >= threshold
    both     = buy_sig & sell_sig
    preds[buy_sig  & ~both] = 1
    preds[sell_sig & ~both] = 2
    preds[both] = np.where(buy_p[both] >= sell_p[both], 1, 2)
    return preds


def compute_metrics(df: pd.DataFrame, predictions: np.ndarray, timeframe: str = "M15") -> dict:
    """
    Calcula métricas financieras simulando operaciones basadas en las predicciones.

    df          : DataFrame del período evaluado (debe tener columna 'close')
    predictions : array de predicciones (0=HOLD, 1=BUY, 2=SELL)
    timeframe   : para el factor de anualización del Sharpe

    Retorna dict con: sharpe, max_drawdown, win_rate, profit_factor, n_trades
    """
    df = df.copy().reset_index(drop=True)
    df["pred"] = predictions

    returns = _simulate_returns(df)

    sharpe       = _sharpe_ratio(returns, timeframe)
    max_dd       = _max_drawdown(returns)
    win_rate     = _win_rate(returns)
    profit_factor = _profit_factor(returns)
    n_trades     = int((df["pred"] != 0).sum())

    metrics = {
        "sharpe":       round(sharpe, 4),
        "max_drawdown": round(max_dd, 4),
        "win_rate":     round(win_rate, 4),
        "profit_factor": round(profit_factor, 4),
        "n_trades":     n_trades,
    }

    logger.debug(
        "Métricas — Sharpe: %.3f | Drawdown: %.3f | Win rate: %.3f | PF: %.3f | Trades: %d",
        sharpe, max_dd, win_rate, profit_factor, n_trades,
    )
    return metrics


def _simulate_returns(df: pd.DataFrame) -> pd.Series:
    """
    Simula retornos barra a barra según las predicciones.
    BUY  (1): retorno = close[t+1] / close[t] - 1
    SELL (2): retorno = close[t] / close[t+1] - 1  (retorno inverso)
    HOLD (0): retorno = 0
    """
    close = df["close"].values
    preds = df["pred"].values
    n = len(close)
    returns = np.zeros(n - 1)

    for i in range(n - 1):
        if preds[i] == 1:   # BUY
            returns[i] = (close[i + 1] - close[i]) / close[i]
        elif preds[i] == 2: # SELL
            returns[i] = (close[i] - close[i + 1]) / close[i]
        # HOLD → 0

    return pd.Series(returns)


def _sharpe_ratio(returns: pd.Series, timeframe: str = "M15") -> float:
    """Sharpe Ratio anualizado. Solo considera barras con retorno != 0."""
    active = returns[returns != 0]
    if len(active) < 2:
        return 0.0
    ann_factor = ANNUALIZATION.get(timeframe, 35040) ** 0.5
    mean = active.mean()
    std  = active.std()
    if std == 0:
        return 0.0
    return float((mean / std) * ann_factor)


def _max_drawdown(returns: pd.Series) -> float:
    """Drawdown máximo como fracción del capital (0.0 = sin drawdown, 1.0 = ruina total)."""
    cumulative = (1 + returns).cumprod()
    peak = cumulative.cummax()
    drawdown = (cumulative - peak) / peak
    return float(abs(drawdown.min()))


def _win_rate(returns: pd.Series) -> float:
    """Porcentaje de operaciones con retorno positivo."""
    active = returns[returns != 0]
    if len(active) == 0:
        return 0.0
    return float((active > 0).sum() / len(active))


def _profit_factor(returns: pd.Series) -> float:
    """Suma de ganancias / suma de pérdidas (en valor absoluto). 0 si no hay pérdidas."""
    active  = returns[returns != 0]
    gains   = active[active > 0].sum()
    losses  = abs(active[active < 0].sum())
    if losses == 0:
        return float(gains) if gains > 0 else 0.0
    return float(gains / losses)


def print_report(metrics: dict) -> None:
    """Imprime un resumen formateado de las métricas."""
    print("\n" + "=" * 45)
    print("  REPORTE DE EVALUACIÓN DEL MODELO")
    print("=" * 45)
    print(f"  Sharpe Ratio    : {metrics['sharpe']:.4f}")
    print(f"  Max Drawdown    : {metrics['max_drawdown']*100:.2f}%")
    print(f"  Win Rate        : {metrics['win_rate']*100:.2f}%")
    print(f"  Profit Factor   : {metrics['profit_factor']:.4f}")
    print(f"  Nº Operaciones  : {metrics['n_trades']}")
    print("=" * 45 + "\n")
