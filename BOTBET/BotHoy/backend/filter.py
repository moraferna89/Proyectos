from datetime import datetime, timezone, timedelta
from backend.models import Match
from config.settings import ODDS_MIN, ODDS_MAX


def _today_window() -> tuple[datetime, datetime]:
    """Ventana de hoy en UTC: desde ahora hasta las 23:59:59 de hoy."""
    now = datetime.now(timezone.utc)
    today = now.date()
    end_of_today = datetime(today.year, today.month, today.day,
                            23, 59, 59, tzinfo=timezone.utc)
    return now, end_of_today


def filter_matches(matches: list[Match]) -> list[Match]:
    """Filtra partidos con cuotas en rango que aún no han comenzado hoy."""
    now, deadline = _today_window()
    filtered = []
    for match in matches:
        best_odd = _best_odd(match)
        if not best_odd:
            continue
        try:
            kick_off = datetime.fromisoformat(match.commence_time.replace("Z", "+00:00"))
        except ValueError:
            continue
        if now < kick_off <= deadline:
            filtered.append(match)
    return filtered


def _best_odd(match: Match) -> float | None:
    """Devuelve la cuota más baja del partido (la más 'segura')."""
    candidates = [o for o in [match.odds.home, match.odds.draw, match.odds.away] if o is not None]
    valid = [o for o in candidates if ODDS_MIN <= o <= ODDS_MAX]
    return min(valid) if valid else None
