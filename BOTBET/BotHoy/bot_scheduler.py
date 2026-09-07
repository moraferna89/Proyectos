"""
Proceso independiente del scheduler de Telegram.
Corre en segundo plano (sin ventana) y manda señales cada 6 horas.
Inicia automáticamente con Windows si se agrega al inicio.
"""
import asyncio
import os
import sys
import logging
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

LOG_FILE = ROOT / "logs" / "scheduler.log"
PID_FILE = ROOT / "logs" / "scheduler.pid"
LOG_FILE.parent.mkdir(exist_ok=True)

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

INTERVAL_HOURS = 6


async def loop():
    from backend.telegram_notifier import send_signal
    logging.info("=== BOTBET Scheduler iniciado ===")
    while True:
        logging.info("Corriendo análisis...")
        await send_signal()
        logging.info(f"Señal enviada. Próximo análisis en {INTERVAL_HOURS}h.")
        await asyncio.sleep(INTERVAL_HOURS * 3600)


if __name__ == "__main__":
    # Guardar PID para que la app pueda controlarlo
    PID_FILE.write_text(str(os.getpid()))
    try:
        asyncio.run(loop())
    finally:
        PID_FILE.unlink(missing_ok=True)
