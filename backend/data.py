import requests

FANTASY_POSITIONS = ["QB", "RB", "WR", "TE"]

def get_all_players():
    url = "https://api.sleeper.app/v1/players/nfl"
    response = requests.get(url)
    players = response.json()
    return players

def get_fantasy_players():
    all_players = get_all_players()
    fantasy_players = []

    for player_id, player in all_players.items():
        position = player.get("position")
        status = player.get("status")

        if position in FANTASY_POSITIONS and status == "Active":
            fantasy_players.append({
                "player_id": player_id,
                "full_name": player.get("full_name"),
                "position": position,
                "team": player.get("team"),
                "age": player.get("age"),
                "years_exp": player.get("years_exp"),
                "injury_status": player.get("injury_status"),
                "depth_chart_order": player.get("depth_chart_order"),
                "search_rank": player.get("search_rank"),
            })

    return fantasy_players

def get_bulk_stats(season):
    url = f"https://api.sleeper.app/v1/stats/nfl/{season}?season_type=regular&grouping=season"
    response = requests.get(url)
    if response.status_code != 200:
        return {}
    return response.json()

def get_player_stats():
    stats_2025 = get_bulk_stats(2025)
    stats_2024 = get_bulk_stats(2024)

    player_stats = {}

    all_player_ids = set(stats_2025.keys()) | set(stats_2024.keys())

    for player_id in all_player_ids:
        s2025 = stats_2025.get(player_id, {})
        s2024 = stats_2024.get(player_id, {})

        def get_yards(s):
            return (s.get("pass_yd") or 0) + (s.get("rush_yd") or 0) + (s.get("rec_yd") or 0)

        def get_targets(s):
            return s.get("rec_tgt") or 0

        def get_snaps(s):
            return s.get("off_snp") or 0

        player_stats[player_id] = {
            "yards_2025": get_yards(s2025),
            "yards_2024": get_yards(s2024),
            "targets_2025": get_targets(s2025),
            "targets_2024": get_targets(s2024),
            "snaps_2025": get_snaps(s2025),
            "snaps_2024": get_snaps(s2024),
        }

    return player_stats

def get_trending_players():
    url = "https://api.sleeper.app/v1/players/nfl/trending/add"
    response = requests.get(url)
    trending = response.json()
    return trending