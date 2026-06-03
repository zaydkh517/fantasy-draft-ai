import requests

def get_all_players():
    url = "https://api.sleeper.app/v1/players/nfl"
    response = requests.get(url)
    players = response.json()
    return players

def get_trending_players():
    url = "https://api.sleeper.app/v1/players/nfl/trending/add"
    response = requests.get(url)
    trending = response.json()
    return trending