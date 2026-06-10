# Peak ages by position
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
    "early":     {"base": 0.70, "upside": 0.20, "need": 0.10, "sleeper_mix": 0.05},  # rounds 1-3
    "middle":    {"base": 0.45, "upside": 0.25, "need": 0.30, "sleeper_mix": 0.25},  # rounds 4-8
    "late":      {"base": 0.45, "upside": 0.35, "need": 0.20, "sleeper_mix": 0.45},  # rounds 9-12
    "very_late": {"base": 0.45, "upside": 0.50, "need": 0.05, "sleeper_mix": 0.60}   # rounds 13+
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

position_to_key = {
    "QB": "qb_starters",   # key: "QB", value: "qb_starters"
    "RB": "rb_starters",   # key: "RB", value: "rb_starters"
    "WR": "wr_starters",   # key: "WR", value: "wr_starters"
    "TE": "te_starters"    # key: "TE", value: "te_starters"
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


def calculate_base_score(search_rank, player_count, round_number):
    if round_number <= 3:
        # early rounds should favor top consensus ranks more strongly
        return max(1.0, 10 - (search_rank - 1) * 0.25)

    return max(1.0, 10 - ((search_rank - 1) / (player_count - 1)) * 9)


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

    same_position_players.sort(key=lambda x: x.get("search_rank") or 9999999)

    position_ranks = [p.get("search_rank", 9999999) for p in same_position_players]
    rank_index = position_ranks.index(player_rank) if player_rank in position_ranks else len(position_ranks)
    percentile = rank_index / len(same_position_players)

    if injury_status is not None:
        injury_penalty = 0.7
    else:
        injury_penalty = 1.0

    return round(potential * (percentile) * injury_penalty, 2)

def calculate_roster_needs(position, roster, league_settings):
    count = 0
    for player in roster:
        if player.get("position") == position:
            count += 1

    settings_key = position_to_key.get(position,"")
    required = league_settings.get(settings_key, 0)

    flex_slots = league_settings.get("flex_starters", 1)
    flex_bonus = FLEX_WEIGHTS.get(position, 0) * flex_slots * 0.1

    if count==0:
        return 1.5 + flex_bonus
    elif count < required:
        return 1.0 + ((required - count) * 0.4) + flex_bonus
    else: 
        return 0.5 + flex_bonus

def rank_players(available_players, fantasy_players, roster, round_number, league_settings):
    ranked = []
    weights = get_round_weights(round_number)
    player_count = len(available_players)

    for player in available_players:
        position = player.get("position")
        search_rank = player.get("search_rank") or 9999999

        base_score = calculate_base_score(search_rank, player_count, round_number)

        potential = calculate_potential_score(player)
        sleeper = calculate_sleeper_score(player, fantasy_players)
        sleeper_mix = weights["sleeper_mix"]
        upside_score = (potential * (1 - sleeper_mix)) + (sleeper * sleeper_mix)

        need = calculate_roster_needs(position, roster, league_settings)
        scarcity = POSITION_SCARCITY.get(position, 0.8)
        need_score = need * scarcity * 10

        overall_score = (
            (base_score * weights["base"]) +
            (upside_score * weights["upside"]) +
            (need_score * weights["need"])
        )

        ranked.append({
            **player,
            "base_score": round(base_score, 2),
            "potential_score": potential,
            "sleeper_score": sleeper,
            "need_score": round(need_score, 2),
            "overall_score": round(overall_score, 2)
        })

    ranked.sort(key=lambda x: x["overall_score"], reverse=True)
    return ranked