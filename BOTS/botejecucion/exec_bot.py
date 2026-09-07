"""
Entrypoint del Bot de Ejecución.

Modos:
  python exec_bot.py          → loop en tiempo real (espera cada nueva vela M5)
  python exec_bot.py --once   → una sola iteración y sale (para pruebas)
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime

from config import (
    SYMBOL, TIMEFRAME, WARMUP_BARS,
    LOGS_DIR, LOG_LEVEL, LOG_FILE,
    STATE_DIR, STATE_FILE, MODEL_PATH,
)
from data.mt5_connector import (
    connect, disconnect, get_latest_bars, get_account_balance,
)
from features.indicators import add_indicators
from execution.signal import load_model, predict_last_bar, get_model_mtime
from execution.order_manager import manage_positions
from execution.tracker import ensure_trades_table, get_stats


# ── Logging ───────────────────────────────────────────────────────────────────

def setup_logging() -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ]
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )


logger = logging.getLogger(__name__)

# ── Tiempo de espera entre barras ─────────────────────────────────────────────

_TIMEFRAME_SECONDS = {
    "M1": 60, "M5": 300, "M15": 900, "M30": 1800,
    "H1": 3600, "H4": 14400, "D1": 86400,
}


def _wait_for_new_bar(timeframe: str) -> None:
    """Espera hasta el inicio de la próxima vela (+ 2 s de margen)."""
    bar_sec   = _TIMEFRAME_SECONDS.get(timeframe, 300)
    now_ts    = datetime.utcnow().timestamp()
    secs_into = now_ts % bar_sec
    wait_sec  = bar_sec - secs_into + 2
    logger.info("Próxima vela en %.0f s...", wait_sec)
    time.sleep(wait_sec)


# ── Estado (el dashboard lo lee) ──────────────────────────────────────────────

def _write_state(state: dict) -> None:
    """Vuelca el estado actual a state/state.json para que el dashboard lo lea."""
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except Exception as exc:
        logger.warning("No se pudo escribir state.json: %s", exc)


# ── Iteración principal ───────────────────────────────────────────────────────

def run_once(model, state: dict) -> dict:
    """
    Ejecuta un ciclo completo:
      1. Descarga barras → 2. Indicadores → 3. Señal → 4. Gestión de posiciones

    Actualiza y retorna el estado para que exec_bot_live() lo persista.
    """
    # 1. Datos
    df_raw = get_latest_bars(symbol=SYMBOL, timeframe=TIMEFRAME, bars=WARMUP_BARS)

    # 2. Indicadores
    df = add_indicators(df_raw)
    if len(df) < 2:
        logger.warning("Datos insuficientes para calcular indicadores.")
        state["last_signal"] = "HOLD"
        return state

    last = df.iloc[-1]

    # 3. Señal
    signal, buy_p, sell_p = predict_last_bar(model, df)

    logger.info(
        "Bar: %s | Close: %.5f | RSI: %.1f | Señal: %s (B:%.3f S:%.3f)",
        last["time"], last["close"], last.get("rsi", 0),
        signal, buy_p, sell_p,
    )

    # 4. Gestión de posiciones
    action = manage_positions(signal, buy_p, sell_p, df)
    logger.info("Acción: %s", action)

    # 5. Estadísticas
    stats   = get_stats()
    balance = get_account_balance()

    # 6. Actualizar estado
    bar_time = last["time"]
    state.update({
        "last_update":   datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "last_bar_time": str(bar_time),
        "last_close":    round(float(last["close"]), 5),
        "last_signal":   signal,
        "buy_prob":      round(buy_p, 4),
        "sell_prob":     round(sell_p, 4),
        "last_action":   action,
        "last_rsi":      round(float(last.get("rsi", 0)), 2),
        "last_atr":      round(float(last.get("atr", 0)), 6),
        "balance":       round(balance, 2),
        **stats,
    })

    if stats.get("total_trades", 0) > 0:
        logger.info(
            "Stats — Total: %d | WR: %.1f%% | Profit: %.2f",
            stats["total_trades"], stats["win_rate"] * 100, stats["total_profit"],
        )

    return state


# ── Modos de ejecución ────────────────────────────────────────────────────────

def run_live() -> None:
    """Loop principal: ejecuta en cada nueva barra cerrada."""
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.info("BOT DE EJECUCIÓN — INICIO")
    logger.info("Símbolo: %s | Timeframe: %s", SYMBOL, TIMEFRAME)
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    if not connect():
        logger.critical("No se pudo conectar a MT5. Abortando.")
        return

    try:
        ensure_trades_table()
        model       = load_model()
        model_mtime = get_model_mtime()

        state = {
            "running":   True,
            "symbol":    SYMBOL,
            "timeframe": TIMEFRAME,
        }

        # Primera iteración inmediata
        state = run_once(model, state)
        _write_state(state)

        while True:
            _wait_for_new_bar(TIMEFRAME)

            # Recargar modelo si el botentrenamiento guardó uno nuevo
            new_mtime = get_model_mtime()
            if new_mtime > model_mtime:
                logger.info("Nuevo modelo detectado — recargando...")
                model       = load_model()
                model_mtime = new_mtime

            try:
                state = run_once(model, state)
                _write_state(state)
            except Exception as exc:
                logger.exception("Error en iteración: %s", exc)
                time.sleep(30)

    except KeyboardInterrupt:
        logger.info("Bot detenido por el usuario (Ctrl+C).")
    except Exception as exc:
        logger.exception("Error fatal: %s", exc)
    finally:
        _write_state({"running": False})
        disconnect()

    logger.info("BOT DE EJECUCIÓN — FIN")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


def run_once_cli() -> None:
    """Una sola iteración (modo --once para testing)."""
    if not connect():
        logger.critical("No se pudo conectar a MT5.")
        sys.exit(1)
    try:
        ensure_trades_table()
        model = load_model()
        state = {"running": False, "symbol": SYMBOL, "timeframe": TIMEFRAME}
        state = run_once(model, state)
        _write_state(state)
    finally:
        disconnect()


if __name__ == "__main__":
    setup_logging()

    parser = argparse.ArgumentParser(description="Bot de Ejecución — XGBoost MT5")
    parser.add_argument(
        "--once", action="store_true",
        help="Ejecutar una sola iteración y salir (modo test).",
    )
    args = parser.parse_args()

    if args.once:
        run_once_cli()
    else:
        run_live()
