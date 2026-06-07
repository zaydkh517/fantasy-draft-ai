# Peak ages by position
from turtle import position


PEAK_AGE = {
    "QB": 29,
    "RB": 25,
    "WR": 27,
    "TE": 27
}

# Positional scarcity weights
POSITION_SCARCITY = {
    "QB": 0.8,
    "RB": 1.0,
    "WR": 1.0,
    "TE": 0.9
}

# Round-based scoring weights
ROUND_WEIGHTS = {
    "early":  {"base": 0.60, "upside": 0.30, "need": 0.10},  # rounds 1-3
    "middle": {"base": 0.45, "upside": 0.25, "need": 0.30},  # rounds 4-8
    "late":   {"base": 0.45, "upside": 0.35, "need": 0.20},  # rounds 9-12
    "very_late": {"base": 0.45, "upside": 0.50, "need": 0.05}  # rounds 13+
}

# FLEX position weights
FLEX_WEIGHTS = {
    "RB": 0.35,
    "WR": 0.35,
    "TE": 0.30
}

# Draft round value mapping
ROUND_VALUE = {
    1: 10,
    2: 8,
    3: 6,
    4: 4
}

def get_round_weights(round_number):
    if round_number <= 3:
        return ROUND_WEIGHTS["early"]
    elif round_number <= 8:
        return ROUND_WEIGHTS["middle"]
    elif round_number <= 12:
        return ROUND_WEIGHTS["late"]
    else:
        return ROUND_WEIGHTS["very_late"]
    
def calculate_draft_capital_score(player):
    round_number = player.get("draft_round")
    years_exp = player.get("years_exp") or 0
    if round_number is None:
        return 0.0
     
    round_score = ROUND_VALUE.get(round_number,2)

    if(years_exp<=1):
        return round_score
    elif(years_exp==2):
        return round_score * 0.5
    else:
        return 0.0

    
def calculate_potential_score(player):
    age = player.get("age")
    position = player.get("position")
    years_exp = player.get("years_exp") or 0

    if age is None or position is None:
        return 5.0
    
    peak = PEAK_AGE.get(position,27)

    if age<peak:
        age_score = 10.0 - ((peak - age) * 0.5)
    elif age == peak:
        age_score = 10.0
    else:
        age_score = 10 - ((age - peak) * 1.2)
    age_score = max(1.0, min(age_score, 10.0))

    draft_capital = calculate_draft_capital_score(player)

    if draft_capital > 0:
        potential = (age_score * 0.7) + (draft_capital * 0.3)
    else:
        potential = age_score

    return round(potential, 2)

def calculate_sleeper_score(player, fantasy_players):

    potential = calculate_potential_score(player)
    position = player.get("position")
    player_rank = player.get("search_rank", 9999999)
    injury_status = player.get("injury_status")

    if(player_rank == 9999999):
        return 0.0
    
    same_position_players = []

    for p in fantasy_players:
        if p.get("position") == position:
            same_position_players.append(p)

    same_position_players.sort(key=lambda x: x.get("search_rank", 9999999))

    position_ranks = [p.get("search_rank", 9999999) for p in same_position_players]
    rank_index = position_ranks.index(player_rank) if player_rank in position_ranks else len(position_ranks)
    percentile = rank_index / len(same_position_players)

    if injury_status is not None:
        injury_penalty = 0.7
    else:
        injury_penalty = 1.0

    return round(potential * (percentile) * injury_penalty, 2)

