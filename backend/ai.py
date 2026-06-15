import os
from openai import OpenAI

def explain_pick(player, roster, round_number):
    client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
    roster_positions = [p.get("position") for p in roster]

    prompt = f"""

Player: {player['full_name']} | {player['position']} | {player['team']} | Age: {player['age']}

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
            "Here is what each score means:"
            "base_score (0-10): how highly the fantasy community ranks this player overall. ""Higher = stronger consensus pick. "
            "potential_score (0-10): " "based on the player's age relative to their position's peak age. " "Higher = more upside. "
            "sleeper_score (0-10): how undervalued this player is relative to their potential. " "Higher = more of a hidden gem. "
            "need_score (0-20): how much the user's current roster needs this position. " "Higher = bigger gap to fill. overall_score: the combined weighted score across all factors. "
            "You will also receive the user's current roster positions. Use this to highlight how this player addresses a specific need. Write 2-3 natural, confident sentences explaining why this player is a good pick. Lead with the strongest factors driving their score. Sound like an experienced fantasy analyst, not a spreadsheet. Don't just list the numbers — use them to tell a story about the pick. Be concise and act as a manager."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200,
    )
    return response.choices[0].message.content
