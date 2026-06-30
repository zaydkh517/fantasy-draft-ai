POSITION_AVG_YARDS = {
    "QB": 4000,
    "RB": 1000,
    "WR": 900,
    "TE": 600
}

POSITION_AVG_TARGETS = {
    "RB": 50,
    "WR": 100,
    "TE": 70
}

POSITION_AVG_SNAPS = {
    "QB": 1000,
    "RB": 400,
    "WR": 600,
    "TE": 500
}

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
      
def calculate_potential_score(player):
    age = player.get("age")
    position = player.get("position")
    years_exp = player.get("years_exp") or 0
    depth = player.get("depth_chart_order") or 2
    yards_2025 = player.get("yards_2025") or 0
    yards_2024 = player.get("yards_2024") or 0
    targets_2025 = player.get("targets_2025") or 0
    targets_2024 = player.get("targets_2024") or 0
    snaps_2025 = player.get("snaps_2025") or 0
    snaps_2024 = player.get("snaps_2024") or 0
    search_rank = player.get("search_rank") or 9999999

    if age is None or position is None:
        return 5.0
    
    # Age score calculation
    peak = PEAK_AGE.get(position, 27)
    if age < peak:
        age_score = 10.0 - ((peak - age) * 0.5)
    elif age == peak:
        age_score = 10.0
    else:
        age_score = 10 - ((age - peak) * 1.35)
    age_score = max(1.0, min(age_score, 10.0))

    # Yards trend score
    if yards_2024 > 0 and yards_2025 > 0:
        yards_change = (yards_2025 - yards_2024) / yards_2024
        yards_trend = min(10.0, max(1.0, 5.5 + (yards_change * 10)))
    elif yards_2025 > 0:
        position_avg_yards = POSITION_AVG_YARDS.get(position, 800)
        yards_trend = min(10.0, max(1.0, (yards_2025 / position_avg_yards) * 7.0))
    elif yards_2024 > 0:
        position_avg_yards = POSITION_AVG_YARDS.get(position, 800)
        yards_trend = min(10.0, max(1.0, (yards_2024 / position_avg_yards) * 7.0))
    elif years_exp == 0:
        yards_trend = max(5.0, min(8.0, 10 - (search_rank * 0.03)))
    else:
        yards_trend = 5.0

    # Target trend score
    if position == "QB":
        targets_trend = 5.0
    elif targets_2024 > 0 and targets_2025 > 0:
        targets_change = (targets_2025 - targets_2024) / targets_2024
        targets_trend = min(10.0, max(1.0, 5.5 + (targets_change * 10)))
    elif targets_2025 > 0:
        position_avg_targets = POSITION_AVG_TARGETS.get(position, 70)
        targets_trend = min(10.0, max(1.0, (targets_2025 / position_avg_targets) * 7.0))
    elif targets_2024 > 0:
        position_avg_targets = POSITION_AVG_TARGETS.get(position, 70)
        targets_trend = min(10.0, max(1.0, (targets_2024 / position_avg_targets) * 7.0))
    elif years_exp == 0:
        targets_trend = max(5.0, min(8.0, 10 - (search_rank * 0.03)))
    else:
        targets_trend = 5.0

    # Snap trend score
    if snaps_2024 > 0 and snaps_2025 > 0:
        snaps_change = (snaps_2025 - snaps_2024) / snaps_2024
        snaps_trend = min(10.0, max(1.0, 5.5 + (snaps_change * 10)))
    elif snaps_2025 > 0:
        position_avg_snaps = POSITION_AVG_SNAPS.get(position, 500)
        snaps_trend = min(10.0, max(1.0, (snaps_2025 / position_avg_snaps) * 7.0))
    elif snaps_2024 > 0:
        position_avg_snaps = POSITION_AVG_SNAPS.get(position, 500)
        snaps_trend = min(10.0, max(1.0, (snaps_2024 / position_avg_snaps) * 7.0))
    elif years_exp == 0:
        snaps_trend = max(5.0, min(8.0, 10 - (search_rank * 0.03)))
    else:
        snaps_trend = 5.0

    # Experience score
    if years_exp == 0:
        exp_score = 7.0
    elif years_exp <= 4:
        exp_score = 9.0
    elif years_exp <= 7:
        exp_score = 7.0
    elif years_exp <= 10:
        exp_score = 5.0
    else:
        exp_score = 3.0

    # Depth score
    if depth == 1:
        depth_score = 10.0
    elif depth == 2:
        depth_score = 7.0
    elif depth == 3:
        depth_score = 4.5
    else:
        depth_score = 2.0

    depth_multiplier = 1.0 if depth == 1 else 0.7 if depth == 2 else 0.5
    yards_trend = yards_trend * depth_multiplier
    targets_trend = targets_trend * depth_multiplier
    snaps_trend = snaps_trend * depth_multiplier

    if position == "QB":
        return round(
            (age_score * 0.25) +
            (yards_trend * 0.45) +
            (snaps_trend * 0.15) +
            (exp_score * 0.10) +
            (depth_score * 0.05),
            2
        )
    
    return round(
        (age_score * 0.20) +
        (yards_trend * 0.30) +
        (targets_trend * 0.20) +
        (snaps_trend * 0.15) +
        (exp_score * 0.10) +
        (depth_score * 0.05),
        2
    )

def calculate_base_score(search_rank, draftable_pool):
    return max(1.0, 10 - ((search_rank - 1) / (draftable_pool - 1)) * 9)


def calculate_sleeper_score(player, fantasy_players, trending_scores = None):
    if trending_scores is None:
        trending_scores = {}

    potential = calculate_potential_score(player)
    position = player.get("position")
    player_rank = player.get("search_rank", 9999999)
    injury_status = player.get("injury_status")
    player_id = player.get("player_id")


    if(player_rank == 9999999):
        return 0.0
    
    same_position_players = []

    for p in fantasy_players:
        if p.get("position") == position:
            same_position_players.append(p)

    same_position_players.sort(key=lambda x: x.get("search_rank") or 9999999)

    position_ranks = [p.get("search_rank") or 9999999 for p in same_position_players]
    rank_index = position_ranks.index(player_rank) if player_rank in position_ranks else len(position_ranks)
    percentile = rank_index / len(same_position_players)

    if injury_status is not None:
        injury_penalty = 0.7
    else:
        injury_penalty = 1.0

    #makes sleeper score more useful and helps filter out the very low ranked players
    base_sleeper = potential * percentile * injury_penalty
    base_sleeper =  min(10,base_sleeper*10)

    trend_score = trending_scores.get(player_id, 0.0)

    return round((base_sleeper * 0.80) + (trend_score * 0.20), 2)



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

def rank_players(available_players, fantasy_players, roster, round_number, league_settings, trending_scores=None):
    ranked = []
    weights = get_round_weights(round_number)
    player_count = len(available_players)

    league_size = league_settings.get("league_size", 12)
    roster_size = league_settings.get("roster_size", 16)
    draftable_pool = min((league_size * roster_size) + 40, player_count)

    for player in available_players:
        position = player.get("position")
        search_rank = player.get("search_rank") or 9999999

        base_score = calculate_base_score(search_rank, draftable_pool)

        potential = calculate_potential_score(player)
        sleeper = calculate_sleeper_score(player, fantasy_players, trending_scores)
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