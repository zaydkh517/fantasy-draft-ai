from flask import Flask
from flask_cors import CORS
from data import get_all_players, get_fantasy_players, get_trending_players
from database import init_db, save_players, get_players_from_db, mark_player_drafted, get_drafted_players, reset_draft

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

if __name__ == '__main__':
    app.run(debug=True)