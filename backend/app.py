import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
from flask import Flask, request, jsonify
from flask_cors import CORS
from data import get_all_players, get_fantasy_players, get_trending_players
from database import init_db, save_players, get_players_from_db, mark_player_drafted, get_drafted_players, reset_draft, save_league_settings, get_league_settings
from ai import explain_pick

app = Flask(__name__)
CORS(app)

init_db()

@app.route('/')
def home():
    return {"status": "Draft Assistant API is running"}

@app.route('/sync-players')
def sync_players():
    players = get_fantasy_players()
    save_players(players)
    return {"message": f"Synced {len(players)} players to database"}

@app.route('/players')
def players():
    players = get_players_from_db()
    return {"count": len(players), "sample": players[:5]}

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

@app.route('/recommend', methods=['POST'])
def recommend():
    from logic import rank_players
    
    data = request.json
    roster = data.get('roster', [])
    round_number = data.get('round_number', 1)
    drafted_ids = data.get('drafted_ids', [])
    
    all_players = get_players_from_db()
    league_settings = get_league_settings()
    
    available = [p for p in all_players if p["player_id"] not in drafted_ids]
    
    ranked = rank_players(available, all_players, roster, round_number, league_settings)

    for player in ranked[:10]:
        player["explanation"] = explain_pick(player, roster, round_number)
    
    return jsonify({"recommendations": ranked[:10]})

if __name__ == '__main__':
    app.run(debug=True)