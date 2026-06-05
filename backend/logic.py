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

    if age is None or position is None:
        return 5.0
    
    peak = PEAK_AGE.get(position,27)