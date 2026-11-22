from datetime import date
import requests

FANTASY_POSITIONS = ["QB", "RB", "WR", "TE"]

# "last" = most recent completed regular season, "prev" = the one before it
STAT_KEYS = ("yards_last", "yards_prev", "targets_last", "targets_prev", "snaps_last", "snaps_prev")

def stat_seasons(today=None):
    """(last, prev) completed NFL regular seasons. The regular season ends in
    early January, so from February on the previous calendar year is complete."""
    today = today or date.today()
    last = today.year - 1 if today.month >= 2 else today.year - 2
    return last, last - 1

def get_all_players():
    url = "https://api.sleeper.app/v1/players/nfl"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    players = response.json()
    return players

def get_fantasy_players():
    all_players = get_all_players()
    fantasy_players = []

    for player_id, player in all_players.items():
        position = player.get("position")
        status = player.get("status")

        if position in FANTASY_POSITIONS and status == "Active" and player.get("team"):
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
    url = f"https://api.sleeper.app/v1/stats/nfl/regular/{season}"
    response = requests.get(url, timeout=30)
    if response.status_code != 200:
        return {}
    return response.json()

def get_player_stats():
    last_season, prev_season = stat_seasons()
    stats_last = get_bulk_stats(last_season)
    stats_prev = get_bulk_stats(prev_season)

    def get_yards(s):
        return (s.get("pass_yd") or 0) + (s.get("rush_yd") or 0) + (s.get("rec_yd") or 0)

    def get_targets(s):
        return s.get("rec_tgt") or 0

    def get_snaps(s):
        return s.get("off_snp") or 0

    player_stats = {}
    for player_id in set(stats_last) | set(stats_prev):
        s_last = stats_last.get(player_id, {})
        s_prev = stats_prev.get(player_id, {})
        player_stats[player_id] = {
            "yards_last": get_yards(s_last),
            "yards_prev": get_yards(s_prev),
            "targets_last": get_targets(s_last),
            "targets_prev": get_targets(s_prev),
            "snaps_last": get_snaps(s_last),
            "snaps_prev": get_snaps(s_prev),
        }

    return player_stats

def get_trending_players():
    url = "https://api.sleeper.app/v1/players/nfl/trending/add"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    trending = response.json()
    return trending