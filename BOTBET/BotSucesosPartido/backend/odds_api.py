import asyncio
import time
import httpx
from config.settings import ODDS_API_KEY
from backend.models import Bet

_BASE = "https://api.the-odds-api.com/v4"

# Cache 2h para proteger el tier gratuito
_cache: dict = {"bets": None, "ts": 0.0}
_CACHE_TTL = 7200

# Mercados estadísticos — h2h excluido (no queremos resultado del partido)
# totals = over/under goles | spreads = hándicap asiático
_MARKETS = "totals,spreads"
_REGIONS = "eu,us,uk"

MARKET_LABELS: dict[str, str] = {
    "totals":  "Goles",
    "spreads": "Hándicap",
}


async def fetch_bets() -> list[Bet]:
    now = time.time()
    if _cache["bets"] is not None and (now - _cache["ts"]) < _CACHE_TTL:
        return _cache["bets"]

    async with httpx.AsyncClient(timeout=30) as client:
        sport_keys = await _fetch_soccer_sport_keys(client)

        sem = asyncio.Semaphore(10)

        async def _fetch_one(key: str) -> list[dict]:
            async with sem:
                return await _fetch_league_odds(client, key)

        results = await asyncio.gather(*[_fetch_one(k) for k in sport_keys])

    seen_events: set[str] = set()
    bets: list[Bet] = []

    for items in results:
        for item in items:
            eid = item.get("id", "")
            if eid in seen_events:
                continue
            seen_events.add(eid)
            bets.extend(_extract_bets(item))

    # Solo cachear si hay resultados (no cachear fallos)
    if bets:
        _cache["bets"] = bets
        _cache["ts"]   = time.time()
    print(f"[OddsAPI] Apuestas obtenidas: {len(bets)} desde {len(sport_keys)} ligas")
    return bets


async def _fetch_soccer_sport_keys(client: httpx.AsyncClient) -> list[str]:
    try:
        r = await client.get(f"{_BASE}/sports", params={"apiKey": ODDS_API_KEY})
        r.raise_for_status()
        keys = [s["key"] for s in r.json() if s.get("group") == "Soccer" and s.get("active")]
        print(f"[OddsAPI] Ligas activas de fútbol: {len(keys)}")
        return keys
    except Exception as e:
        print(f"[OddsAPI] ERROR al obtener ligas: {e}")
        return []


async def _fetch_league_odds(client: httpx.AsyncClient, sport_key: str) -> list[dict]:
    try:
        r = await client.get(
            f"{_BASE}/sports/{sport_key}/odds",
            params={
                "apiKey":      ODDS_API_KEY,
                "regions":     _REGIONS,
                "markets":     _MARKETS,
                "oddsFormat":  "decimal",
            },
        )
        if r.status_code in (404, 422):
            return []
        if r.status_code == 401:
            print(f"[OddsAPI] ERROR 401 — API key inválida o cuota agotada")
            return []
        if r.status_code == 429:
            print(f"[OddsAPI] ERROR 429 — Límite de peticiones alcanzado")
            return []
        r.raise_for_status()
        data = r.json()
        if data:
            print(f"[OddsAPI] {sport_key}: {len(data)} eventos")
        return data
    except Exception as e:
        print(f"[OddsAPI] ERROR en {sport_key}: {e}")
        return []


def _extract_bets(item: dict) -> list[Bet]:
    """Extrae todas las apuestas individuales de un evento, tomando la mejor cuota disponible."""
    match_id      = item.get("id", "")
    league        = item.get("sport_title", "")
    home_team     = item.get("home_team", "")
    away_team     = item.get("away_team", "")
    commence_time = item.get("commence_time", "")

    # Recolectar la mejor cuota disponible por (market, outcome_name, description)
    best: dict[tuple, float] = {}

    for bookmaker in item.get("bookmakers", []):
        for market in bookmaker.get("markets", []):
            mkey = market.get("key", "")
            if mkey not in MARKET_LABELS:
                continue
            for outcome in market.get("outcomes", []):
                name  = outcome.get("name", "")
                # 'point' lleva el valor de la línea (ej: 2.5 para totals, -0.5 para spreads)
                # 'description' es fallback para compatibilidad
                point = outcome.get("point")
                desc  = str(point) if point is not None else str(outcome.get("description", ""))
                price = float(outcome.get("price", 0.0))
                key   = (mkey, name, desc)
                if key not in best or price > best[key]:
                    best[key] = price

    bets: list[Bet] = []
    for (mkey, name, desc), price in best.items():
        outcome_label = _format_outcome(mkey, name, desc, home_team, away_team)
        if outcome_label is None:
            continue
        bets.append(Bet(
            match_id=match_id,
            league=league,
            home_team=home_team,
            away_team=away_team,
            commence_time=commence_time,
            market=mkey,
            market_label=MARKET_LABELS[mkey],
            outcome=outcome_label,
            odds=round(price, 3),
        ))

    return bets


def _format_outcome(market: str, name: str, desc: str, home: str, away: str) -> str | None:
    if market == "totals":
        if name == "Over":
            return f"Más de {desc} goles en el partido"
        if name == "Under":
            return f"Menos de {desc} goles en el partido"

    elif market == "spreads":
        role = "Local" if name == home else ("Visitante" if name == away else None)
        if role is None:
            return None
        try:
            val = float(desc)
        except (ValueError, TypeError):
            return f"{role} hándicap {desc}"

        equipo = "local" if role == "Local" else "visitante"

        if val == 0.0:
            # Draw No Bet: gana si gana, reembolso si empata, pierde si pierde
            return f"El {equipo} debe ganar (reembolso si empatan)"
        elif val > 0:
            # El equipo recibe ventaja: puede perder por hasta int(val) goles
            if val != int(val):  # .5 — no hay reembolso posible
                return f"El {equipo} puede perder por {int(val)} gol(es) y la apuesta igual gana"
            else:  # entero — hay reembolso si pierde exactamente por val
                m = int(val)
                return f"El {equipo} gana aunque pierda por {m} (reembolso si pierde por exactamente {m})"
        else:
            # El equipo da ventaja: debe ganar por margen suficiente
            abs_val = abs(val)
            if abs_val != int(abs_val):  # .5 — no hay reembolso
                m = int(abs_val) + 1
                return f"El {equipo} debe ganar por {m} goles o más"
            else:  # entero — reembolso si gana por exactamente abs_val
                m = int(abs_val)
                return f"El {equipo} debe ganar por {m + 1}+ goles (reembolso si gana por exactamente {m})"

    return None
