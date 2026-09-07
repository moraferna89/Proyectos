from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from backend.odds_api import fetch_matches
from backend.filter import filter_matches
from backend.combinations import generate_combinations
from backend.gemini_api import evaluate_combinations
from backend.models import AnalysisResult
from backend import database

app = FastAPI(title="BOTBET Dashboard", version="1.0.0")

# Inicializar BD al arrancar
database.init_db()

# Servir frontend estático
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/")
async def root():
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.get("/api/analyze", response_model=AnalysisResult)
async def analyze():
    """Pipeline completo: fetch → filter → combine → Gemini → resultado.
    Reutiliza combos ya guardados en BD y omite re-evaluarlos con Gemini."""

    # 1. Limpiar combos expirados (partidos ya comenzados)
    database.clean_expired()

    # 2. Cargar combos ya evaluados y guardados
    saved = database.load_saved_combos()
    saved_keys = database.get_saved_keys()

    # 3. Obtener partidos frescos de la API
    try:
        matches = await fetch_matches()
    except Exception as e:
        # Si falla la API pero hay guardados, devolverlos
        if saved:
            return AnalysisResult(
                total_matches_found=0,
                matches_filtered=0,
                combinations_generated=0,
                top_combinations=saved[:10],
            )
        raise HTTPException(status_code=502, detail=f"Error al obtener partidos: {e}")

    filtered = filter_matches(matches)
    all_combos = generate_combinations(filtered)

    # 4. Separar combos nuevos (no están en BD) de los ya evaluados
    def _key(combo):
        a, b = combo.match_a.id, combo.match_b.id
        return (a, b) if a <= b else (b, a)

    new_combos = [c for c in all_combos if _key(c) not in saved_keys]

    # 5. Evaluar solo los combos nuevos con Gemini (máximo 20)
    new_evaluated = []
    if new_combos:
        top_new = new_combos[:20]
        try:
            new_evaluated = await evaluate_combinations(top_new)
        except Exception:
            from backend.gemini_api import _fallback_evaluation
            new_evaluated = _fallback_evaluation(top_new)

        # 6. Guardar los nuevos en BD
        database.save_combos(new_evaluated)

    # 7. Combinar guardados + nuevos, ordenar por score y devolver top 10
    all_evaluated = saved + new_evaluated
    all_evaluated.sort(key=lambda ec: ec.score, reverse=True)

    return AnalysisResult(
        total_matches_found=len(matches),
        matches_filtered=len(filtered),
        combinations_generated=len(all_combos),
        top_combinations=all_evaluated,
    )


@app.get("/api/saved", response_model=AnalysisResult)
async def saved():
    """Devuelve los combos guardados en BD sin llamar a ninguna API externa."""
    database.clean_expired()
    combos = database.load_saved_combos()
    return AnalysisResult(
        total_matches_found=0,
        matches_filtered=0,
        combinations_generated=len(combos),
        top_combinations=combos,
    )


@app.get("/api/debug/matches")
async def debug_matches():
    """Ver partidos raw con sus cuotas reales (para ajustar filtros)."""
    try:
        matches = await fetch_matches()
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
    return sorted([
        {
            "commence_time": m.commence_time,
            "league": m.league,
            "match": f"{m.home_team} vs {m.away_team}",
            "min_odd": min(m.odds.home, m.odds.draw, m.odds.away),
        }
        for m in matches
    ], key=lambda x: x["commence_time"])


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "BOTBET"}
