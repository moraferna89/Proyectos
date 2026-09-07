import google.generativeai as genai
from config.settings import GEMINI_API_KEY, ODDS_MIN, ODDS_MAX
from backend.models import Combination, EvaluatedCombo, Match

genai.configure(api_key=GEMINI_API_KEY)
_MODELS = ["gemini-2.5-flash-lite", "gemini-2.0-flash-lite", "gemini-flash-lite-latest"]


async def evaluate_combinations(combos: list[Combination]) -> list[EvaluatedCombo]:
    """Envía las combinaciones a Gemini para análisis y ranking. Intenta varios modelos."""
    if not combos:
        return []

    prompt = _build_prompt(combos)

    for model_name in _MODELS:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return _parse_response(response.text, combos)
        except Exception as e:
            err = str(e)
            if "429" in err or "quota" in err.lower() or "404" in err:
                continue
            raise

    return _fallback_evaluation(combos)


def _bet_info(match: Match) -> tuple[str, float]:
    """Devuelve (etiqueta, cuota) del resultado que se va a apostar (el que cae en rango 1.4-1.8)."""
    candidates = [
        ("Local",      match.odds.home),
        ("Empate",     match.odds.draw),
        ("Visitante",  match.odds.away),
    ]
    valid = [(label, odd) for label, odd in candidates if ODDS_MIN <= odd <= ODDS_MAX]
    if valid:
        return min(valid, key=lambda x: x[1])
    return min(candidates, key=lambda x: x[1])


def _fmt_time(iso: str) -> str:
    from datetime import datetime, timezone
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%d/%m %H:%M UTC")
    except Exception:
        return iso


def _build_prompt(combos: list[Combination]) -> str:
    header = """Eres un analista especializado en apuestas deportivas de fútbol combinadas.

CONTEXTO:
El sistema filtra automáticamente partidos donde un resultado tiene cuota entre 1.40 y 1.80 (favoritos claros).
Tu tarea es evaluar qué tan CONFIABLE es apostar a ese resultado específico en cada combinación de 2 partidos.
La apuesta que se va a realizar ya está indicada para cada partido (Local / Empate / Visitante).

CRITERIOS DE EVALUACIÓN (considera cada uno):
1. Diferencia de nivel real entre los equipos — ¿el favorito es dominante o hay incertidumbre?
2. Calidad y predecibilidad de la liga:
   - ALTA: FIFA World Cup, UEFA Champions/Europa League, Euros, Premier League, LaLiga, Bundesliga, Serie A, Ligue 1, Copa América, Nations League
   - MEDIA: Eredivisie, Brasileirao Serie A, Liga MX, MLS, Copa Libertadores, ligas de segunda de las top 5
   - BAJA: Serie B Brasil, Veikkausliiga (Finlandia), ligas escandinavas, ligas de Europa del Este, ligas menores
3. Cuota del favorito — cuanto más baja, más predecible se considera el resultado:
   - 1.40–1.55: favorito dominante
   - 1.56–1.70: favorito claro pero con riesgo
   - 1.71–1.80: favorito ajustado, más incertidumbre
4. Cuota combinada total — zona óptima 1.96–2.50; por encima de 3.00 el riesgo es elevado
5. Contexto del partido — rivalidades históricas, fase de la competición, motivación

RÚBRICA DE SCORING (obligatorio respetar):
  9–10 → Dos favoritos dominantes (cuota ≤1.60) en ligas de predecibilidad ALTA. Casi sin margen de sorpresa.
  7–8  → Favoritos claros en ligas ALTA, o favoritos dominantes en ligas MEDIA. Riesgo bajo-moderado.
  5–6  → Al menos un partido en liga MEDIA con cuota ajustada, o un partido en liga BAJA aunque el favorito sea claro.
  3–4  → Una liga BAJA o un partido con cuota 1.70–1.80 en liga impredecible. Riesgo notable.
  1–2  → Ambas ligas BAJA, o combinación de factores que hacen muy probable una sorpresa.

FORMATO DE RESPUESTA — JSON puro, sin texto antes ni después, sin bloques de código:
[{"index": 0, "score": 7, "reasoning": "[Partido A]: análisis. [Partido B]: análisis. [Combinación]: justificación del score."}]

NOTA: el campo "recommendation" NO es necesario, se calcula automáticamente desde el score.

COMBINACIONES A EVALUAR:
"""

    lines = [header]
    for i, combo in enumerate(combos):
        a, b = combo.match_a, combo.match_b
        bet_a_label, bet_a_odd = _bet_info(a)
        bet_b_label, bet_b_odd = _bet_info(b)

        lines.append(f"--- COMBO {i} ---")
        lines.append(f"Partido A: [{a.league}] {a.home_team} vs {a.away_team} | {_fmt_time(a.commence_time)}")
        lines.append(f"  Apuesta: {bet_a_label} @ {bet_a_odd}  (todas las cuotas — L:{a.odds.home} E:{a.odds.draw} V:{a.odds.away})")
        lines.append(f"Partido B: [{b.league}] {b.home_team} vs {b.away_team} | {_fmt_time(b.commence_time)}")
        lines.append(f"  Apuesta: {bet_b_label} @ {bet_b_odd}  (todas las cuotas — L:{b.odds.home} E:{b.odds.draw} V:{b.odds.away})")
        lines.append(f"Cuota combinada total: {combo.combined_odds}")
        lines.append("")

    return "\n".join(lines)


def _parse_response(text: str, combos: list[Combination]) -> list[EvaluatedCombo]:
    import json
    import re

    # Extraer JSON: primero intentar bloque ```json ... ```, luego array directo
    json_block = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", text, re.DOTALL)
    raw = json_block.group(1) if json_block else None

    if not raw:
        array_match = re.search(r"\[.*\]", text, re.DOTALL)
        raw = array_match.group() if array_match else None

    if not raw:
        return _fallback_evaluation(combos)

    try:
        items = json.loads(raw)
    except json.JSONDecodeError:
        return _fallback_evaluation(combos)

    results = []
    seen_indexes = set()
    for item in items:
        idx = item.get("index", 0)
        if idx >= len(combos) or idx in seen_indexes:
            continue
        seen_indexes.add(idx)
        score = max(1, min(10, int(item.get("score", 5))))
        recommendation = "ALTA" if score >= 7 else "MEDIA" if score >= 5 else "BAJA"
        results.append(EvaluatedCombo(
            combination=combos[idx],
            score=score,
            reasoning=item.get("reasoning", "Sin análisis disponible."),
            recommendation=recommendation,
        ))

    results.sort(key=lambda r: r.score, reverse=True)
    return results


def _fallback_evaluation(combos: list[Combination]) -> list[EvaluatedCombo]:
    """Evaluación básica si Gemini no responde correctamente."""
    return [
        EvaluatedCombo(
            combination=c,
            score=5,
            reasoning="Análisis automático no disponible.",
            recommendation="MEDIA",
        )
        for c in combos
    ]
