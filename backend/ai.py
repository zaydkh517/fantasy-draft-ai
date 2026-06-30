import os
from openai import OpenAI

def explain_pick(player, roster, round_number):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    roster_positions = [p.get("position") for p in roster]

    yards_2025 = player.get('yards_2025', 0)
    yards_2024 = player.get('yards_2024', 0)
    years_exp = player.get('years_exp', 0)
    depth = player.get('depth_chart_order', 2)
    injury_status = player.get('injury_status')

    depth_label = "starter" if depth == 1 else "backup" if depth == 2 else "depth player"
    exp_label = "rookie" if years_exp == 0 else f"year {years_exp + 1} player"
    injury_context = f"Currently {injury_status}." if injury_status else ""

    yards_context = ""
    if yards_2025 > 0 and yards_2024 > 0:
        direction = "up" if yards_2025 > yards_2024 else "down"
        yards_context = f"Yards trending {direction}: {yards_2024} in 2024 → {yards_2025} in 2025."
    elif yards_2025 > 0:
        yards_context = f"Put up {yards_2025} yards in 2025."
    elif yards_2024 > 0:
        yards_context = f"Put up {yards_2024} yards in 2024."

    prompt = f"""
Player: {player['full_name']} | {player['position']} | {player['team']} | Age: {player['age']} | {exp_label} | {depth_label}
{yards_context}
{injury_context}

Scores:
- base_score: {player['base_score']}
- potential_score: {player['potential_score']}
- sleeper_score: {player['sleeper_score']}
- need_score: {player['need_score']}
- overall_score: {player['overall_score']}

Current roster positions: {roster_positions}
Draft round: {round_number}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a fantasy football draft analyst. "
             "You will receive a player's data including 5 scores. "
             "Here is what each score means: "
             "base_score (0-10): how highly the fantasy community ranks this player overall. Higher = stronger consensus pick. "
             "potential_score (0-10): based on the player's age, years of experience, depth chart role, and yards trend. Higher = more upside. "
             "sleeper_score (0-10): how undervalued this player is relative to their potential. Higher = more of a hidden gem. "
             "need_score (0-20): how much the user's current roster needs this position. Higher = bigger gap to fill. "
             "overall_score: the combined weighted score across all factors. "
             "You will also receive the user's current roster positions. Use this to highlight how this player addresses a specific need. "
             "Write 2-3 natural, confident sentences explaining why this player is a good pick. "
             "Lead with the strongest factors driving their score. "
             "Sound like an experienced fantasy analyst, not a spreadsheet. "
             "Don't list the numbers — use them to tell a story about the pick. "
             "Be concise and act like a manager. "
             "Use natural language to explain the scores, but don't include the score itself, except for overall score. "
             "Reference yards trends and experience level where relevant. "
             "Do not be generic."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200,
    )
    return response.choices[0].message.content