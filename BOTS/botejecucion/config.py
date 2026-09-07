"""
Parámetros globales del Bot de Ejecución.
Los indicadores deben ser idénticos al botentrenamiento.
"""

from pathlib import Path

# ── Rutas propias ──────────────────────────────────────────────────────────────
BASE_DIR  = Path(__file__).resolve().parent
LOGS_DIR  = BASE_DIR / "logs"
STATE_DIR = BASE_DIR / "state"

# ── Rutas compartidas con botentrenamiento ─────────────────────────────────────
TRAIN_BASE = BASE_DIR.parent / "botentrenamiento"
MODEL_PATH = TRAIN_BASE / "models" / "model_latest.pkl"
DB_PATH    = TRAIN_BASE / "db" / "trades.db"   # Base de datos compartida

# ── MT5: Instrumento y temporalidad ───────────────────────────────────────────
SYMBOL      = "EURUSD"
TIMEFRAME   = "M5"
WARMUP_BARS = 300   # velas para warm-up de indicadores (mismo warm-up que entrenamiento)

# ── Indicadores técnicos (IDÉNTICOS al botentrenamiento) ──────────────────────
RSI_PERIOD    = 10
MACD_FAST     = 5
MACD_SLOW     = 13
MACD_SIGNAL   = 3
EMA_FAST      = 8
EMA_SLOW      = 34
BB_PERIOD     = 5
BB_STD        = 2.0
ATR_PERIOD    = 7
VOL_MA_PERIOD = 20

# ── Señal ─────────────────────────────────────────────────────────────────────
SIGNAL_THRESHOLD = 0.35   # mismo que entrenamiento

# ── Gestión de riesgo ─────────────────────────────────────────────────────────
LOT_SIZE      = 0.01    # Lote fijo por operación
SL_ATR_MULT   = 1.5     # Stop Loss  = ATR × multiplicador
TP_ATR_MULT   = 3.0     # Take Profit = ATR × multiplicador
MAX_POSITIONS = 1       # Máximo de posiciones abiertas simultáneas
MAGIC_NUMBER  = 123456  # Número mágico para identificar órdenes del bot

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_LEVEL = "INFO"
LOG_FILE  = LOGS_DIR / "exec_bot.log"

# ── Estado (dashboard lo lee) ─────────────────────────────────────────────────
STATE_FILE = STATE_DIR / "state.json"
