import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from backend.models import Combination, EvaluatedCombo, Match, Odds

DB_PATH = Path(__file__).parent.parent / "data" / "combos.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS evaluated_combos (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                match_a_id      TEXT NOT NULL,
                match_b_id      TEXT NOT NULL,
                a_sport_key     TEXT,
                a_league        TEXT,
                a_home_team     TEXT,
                a_away_team     TEXT,
                a_commence_time TEXT,
                a_odds_home     REAL,
                a_odds_draw     REAL,
                a_odds_away     REAL,
                b_sport_key     TEXT,
                b_league        TEXT,
                b_home_team     TEXT,
                b_away_team     TEXT,
                b_commence_time TEXT,
                b_odds_home     REAL,
                b_odds_draw     REAL,
                b_odds_away     REAL,
                combined_odds   REAL,
                score           INTEGER,
                reasoning       TEXT,
                recommendation  TEXT,
                saved_at        TEXT,
                UNIQUE(match_a_id, match_b_id)
            )
        """)


def clean_expired() -> int:
    """Elimina combos donde alguno de los partidos ya comenzó. Retorna cuántos se borraron."""
    now = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        cursor = conn.execute(
            "DELETE FROM evaluated_combos WHERE a_commence_time < ? OR b_commence_time < ?",
            (now, now),
        )
        return cursor.rowcount


def get_saved_keys() -> set[tuple[str, str]]:
    """Retorna el conjunto de pares (min_id, max_id) ya evaluados en la BD."""
    with _connect() as conn:
        rows = conn.execute("SELECT match_a_id, match_b_id FROM evaluated_combos").fetchall()
    return {(r["match_a_id"], r["match_b_id"]) for r in rows}


def load_saved_combos() -> list[EvaluatedCombo]:
    """Carga todos los combos guardados ordenados por score descendente."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM evaluated_combos ORDER BY score DESC"
        ).fetchall()
    return [_row_to_combo(r) for r in rows]


def save_combos(combos: list[EvaluatedCombo]) -> None:
    """Inserta combos nuevos; ignora duplicados (por par de match IDs)."""
    now = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        for ec in combos:
            a = ec.combination.match_a
            b = ec.combination.match_b
            # Normalizar orden para que (A,B) y (B,A) no generen duplicados
            a_id, b_id = (a.id, b.id) if a.id <= b.id else (b.id, a.id)
            ma, mb = (a, b) if a.id <= b.id else (b, a)
            conn.execute("""
                INSERT OR IGNORE INTO evaluated_combos (
                    match_a_id, match_b_id,
                    a_sport_key, a_league, a_home_team, a_away_team, a_commence_time,
                    a_odds_home, a_odds_draw, a_odds_away,
                    b_sport_key, b_league, b_home_team, b_away_team, b_commence_time,
                    b_odds_home, b_odds_draw, b_odds_away,
                    combined_odds, score, reasoning, recommendation, saved_at
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                a_id, b_id,
                ma.sport_key, ma.league, ma.home_team, ma.away_team, ma.commence_time,
                ma.odds.home, ma.odds.draw, ma.odds.away,
                mb.sport_key, mb.league, mb.home_team, mb.away_team, mb.commence_time,
                mb.odds.home, mb.odds.draw, mb.odds.away,
                ec.combination.combined_odds,
                ec.score, ec.reasoning, ec.recommendation, now,
            ))


def _row_to_combo(r: sqlite3.Row) -> EvaluatedCombo:
    match_a = Match(
        id=r["match_a_id"],
        sport_key=r["a_sport_key"],
        league=r["a_league"],
        home_team=r["a_home_team"],
        away_team=r["a_away_team"],
        commence_time=r["a_commence_time"],
        odds=Odds(home=r["a_odds_home"], draw=r["a_odds_draw"], away=r["a_odds_away"]),
    )
    match_b = Match(
        id=r["match_b_id"],
        sport_key=r["b_sport_key"],
        league=r["b_league"],
        home_team=r["b_home_team"],
        away_team=r["b_away_team"],
        commence_time=r["b_commence_time"],
        odds=Odds(home=r["b_odds_home"], draw=r["b_odds_draw"], away=r["b_odds_away"]),
    )
    return EvaluatedCombo(
        combination=Combination(
            match_a=match_a,
            match_b=match_b,
            combined_odds=r["combined_odds"],
        ),
        score=r["score"],
        reasoning=r["reasoning"],
        recommendation=r["recommendation"],
    )
