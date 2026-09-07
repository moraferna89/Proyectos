"""
Parámetros globales del Bot de Entrenamiento.
Todos los módulos importan desde aquí.
"""

from pathlib import Path

# ── Rutas ─────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
DB_DIR     = BASE_DIR / "db"
LOGS_DIR   = BASE_DIR / "logs"

MODEL_PATH = MODELS_DIR / "model_latest.pkl"
DB_PATH    = DB_DIR / "trades.db"

# ── MT5: Instrumento y temporalidad ───────────────────────────────────────────
SYMBOL     = "EURUSD"
TIMEFRAME  = "M5"           # M1 M5 M15 M30 H1 H4 D1
BARS       = 200000         # Cantidad de velas históricas a descargar

# ── Indicadores técnicos (scalping: periodos cortos, más reactivos) ───────────
RSI_PERIOD = 12
MACD_FAST        = 5
MACD_SLOW        = 13
MACD_SIGNAL      = 3
EMA_FAST = 10
EMA_SLOW = 40
BB_PERIOD        = 19
BB_STD           = 2.0
ATR_PERIOD       = 7
VOL_MA_PERIOD    = 20

# ── Etiquetado — scalping: horizonte corto y umbral pequeño (1-2 pips) ───────
LABEL_HORIZON    = 1          # 1 barra M5 = 5 minutos de holding
LABEL_THRESHOLD = 0.0002601424913031369   # ~1.2 pips en EUR/USD

# ── Entrenamiento ─────────────────────────────────────────────────────────────
TRAIN_RATIO       = 0.5        # 50% train (~2 años) / 50% OOS (~2 años) con 300k barras
WALKFORWARD_FOLDS = 8

XGBOOST_PARAMS = {
    "objective": "multi:softprob",
    "num_class": 3,
    "n_estimators": 220,      # mantengo el valor que tenías
    "max_depth": 4,           # depth=3
    "learning_rate": 0.121146,  # lr=0.0686
    "subsample": 0.843129,
    "colsample_bytree": 0.690484,
    "reg_lambda": 0.943228,
    "random_state": 42,
    "n_jobs": -1,
}

# ── Métricas mínimas para reemplazar modelo ───────────────────────────────────
MIN_SHARPE       = 0.0        # sin mínimo — guardar siempre para poder operar
MIN_WIN_RATE     = 0.0
MAX_DRAWDOWN     = 1.0
MIN_TRADES       = 0
SIGNAL_THRESHOLD = 0.35       # prob mínima para señalar BUY/SELL (vs argmax >0.50)
MIN_SAMPLES      = 0

# ── Optimización (Optuna) ─────────────────────────────────────────────────────
N_TRIALS         = 50      # número de combinaciones a probar

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_LEVEL        = "INFO"
LOG_FILE         = LOGS_DIR / "train_bot.log"
