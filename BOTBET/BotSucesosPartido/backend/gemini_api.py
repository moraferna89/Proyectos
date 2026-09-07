import google.generativeai as genai
from config.settings import GEMINI_API_KEY
from backend.models import BetCombo, EvaluatedBetCombo

genai.configure(api_key=GEMINI_API_KEY)

_MODELS = ["gemini-2.5-flash-lite", "gemini-2.0-flash-lite", "gemini-flash-lite-latest"]


async def evaluate_combinations(combos: list[BetCombo]) -> list[EvaluatedBetCombo]:
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


def _build_prompt(combos: list[BetCombo]) -> str:
    lines = [
        "Eres un experto en apuestas deportivas de fútbol especializado en mercados estadísticos.",
        "Analiza las siguientes combinadas de 2 apuestas individuales.",
        "",
        "Mercados disponibles:",
        "  • 'Más/Menos de X.X goles': evalúa el potencial goleador según liga, equipos y estilo de juego",
        "  • 'Local/Visitante hándicap ±X.X': evalúa la diferencia de nivel real entre ambos equipos",
        "",
        "Para cada combinación evalúa:",
        "  1. Probabilidad individual de cada apuesta basándote en la liga, los equipos y el mercado",
        "  2. Si ambas apuestas son independientes o se correlacionan positivamente",
        "  3. Si la cuota combinada justifica el riesgo (rango esperado 1.4–1.85 por apuesta)",
        "",
        "Criterio de score:",
        "  10 = ambas apuestas muy probables, excelente combinación",
        "  7–9 = una apuesta muy sólida y la otra razonable",
        "  5–6 = razonable pero con incertidumbre",
        "  1–4 = muy arriesgada, no recomendable",
        "",
        "RESPONDE SOLO JSON (sin texto adicional):",
        '[{"index": 0, "score": 8, "reasoning": "...", "recommendation": "ALTA|MEDIA|BAJA"}]',
        "  ALTA = score >= 7 | MEDIA = score 5-6 | BAJA = score <= 4",
        "",
        "COMBINADAS A ANALIZAR:",
    ]

    for i, combo in enumerate(combos):
        a, b = combo.bet_a, combo.bet_b
        lines.append(
            f"{i}. [{a.league}] {a.home_team} vs {a.away_team} | "
            f"{a.market_label}: {a.outcome} @ {a.odds} | {a.commence_time[:10]}"
        )
        lines.append(
            f"   + [{b.league}] {b.home_team} vs {b.away_team} | "
            f"{b.market_label}: {b.outcome} @ {b.odds} | {b.commence_time[:10]}"
        )
        lines.append(f"   Cuota combinada: {combo.combined_odds}")

    return "\n".join(lines)


def _parse_response(text: str, combos: list[BetCombo]) -> list[EvaluatedBetCombo]:
    import json, re

    match = re.search(r"\[.*\]", text, re.DOTALL)
    if not match:
        return _fallback_evaluation(combos)

    try:
        items = json.loads(match.group())
    except json.JSONDecodeError:
        return _fallback_evaluation(combos)

    results = []
    for item in items:
        idx = item.get("index", 0)
        if idx >= len(combos):
            continue
        results.append(EvaluatedBetCombo(
            combination=combos[idx],
            score=int(item.get("score", 5)),
            reasoning=item.get("reasoning", "Sin análisis disponible."),
            recommendation=item.get("recommendation", "MEDIA"),
        ))

    results.sort(key=lambda r: r.score, reverse=True)
    return results


def _fallback_evaluation(combos: list[BetCombo]) -> list[EvaluatedBetCombo]:
    return [
        EvaluatedBetCombo(
            combination=c,
            score=5,
            reasoning="Análisis automático no disponible.",
            recommendation="MEDIA",
        )
        for c in combos
    ]
