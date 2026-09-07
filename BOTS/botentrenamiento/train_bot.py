"""
Entrypoint principal del Bot de Entrenamiento.

Modos de ejecución:
  python train_bot.py                  → entrena una vez
  python train_bot.py --optimize       → optimiza parámetros y luego entrena
  python train_bot.py --schedule       → entrena cada sábado a las 00:00
  python train_bot.py --optimize --schedule → optimiza + entrena cada sábado
"""

import argparse
import logging
import sys
import time
from pathlib import Path

import schedule

from config import (
    SYMBOL, TIMEFRAME, N_TRIALS,
    LOGS_DIR, LOG_LEVEL, LOG_FILE,
    MODELS_DIR, DB_DIR,
)
from data.mt5_connector import connect, disconnect, get_ohlcv
from data.db_reader import get_trade_count


def setup_logging() -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    DB_DIR.mkdir(parents=True, exist_ok=True)

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


def run_training(optimize: bool = False) -> None:
    """Ejecuta el pipeline completo. Si optimize=True, busca los mejores parámetros primero."""
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.info("BOT DE ENTRENAMIENTO — INICIO%s", " (modo optimización)" if optimize else "")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    if not connect():
        logger.critical("No se pudo conectar a MT5. Abortando.")
        return

    try:
        # ── 1. Descargar datos OHLCV ──────────────────────────────────────────
        df_raw = get_ohlcv(symbol=SYMBOL, timeframe=TIMEFRAME, bars=300_000)

        # ── 2. Optimizar parámetros (opcional) ────────────────────────────────
        if optimize:
            from training.optimizer import run_optimization
            logger.info("Iniciando búsqueda de parámetros con Optuna (%d trials)...", N_TRIALS)
            run_optimization(df_raw, n_trials=N_TRIALS)
            # Recargar config Y todos los módulos que dependen de él para que
            # los pasos siguientes usen los nuevos parámetros.
            import importlib
            import config              as _cfg
            import features.indicators as _ind
            import training.labeler    as _lab
            import training.dataset    as _ds
            import training.trainer    as _tr
            for _mod in (_cfg, _ind, _lab, _ds, _tr):
                importlib.reload(_mod)
            logger.info("Parámetros optimizados aplicados. Módulos recargados.")

        # Importar aquí (después del posible reload) para usar siempre la
        # versión actualizada de cada módulo.
        from features.indicators import add_indicators
        from training.labeler    import add_labels, label_distribution
        from training.dataset    import build_dataset
        from training.trainer    import train

        # ── 3. Calcular indicadores técnicos ──────────────────────────────────
        df = add_indicators(df_raw)

        # ── 4. Generar etiquetas ───────────────────────────────────────────────
        df = add_labels(df)
        dist = label_distribution(df)
        logger.info("Distribución de etiquetas: %s", dist)

        # ── 5. Construir dataset limpio ────────────────────────────────────────
        dataset = build_dataset(df)

        # ── 6. Info de operaciones históricas en SQLite ───────────────────────
        n_trades = get_trade_count()
        logger.info("Operaciones históricas en SQLite: %d", n_trades)

        # ── 7. Entrenar y evaluar modelo ──────────────────────────────────────
        model = train(dataset)

        if model is not None:
            logger.info("Entrenamiento completado. Nuevo modelo guardado.")
        else:
            logger.info("Entrenamiento completado. Modelo anterior conservado.")

    except Exception as exc:
        logger.exception("Error inesperado durante el entrenamiento: %s", exc)
    finally:
        disconnect()

    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.info("BOT DE ENTRENAMIENTO — FIN")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


def run_scheduled(optimize: bool = False) -> None:
    """Programa el pipeline para correr cada sábado a las 00:00."""
    logger.info("Modo automático: programado cada sábado a las 00:00.")
    schedule.every().saturday.at("00:00").do(run_training, optimize=optimize)
    run_training(optimize=optimize)
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    setup_logging()

    parser = argparse.ArgumentParser(description="Bot de Entrenamiento — XGBoost MT5")
    parser.add_argument("--schedule", action="store_true",
                        help="Ejecutar automáticamente cada sábado a las 00:00.")
    parser.add_argument("--optimize", action="store_true",
                        help="Buscar mejores parámetros con Optuna antes de entrenar.")
    args = parser.parse_args()

    if args.schedule:
        run_scheduled(optimize=args.optimize)
    else:
        run_training(optimize=args.optimize)
