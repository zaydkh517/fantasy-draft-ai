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

def get_trending_players():
    url = "https://api.sleeper.app/v1/players/nfl/trending/add"
    response = requests.get(url)
    trending = response.json()
    return trending

