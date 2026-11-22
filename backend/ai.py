import os
import threading
from openai import OpenAI
from data import stat_seasons

MODEL = os.getenv("EXPLAIN_MODEL", "gpt-4.1-mini")

_client = None
_client_lock = threading.Lock()
_explanations = {}
_MAX_CACHED = 2000

SYSTEM_PROMPT = """You are a fantasy football analyst sitting next to a manager during a live snake draft. They are on the clock, scanning a list of about ten recommended players, and you write the short note under one of them. The manager reads every note side by side, so each one has to say something the others don't.

Write exactly 2 sentences, 45 words at most, plain text.
- Sentence one: the case for him, built on the single most telling fact in his data: a production jump or decline (with the numbers), his role, his age, an injury designation, or a steep drop-off at his position.
- Sentence two: the decision, meaning what taking him now does for this roster versus the best option at another position, e.g. locking in the second WR now and waiting on TE, or why he can wait.

Rules:
- Use only the facts provided. Never invent stats, injuries, coaching or scheme changes, quarterback chemistry, contracts or team news.
- Quote numbers exactly as given. Never mention scores, the model, or the recommendation engine.
- Only describe a drop-off, a tier, or someone being "the last" at a position when the facts state it.
- You only know the players named here. Never make league-wide comparisons like "led all TEs" or "best in the league", and never predict how long players will last.
- For recommendation #6 or later, make the honest case for when he is the right call, not a sales pitch.
- If he would only fill a bench spot, say so plainly.
- Vary your phrasing: don't open with his name, "Ranked", or "Entering". Refer to him as "he" or by last name.
- Banned words: excellent, solid, promising, significant, strategic, steal, league-winner, enhance, bolster, corps, upside play. No hedging, no exclamation marks.

Example of the tone (different player, illustrative only):
Targets jumped from 88 to 131 and he's the last WR left inside the top 40, so the drop after him is steep. Taking him fills your WR2 now and leaves tight end for later, where the top option, Kincaid, sits nine spots further down the rankings."""


def _get_client():
    global _client
    with _client_lock:
        if _client is None:
            _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        return _client


def explain_pick(player, roster, round_number, context=None):
    # Cache on the exact prompt: any change in roster, round, or player facts
    # produces a new prompt and a fresh explanation.
    prompt = _build_prompt(player, roster, round_number, context or {})
    if prompt in _explanations:
        return _explanations[prompt]
    text = _request_explanation(prompt)
    if len(_explanations) >= _MAX_CACHED:
        _explanations.clear()
    _explanations[prompt] = text
    return text


def _trend(label, new, old):
    new, old = new or 0, old or 0
    last, prev = stat_seasons()
    if new and old:
        pct = round((new - old) / old * 100)
        direction = "up" if pct > 0 else "down" if pct < 0 else "flat"
        return f"{label}: {old} ({prev}) → {new} ({last}), {direction} {abs(pct)}%"
    if new:
        return f"{label}: {new} in {last} (no {prev} data)"
    if old:
        return f"{label}: {old} in {prev}, none in {last}"
    return None


def _ordinal(n):
    suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _build_prompt(player, roster, round_number, context):
    position = player.get("position")
    years_exp = player.get("years_exp") or 0
    depth = player.get("depth_chart_order")
    injury_status = player.get("injury_status")
    search_rank = player.get("search_rank")

    if depth == 1:
        role = "listed starter on depth chart"
    elif depth == 2:
        role = "No. 2 on depth chart (backup)"
    elif depth:
        role = f"No. {depth} on depth chart"
    else:
        role = "depth chart role unknown"
    experience = "rookie" if years_exp == 0 else f"entering year {years_exp + 1}"

    lines = [
        f"PLAYER: {player['full_name']}, {position}, {player.get('team') or 'free agent'}",
        f"- Age {player.get('age') or 'unknown'}, {experience}, {role}",
    ]
    if injury_status:
        lines.append(f"- Injury designation: {injury_status}")
    if search_rank and search_rank < 9999999:
        lines.append(f"- Sleeper consensus rank: {search_rank} overall")
    if context.get("pos_rank_available"):
        lines.append(f"- {_ordinal(context['pos_rank_available'])}-ranked {position} still available")
    if context.get("next_same_position") and search_rank and search_rank < 9999999:
        nxt = context["next_same_position"]
        gap = nxt["rank"] - search_rank
        if gap >= 20:
            drop = "steep drop-off at the position after him"
        elif gap >= 8:
            drop = "noticeable drop-off at the position after him"
        else:
            drop = "no real drop-off; similar options remain at the position"
        lines.append(f"- Next-best {position} available: {nxt['name']} (consensus rank {nxt['rank']}): {drop}")

    production = [_trend("Yards", player.get("yards_last"), player.get("yards_prev"))]
    if position != "QB":
        production.append(_trend("Targets", player.get("targets_last"), player.get("targets_prev")))
    production.append(_trend("Snaps", player.get("snaps_last"), player.get("snaps_prev")))
    production = [p for p in production if p]
    if production:
        lines.append("PRODUCTION:")
        lines += [f"- {p}" for p in production]

    lines.append("DRAFT SITUATION:")
    total_rounds = context.get("total_rounds")
    lines.append(f"- Round {round_number}" + (f" of {total_rounds}" if total_rounds else ""))
    if context.get("rec_rank"):
        lines.append(f"- Recommendation #{context['rec_rank']} of {context.get('rec_total', 10)} for this pick")
    if context.get("projected_slot"):
        lines.append(f"- Would fill: {context['projected_slot']}")
    if context.get("alternatives"):
        alts = ", ".join(f"{a['name']} ({a['position']}, #{a['rec_rank']})" for a in context["alternatives"])
        lines.append(f"- Best recommended option at other positions: {alts}")

    lines.append("MANAGER'S ROSTER:")
    if context.get("roster_summary"):
        lines += [f"- {row}" for row in context["roster_summary"]]
    elif roster:
        lines.append("- " + ", ".join(f"{p.get('full_name', '?')} ({p.get('position')})" for p in roster))
    else:
        lines.append("- Empty (first pick)")

    return "\n".join(lines)


def _request_explanation(prompt):
    client = _get_client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        max_tokens=120,
        temperature=0.6,
    )
    return response.choices[0].message.content.strip()
