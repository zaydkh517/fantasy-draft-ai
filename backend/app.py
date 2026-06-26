from concurrent.futures import ThreadPoolExecutor
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
from flask import Flask, request, jsonify
from flask_cors import CORS
from data import get_all_players, get_fantasy_players, get_trending_players, get_player_stats
from database import init_db, save_players, get_players_from_db, mark_player_drafted, get_drafted_players, reset_draft, save_league_settings, get_league_settings
from ai import explain_pick
import threading

app = Flask(__name__)
CORS(app)

init_db()

def startup_sync():
    from data import get_fantasy_players, get_player_stats
    players = get_fantasy_players()
    stats = get_player_stats()
    for player in players:
        player_id = player["player_id"]
        player_stats = stats.get(player_id, {})
        player["yards_2025"] = player_stats.get("yards_2025", 0)
        player["yards_2024"] = player_stats.get("yards_2024", 0)
        player["targets_2025"] = player_stats.get("targets_2025", 0)
        player["targets_2024"] = player_stats.get("targets_2024", 0)
        player["snaps_2025"] = player_stats.get("snaps_2025", 0)
        player["snaps_2024"] = player_stats.get("snaps_2024", 0)
    save_players(players)


threading.Thread(target=startup_sync, daemon=True).start()

@app.route('/')
def home():
    return {"status": "Draft Assistant API is running"}

@app.route('/sync-players')
def sync_players():
    players = get_fantasy_players()
    stats = get_player_stats()
    
    for player in players:
        player_id = player["player_id"]
        player_stats = stats.get(player_id, {})
        player["yards_2025"] = player_stats.get("yards_2025", 0)
        player["yards_2024"] = player_stats.get("yards_2024", 0)
        player["targets_2025"] = player_stats.get("targets_2025", 0)
        player["targets_2024"] = player_stats.get("targets_2024", 0)
        player["snaps_2025"] = player_stats.get("snaps_2025", 0)
        player["snaps_2024"] = player_stats.get("snaps_2024", 0)
    
    save_players(players)
    return {"message": f"Synced {len(players)} players to database"}

@app.route('/players')
def players():
    players = get_players_from_db()
    return jsonify({"count": len(players), "players": players})

@app.route('/draft', methods=['POST'])
def draft_player():
    data = request.json
    player_id = data.get('player_id')
    mark_player_drafted(player_id)
    return {"message": f"Player {player_id} marked as drafted"}

@app.route('/drafted')
def drafted():
    drafted = get_drafted_players()
    return {"drafted": drafted}

@app.route('/reset', methods=['POST'])
def reset():
    reset_draft()
    return {"message": "Draft reset successfully"}

@app.route('/settings', methods=['POST'])
def save_settings():
    data = request.json
    save_league_settings(data)
    return {"message": "League settings saved"}

@app.route('/settings', methods=['GET'])
def get_settings():
    settings = get_league_settings()
    return settings

@app.route('/rank-all', methods=['POST'])
def rank_all():
    from logic import rank_players
    
    data = request.json
    roster = data.get('roster', [])
    round_number = data.get('round_number', 1)
    drafted_ids = data.get('drafted_ids', [])
    
    all_players = get_players_from_db()
    league_settings = get_league_settings()
    
    available = [p for p in all_players if p["player_id"] not in drafted_ids]
    
    raw_trending = get_trending_players()
    max_count = max((t.get("count", 1) for t in raw_trending), default=1)
    trending_scores = {
        t["player_id"]: min(10.0, (t.get("count", 0) / max_count) * 10)
        for t in raw_trending
    }
    
    ranked = rank_players(available, all_players, roster, round_number, league_settings, trending_scores)
    
    return jsonify({"players": ranked})

@app.route('/recommend', methods=['POST'])
def recommend():
    from logic import rank_players
    from concurrent.futures import ThreadPoolExecutor
    
    data = request.json
    roster = data.get('roster', [])
    round_number = data.get('round_number', 1)
    drafted_ids = data.get('drafted_ids', [])
    
    all_players = get_players_from_db()
    league_settings = get_league_settings()
    
    available = [p for p in all_players if p["player_id"] not in drafted_ids]
    print("available count:", len(available))

    available = [p for p in all_players if p["player_id"] not in drafted_ids]
    
    raw_trending = get_trending_players()
    max_count = max((t.get("count", 1) for t in raw_trending), default=1)
    trending_scores = {
        t["player_id"]: min(10.0, (t.get("count", 0) / max_count) * 10)
        for t in raw_trending
    }

    ranked = rank_players(available, all_players, roster, round_number, league_settings, trending_scores)

    generate_explanations = data.get('generate_explanations', True)

    
    if generate_explanations:
        def add_explanation(player):
            player["explanation"] = explain_pick(player, roster, round_number)
            return player
        with ThreadPoolExecutor(max_workers=10) as executor:
            ranked[:10] = list(executor.map(add_explanation, ranked[:10]))
    else:
        for player in ranked[:10]:
            player["explanation"] = None
    
    return jsonify({"recommendations": ranked[:10]})

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
