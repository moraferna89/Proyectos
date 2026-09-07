from pydantic import BaseModel
from typing import Optional


class Odds(BaseModel):
    home: float
    draw: float
    away: float


class Match(BaseModel):
    id: str
    sport_key: str
    league: str
    home_team: str
    away_team: str
    commence_time: str
    odds: Odds


class Combination(BaseModel):
    match_a: Match
    match_b: Match
    combined_odds: float


class EvaluatedCombo(BaseModel):
    combination: Combination
    score: int
    reasoning: str
    recommendation: str


class AnalysisResult(BaseModel):
    total_matches_found: int
    matches_filtered: int
    combinations_generated: int
    top_combinations: list[EvaluatedCombo]
