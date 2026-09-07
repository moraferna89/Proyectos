from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from backend.odds_api import fetch_bets
from backend.filter import filter_bets
from backend.combinations import generate_bet_combinations
from backend.gemini_api import evaluate_combinations, _fallback_evaluation
from backend.models import PropAnalysisResult

app = FastAPI(title="BotSucesosPartido", version="2.0.0")

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/")
async def root():
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.get("/api/analyze", response_model=PropAnalysisResult)
async def analyze():
    """Pipeline: fetch todos los mercados → filtrar por cuota → combinar → Gemini → top 50."""
    try:
        all_bets = await fetch_bets()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error al obtener cuotas: {e}")

    filtered = filter_bets(all_bets)
    combos   = generate_bet_combinations(filtered)

    try:
        evaluated = await evaluate_combinations(combos)
    except Exception:
        evaluated = _fallback_evaluation(combos)

    return PropAnalysisResult(
        total_bets_found=len(all_bets),
        bets_in_range=len(filtered),
        combinations_generated=len(combos),
        top_combinations=evaluated[:50],
    )


@app.get("/api/debug/bets")
async def debug_bets():
    """Ver todas las apuestas individuales en rango para ajustar filtros."""
    try:
        all_bets = await fetch_bets()
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    filtered = filter_bets(all_bets)
    return sorted([
        {
            "commence_time": b.commence_time,
            "league":        b.league,
            "match":         f"{b.home_team} vs {b.away_team}",
            "market":        b.market_label,
            "outcome":       b.outcome,
            "odds":          b.odds,
        }
        for b in filtered
    ], key=lambda x: x["commence_time"])


@app.get("/api/debug/api-test")
async def debug_api_test():
    """Diagnóstico completo: prueba la API y muestra qué se obtiene."""
    import httpx
    from config.settings import ODDS_API_KEY
    from backend.odds_api import _BASE, _MARKETS

    resultado = {"api_key_preview": ODDS_API_KEY[:8] + "...", "markets": _MARKETS}

    # 1. Probar /sports
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(f"{_BASE}/sports", params={"apiKey": ODDS_API_KEY})
            resultado["sports_status"] = r.status_code
            if r.status_code == 200:
                sports = r.json()
                soccer = [s["key"] for s in sports if s.get("group") == "Soccer" and s.get("active")]
                resultado["soccer_leagues_count"] = len(soccer)
                resultado["soccer_leagues_sample"] = soccer[:5]
            else:
                resultado["sports_error"] = r.text[:300]
    except Exception as e:
        resultado["sports_exception"] = str(e)

    # 2. Probar odds de la primera liga disponible
    if resultado.get("soccer_leagues_sample"):
        liga = resultado["soccer_leagues_sample"][0]
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.get(
                    f"{_BASE}/sports/{liga}/odds",
                    params={"apiKey": ODDS_API_KEY, "regions": "eu",
                            "markets": _MARKETS, "oddsFormat": "decimal"},
                )
                resultado["odds_test_league"] = liga
                resultado["odds_test_status"] = r.status_code
                if r.status_code == 200:
                    events = r.json()
                    resultado["events_count"] = len(events)
                    if events:
                        ev = events[0]
                        bkm = ev.get("bookmakers", [])
                        resultado["first_event"] = f"{ev.get('home_team')} vs {ev.get('away_team')}"
                        resultado["bookmakers_count"] = len(bkm)
                        resultado["markets_available"] = [
                            m["key"] for bk in bkm for m in bk.get("markets", [])
                        ][:10]
                else:
                    resultado["odds_error"] = r.text[:300]
        except Exception as e:
            resultado["odds_exception"] = str(e)

    # 3. Estado del filtro
    from backend.odds_api import fetch_bets
    from backend.filter import filter_bets
    all_bets = await fetch_bets()
    filtered  = filter_bets(all_bets)
    resultado["total_bets_fetched"] = len(all_bets)
    resultado["bets_in_range_1_4_1_7"] = len(filtered)
    if all_bets:
        sample = all_bets[:3]
        resultado["sample_bets"] = [
            {"match": f"{b.home_team} vs {b.away_team}", "market": b.market_label,
             "outcome": b.outcome, "odds": b.odds}
            for b in sample
        ]

    return resultado


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "BotSucesosPartido"}
