import google.generativeai as genai
from config.settings import GEMINI_API_KEY
from backend.models import Combination, EvaluatedCombo

genai.configure(api_key=GEMINI_API_KEY)
_MODELS = ["gemini-2.5-flash-lite", "gemini-2.0-flash-lite", "gemini-flash-lite-latest"]
_model = None

def _get_model():
    global _model
    if _model is None:
        _model = genai.GenerativeModel(_MODELS[0])
    return _model


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


async def evaluate_all_combinations(combos: list[Combination], batch_size: int = 20) -> list[EvaluatedCombo]:
    """Evalúa TODAS las combinaciones en lotes para soportar grandes cantidades."""
    if not combos:
        return []

    all_results: list[EvaluatedCombo] = []
    for i in range(0, len(combos), batch_size):
        batch = combos[i:i + batch_size]
        try:
            results = await evaluate_combinations(batch)
            all_results.extend(results)
        except Exception:
            all_results.extend(_fallback_evaluation(batch))

    all_results.sort(key=lambda r: r.score, reverse=True)
    return all_results


def _build_prompt(combos: list[Combination]) -> str:
    lines = [
        "Eres un experto en análisis de apuestas deportivas multideporte.",
        "Analiza las siguientes combinaciones de 2 eventos para apuesta combinada.",
        "Para cada combinación evalúa: forma reciente de los participantes, diferencia de nivel, deporte/competición, hora del evento.",
        "Asigna un score del 1 al 10 (10 = más recomendable) y una justificación breve.",
        "",
        "RESPONDE EN FORMATO JSON con este esquema:",
        '[{"index": 0, "score": 8, "reasoning": "...", "recommendation": "ALTA|MEDIA|BAJA"}]',
        "",
        "COMBINACIONES:",
    ]
    for i, combo in enumerate(combos):
        a, b = combo.match_a, combo.match_b
        draw_a = f" X:{a.odds.draw}" if a.odds.draw else ""
        draw_b = f" X:{b.odds.draw}" if b.odds.draw else ""
        lines.append(
            f"{i}. [{a.sport} · {a.league}] {a.home_team} vs {a.away_team} "
            f"(1:{a.odds.home}{draw_a} 2:{a.odds.away}) @ {a.commence_time}"
        )
        lines.append(
            f"   + [{b.sport} · {b.league}] {b.home_team} vs {b.away_team} "
            f"(1:{b.odds.home}{draw_b} 2:{b.odds.away}) @ {b.commence_time}"
        )
        lines.append(f"   Cuota combinada: {combo.combined_odds}")

    return "\n".join(lines)


def _parse_response(text: str, combos: list[Combination]) -> list[EvaluatedCombo]:
    import json
    import re

    # Extraer JSON del texto de Gemini
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
        results.append(EvaluatedCombo(
            combination=combos[idx],
            score=item.get("score", 5),
            reasoning=item.get("reasoning", "Sin análisis disponible."),
            recommendation=item.get("recommendation", "MEDIA"),
        ))

    # Ordenar por score descendente
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
