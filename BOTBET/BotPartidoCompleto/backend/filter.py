from datetime import datetime, timezone, timedelta
from backend.models import Match
from config.settings import ODDS_MIN, ODDS_MAX, DAYS_AHEAD


def _deadline() -> datetime:
    """Fin del último día permitido en UTC."""
    target = datetime.now(timezone.utc).date() + timedelta(days=DAYS_AHEAD)
    return datetime(target.year, target.month, target.day,
                    23, 59, 59, tzinfo=timezone.utc)


def filter_matches(matches: list[Match]) -> list[Match]:
    """Filtra partidos con cuotas en rango y que se jueguen en los próximos 3 días."""
    deadline = _deadline()
    filtered = []
    for match in matches:
        best_odd = _best_odd(match)
        if not best_odd:
            continue
        try:
            kick_off = datetime.fromisoformat(match.commence_time.replace("Z", "+00:00"))
        except ValueError:
            continue
        if kick_off <= deadline:
            filtered.append(match)
    return filtered


def _best_odd(match: Match) -> float | None:
    """Devuelve la cuota más baja del partido (la más 'segura')."""
    candidates = [match.odds.home, match.odds.draw, match.odds.away]
    valid = [o for o in candidates if ODDS_MIN <= o <= ODDS_MAX]
    return min(valid) if valid else None
