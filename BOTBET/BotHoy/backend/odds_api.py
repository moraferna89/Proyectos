import asyncio
import time
import httpx
from config.settings import ODDS_API_KEY
from backend.models import Match, Odds

_BASE = "https://api.the-odds-api.com/v4"

# Cache 2h para proteger los 500 req/mes del tier gratuito
_cache: dict = {"matches": None, "ts": 0.0}
_CACHE_TTL = 7200


async def fetch_matches() -> list[Match]:
    now = time.time()
    if _cache["matches"] is not None and (now - _cache["ts"]) < _CACHE_TTL:
        return _cache["matches"]

    async with httpx.AsyncClient(timeout=30) as client:
        # 1. Obtener todos los deportes activos
        sport_keys = await _fetch_all_sport_keys(client)

        # 2. Obtener odds de cada deporte en paralelo (máx 10 concurrentes)
        sem = asyncio.Semaphore(10)
        async def _fetch_one(key: str) -> list[dict]:
            async with sem:
                return await _fetch_league_odds(client, key)

        results = await asyncio.gather(*[_fetch_one(k) for k in sport_keys])

    # 3. Aplanar, deduplicar y construir objetos Match
    seen: set[str] = set()
    matches: list[Match] = []
    for items in results:
        for item in items:
            fid = item.get("id", "")
            if fid in seen:
                continue
            seen.add(fid)
            odds = _extract_odds(item)
            if odds is None:
                continue
            sport_key = item.get("sport_key", "")
            matches.append(Match(
                id=fid,
                sport_key=sport_key,
                sport=_sport_name(sport_key),
                league=item.get("sport_title", ""),
                home_team=item.get("home_team", ""),
                away_team=item.get("away_team", ""),
                commence_time=item.get("commence_time", ""),
                odds=odds,
            ))

    _cache["matches"] = matches
    _cache["ts"] = time.time()
    return matches


async def _fetch_all_sport_keys(client: httpx.AsyncClient) -> list[str]:
    try:
        r = await client.get(
            f"{_BASE}/sports",
            params={"apiKey": ODDS_API_KEY},
        )
        r.raise_for_status()
        sports = r.json()
        return [s["key"] for s in sports if s.get("active")]
    except Exception:
        return []


async def _fetch_league_odds(client: httpx.AsyncClient, sport_key: str) -> list[dict]:
    try:
        r = await client.get(
            f"{_BASE}/sports/{sport_key}/odds",
            params={
                "apiKey": ODDS_API_KEY,
                "regions": "eu",
                "markets": "h2h",
                "oddsFormat": "decimal",
            },
        )
        if r.status_code == 422:
            return []
        r.raise_for_status()
        return r.json()
    except Exception:
        return []


_SPORT_NAMES: dict[str, str] = {
    "soccer":           "Fútbol",
    "basketball":       "Baloncesto",
    "tennis":           "Tenis",
    "americanfootball": "Fútbol Americano",
    "baseball":         "Béisbol",
    "icehockey":        "Hockey Hielo",
    "mma":              "MMA",
    "cricket":          "Cricket",
    "rugby":            "Rugby",
    "aussierules":      "Fútbol Australiano",
    "golf":             "Golf",
    "boxing":           "Boxeo",
    "volleyball":       "Vóleibol",
    "handball":         "Balonmano",
    "cycling":          "Ciclismo",
    "snooker":          "Snooker",
    "darts":            "Dardos",
}

def _sport_name(sport_key: str) -> str:
    prefix = sport_key.split("_")[0].lower()
    return _SPORT_NAMES.get(prefix, prefix.capitalize())


def _extract_odds(item: dict) -> Odds | None:
    home_team = item.get("home_team", "")
    away_team = item.get("away_team", "")
    for bookmaker in item.get("bookmakers", []):
        for market in bookmaker.get("markets", []):
            if market.get("key") != "h2h":
                continue
            outcomes = {o["name"]: o["price"] for o in market.get("outcomes", [])}
            home = outcomes.get(home_team)
            away = outcomes.get(away_team)
            if not (home and away):
                continue
            draw = outcomes.get("Draw")
            return Odds(
                home=float(home),
                draw=float(draw) if draw else None,
                away=float(away),
            )
    return None
