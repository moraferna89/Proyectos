import asyncio
from datetime import datetime, timezone
import httpx
from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from backend.odds_api import fetch_bets, _cache as _odds_cache
from backend.filter import filter_bets
from backend.combinations import generate_bet_combinations
from backend.gemini_api import evaluate_combinations, _fallback_evaluation


async def _run_pipeline():
    # Forzar fetch fresco (invalida el caché)
    _odds_cache["bets"] = None

    all_bets = await fetch_bets()
    filtered = filter_bets(all_bets)
    if not filtered:
        return None

    combos = generate_bet_combinations(filtered)
    if not combos:
        return None

    try:
        evaluated = await evaluate_combinations(combos)
    except Exception:
        evaluated = _fallback_evaluation(combos)

    if not evaluated:
        return None

    # Priorizar la combinación con el partido más próximo
    now = datetime.now(timezone.utc)

    def _next_kickoff(ec):
        times = []
        for bet in [ec.combination.bet_a, ec.combination.bet_b]:
            try:
                t = datetime.fromisoformat(bet.commence_time.replace("Z", "+00:00"))
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
    a, b = c.bet_a, c.bet_b
    rec_emoji = {"ALTA": "🟢", "MEDIA": "🟡", "BAJA": "🔴"}.get(ec.recommendation, "⚪")
    return (
        f"⚽ *BOTBET — SEÑAL AUTOMÁTICA*\n\n"
        f"{rec_emoji} Confianza: *{ec.recommendation}*   Score: *{ec.score}/10*\n"
        f"💰 Cuota combinada: *{c.combined_odds:.3f}*\n\n"
        f"🅐 *{a.home_team} vs {a.away_team}*\n"
        f"   📋 {a.league}\n"
        f"   🎯 {a.market_label}: *{a.outcome}*   @ {a.odds}\n"
        f"   🕐 {_fmt_time(a.commence_time)}\n\n"
        f"🅑 *{b.home_team} vs {b.away_team}*\n"
        f"   📋 {b.league}\n"
        f"   🎯 {b.market_label}: *{b.outcome}*   @ {b.odds}\n"
        f"   🕐 {_fmt_time(b.commence_time)}\n\n"
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
    try:
        ec = await _run_pipeline()
        if ec is None:
            print("[Telegram] Sin combinaciones disponibles — señal omitida.")
            return
        msg = _build_message(ec)
        await _send(msg)
        a, b = ec.combination.bet_a, ec.combination.bet_b
        print(f"[Telegram] Señal: {a.outcome} ({a.home_team}) + {b.outcome} ({b.home_team})")
    except Exception as e:
        print(f"[Telegram] Error al enviar señal: {e}")


def run_signal_sync():
    asyncio.run(send_signal())
