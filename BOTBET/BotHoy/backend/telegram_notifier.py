import asyncio
from datetime import datetime, timezone
import httpx
from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from backend.odds_api import fetch_matches, _cache as _odds_cache
from backend.filter import filter_matches
from backend.combinations import generate_combinations
from backend.gemini_api import evaluate_combinations, _fallback_evaluation


async def _run_pipeline():
    # Forzar fetch fresco (invalida el caché)
    _odds_cache["matches"] = None

    matches = await fetch_matches()
    filtered = filter_matches(matches)
    if not filtered:
        return None

    combos = generate_combinations(filtered)
    if not combos:
        return None

    top = combos[:20]
    try:
        evaluated = await evaluate_combinations(top)
    except Exception:
        evaluated = _fallback_evaluation(top)

    if not evaluated:
        return None

    # Priorizar la combinación cuyo partido más próximo está más cerca
    now = datetime.now(timezone.utc)
    def _next_kickoff(ec):
        times = []
        for m in [ec.combination.match_a, ec.combination.match_b]:
            try:
                t = datetime.fromisoformat(m.commence_time.replace("Z", "+00:00"))
                if t > now:
                    times.append(t)
            except Exception:
                pass
        return min(times) if times else datetime.max.replace(tzinfo=timezone.utc)

    evaluated.sort(key=_next_kickoff)
    return evaluated[0]


def _fmt_time(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%d/%m %H:%M UTC")
    except Exception:
        return iso


def _build_message(ec) -> str:
    c = ec.combination
    a, b = c.match_a, c.match_b
    rec_emoji = {"ALTA": "🟢", "MEDIA": "🟡", "BAJA": "🔴"}.get(ec.recommendation, "⚪")
    return (
        f"⚽ *BOTBET — SEÑAL AUTOMÁTICA*\n\n"
        f"{rec_emoji} Confianza: *{ec.recommendation}*   Score: *{ec.score}/10*\n"
        f"💰 Cuota combinada: *{c.combined_odds:.2f}*\n\n"
        f"🅐 *{a.home_team} vs {a.away_team}*\n"
        f"   📋 {a.league}\n"
        f"   🕐 {_fmt_time(a.commence_time)}\n"
        f"   1={a.odds.home}  X={a.odds.draw}  2={a.odds.away}\n\n"
        f"🅑 *{b.home_team} vs {b.away_team}*\n"
        f"   📋 {b.league}\n"
        f"   🕐 {_fmt_time(b.commence_time)}\n"
        f"   1={b.odds.home}  X={b.odds.draw}  2={b.odds.away}\n\n"
        f"💡 _{ec.reasoning[:220]}_"
    )


async def _send(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "Markdown",
        })
        r.raise_for_status()


async def send_signal():
    """Punto de entrada: corre el pipeline y envía señal a Telegram."""
    try:
        ec = await _run_pipeline()
        if ec is None:
            print("[Telegram] Sin combinaciones disponibles — señal omitida.")
            return
        msg = _build_message(ec)
        await _send(msg)
        a, b = ec.combination.match_a, ec.combination.match_b
        print(f"[Telegram] Señal enviada: {a.home_team} vs {a.away_team} + {b.home_team} vs {b.away_team}")
    except Exception as e:
        print(f"[Telegram] Error al enviar señal: {e}")


def run_signal_sync():
    """Wrapper síncrono para APScheduler."""
    asyncio.run(send_signal())
