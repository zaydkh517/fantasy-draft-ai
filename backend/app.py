from flask import Flask
from flask_cors import CORS
from data import get_all_players, get_fantasy_players, get_trending_players

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return {"status": "Draft Assistant API is running"}

@app.route('/players')
def players():
    data = get_all_players()
    return {"count": len(data), "sample": list(data.items())[:3]}

@app.route('/fantasy-players')
def fantasy_players():
    players = get_fantasy_players()
    return {"count": len(players), "sample": players[:5]}

@app.route('/debug')
def debug():
    all_players = get_all_players()
    results = []
    for player_id, player in all_players.items():
        position = player.get("position")
        status = player.get("status")
        if position in ["QB", "RB", "WR", "TE"]:
            results.append({
                "name": player.get("full_name"),
                "position": position,
                "status": status
            })
    return {"count": len(results), "sample": results[:5]}

if __name__ == '__main__':
    app.run(debug=True)