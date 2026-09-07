from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 8000))

ODDS_MIN = float(os.getenv("ODDS_MIN", 1.35))
ODDS_MAX = float(os.getenv("ODDS_MAX", 1.95))

COMBO_SIZE = int(os.getenv("COMBO_SIZE", 2))

ODDS_API_KEY = os.getenv("ODDS_API_KEY", "")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID", "")

DAYS_AHEAD = int(os.getenv("DAYS_AHEAD", 7))
