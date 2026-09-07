from itertools import combinations
from backend.models import Match, Combination
from config.settings import COMBO_SIZE


def generate_combinations(matches: list[Match]) -> list[Combination]:
    """Genera todas las combinaciones de COMBO_SIZE partidos."""
    combos = []
    for pair in combinations(matches, COMBO_SIZE):
        a, b = pair[0], pair[1]
        combined_odds = _best_odd(a) * _best_odd(b)
        combos.append(Combination(
            match_a=a,
            match_b=b,
            combined_odds=round(combined_odds, 3),
        ))
    # Ordenar por cuota combinada ascendente (menor riesgo primero)
    combos.sort(key=lambda c: c.combined_odds)
    return combos


def _best_odd(match: Match) -> float:
    from config.settings import ODDS_MIN, ODDS_MAX
    candidates = [o for o in [match.odds.home, match.odds.draw, match.odds.away] if o is not None]
    valid = [o for o in candidates if ODDS_MIN <= o <= ODDS_MAX]
    return min(valid) if valid else min(candidates)
