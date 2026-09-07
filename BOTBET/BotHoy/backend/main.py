from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from backend.odds_api import fetch_matches
from backend.filter import filter_matches
from backend.combinations import generate_combinations
from backend.gemini_api import evaluate_all_combinations
from backend.models import AnalysisResult

app = FastAPI(title="BOTBET Dashboard", version="1.0.0")

# Servir frontend estático
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/")
async def root():
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.get("/api/analyze", response_model=AnalysisResult)
async def analyze():
    """Pipeline completo: fetch → filter → combine → Gemini → resultado."""
    try:
        matches = await fetch_matches()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error al obtener partidos: {e}")

    filtered = filter_matches(matches)
    combos = generate_combinations(filtered)

    try:
        evaluated = await evaluate_all_combinations(combos)
    except Exception:
        from backend.gemini_api import _fallback_evaluation
        evaluated = _fallback_evaluation(combos)

    return AnalysisResult(
        total_matches_found=len(matches),
        matches_filtered=len(filtered),
        combinations_generated=len(combos),
        top_combinations=evaluated,
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
