from pydantic import BaseModel


class Bet(BaseModel):
    match_id: str
    league: str
    home_team: str
    away_team: str
    commence_time: str
    market: str        # totals | btts | spreads | h2h
    market_label: str  # etiqueta en español
    outcome: str       # "Más de 2.5 goles", "Ambos anotan: Sí", etc.
    odds: float


class BetCombo(BaseModel):
    bet_a: Bet
    bet_b: Bet
    combined_odds: float


class EvaluatedBetCombo(BaseModel):
    combination: BetCombo
    score: int
    reasoning: str
    recommendation: str  # ALTA | MEDIA | BAJA


class PropAnalysisResult(BaseModel):
    total_bets_found: int
    bets_in_range: int
    combinations_generated: int
    top_combinations: list[EvaluatedBetCombo]
