from datetime import datetime, timezone, timedelta
from backend.models import Bet
from config.settings import ODDS_MIN, ODDS_MAX, DAYS_AHEAD


def _deadline() -> datetime:
    target = datetime.now(timezone.utc).date() + timedelta(days=DAYS_AHEAD)
    return datetime(target.year, target.month, target.day, 23, 59, 59, tzinfo=timezone.utc)


def filter_bets(bets: list[Bet]) -> list[Bet]:
    """Filtra apuestas con cuota en rango [ODDS_MIN, ODDS_MAX] y dentro de DAYS_AHEAD."""
    deadline = _deadline()
    filtered = []
    for bet in bets:
        if not (ODDS_MIN <= bet.odds <= ODDS_MAX):
            continue
        try:
            kick_off = datetime.fromisoformat(bet.commence_time.replace("Z", "+00:00"))
        except ValueError:
            continue
        if kick_off <= deadline:
            filtered.append(bet)
    return filtered
