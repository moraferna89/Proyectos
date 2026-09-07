from itertools import combinations
from config.settings import ODDS_MIN, ODDS_MAX
from backend.models import Bet, BetCombo

# Rango válido de cuota combinada: 1.35×1.35 a 1.95×1.95
_COMBINED_MIN = round(ODDS_MIN * ODDS_MIN, 4)   # ~1.82
_COMBINED_MAX = round(ODDS_MAX * ODDS_MAX, 4)   # ~3.80

# Máximo de combinaciones por par de partidos (diversidad)
_MAX_PER_MATCH_PAIR = 3

# Cuántas combinaciones pasar a Gemini como máximo
MAX_FOR_GEMINI = 100


def generate_bet_combinations(bets: list[Bet]) -> list[BetCombo]:
    """
    Genera pares de apuestas con cuota combinada en rango válido.
    Aplica filtro de diversidad: máximo _MAX_PER_MATCH_PAIR combos por par de partidos.
    """
    # Paso 1: Generar todas las combinaciones en rango
    raw: list[BetCombo] = []
    for a, b in combinations(bets, 2):
        combined = round(a.odds * b.odds, 3)
        if _COMBINED_MIN <= combined <= _COMBINED_MAX:
            raw.append(BetCombo(bet_a=a, bet_b=b, combined_odds=combined))

    # Paso 2: Ordenar por cuota combinada ascendente (más seguras primero)
    raw.sort(key=lambda c: c.combined_odds)

    # Paso 3: Filtro de diversidad — máximo _MAX_PER_MATCH_PAIR por par de partidos
    pair_count: dict[frozenset, int] = {}
    diverse: list[BetCombo] = []

    for combo in raw:
        pair_key = frozenset([combo.bet_a.match_id, combo.bet_b.match_id])
        count = pair_count.get(pair_key, 0)
        if count < _MAX_PER_MATCH_PAIR:
            pair_count[pair_key] = count + 1
            diverse.append(combo)
        if len(diverse) >= MAX_FOR_GEMINI:
            break

    return diverse
