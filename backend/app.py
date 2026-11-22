from concurrent.futures import ThreadPoolExecutor
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
from flask import Flask, request, jsonify
from flask_cors import CORS
from data import get_fantasy_players, get_trending_players, get_player_stats
from database import init_db, save_players, get_players_from_db, mark_player_drafted, get_drafted_players, reset_draft, save_league_settings, get_league_settings
from ai import explain_pick
import threading
import time

_trending_cache = {"data": [], "at": 0.0}
TRENDING_TTL = 900  # Sleeper trending data changes slowly; refresh every 15 min

def get_trending_cached():
    if time.time() - _trending_cache["at"] > TRENDING_TTL:
        try:
            _trending_cache["data"] = get_trending_players()
        except Exception as e:
            print(f"Trending fetch failed: {e}")
        _trending_cache["at"] = time.time()
    return _trending_cache["data"]

app = Flask(__name__)
CORS(app)

init_db()

_sync_lock = threading.Lock()

def sync_players_to_db():
    """Pull players and season stats from Sleeper into SQLite. Returns player count."""
    with _sync_lock:
        players = get_fantasy_players()
        stats = get_player_stats()
        for player in players:
            player_stats = stats.get(player["player_id"], {})
            for key in ("yards_2025", "yards_2024", "targets_2025", "targets_2024", "snaps_2025", "snaps_2024"):
                player[key] = player_stats.get(key, 0)
        save_players(players)
        return len(players)

def startup_sync():
    try:
        sync_players_to_db()
    except Exception as e:
        print(f"Startup sync failed: {e}")

threading.Thread(target=startup_sync, daemon=True).start()

def load_players():
    """Players from the DB; if the DB is empty (fresh image), sync before answering."""
    players = get_players_from_db()
    if not players:
        with _sync_lock:  # waits for an in-flight startup sync to finish
            players = get_players_from_db()
        if not players:
            sync_players_to_db()
            players = get_players_from_db()
    return players

SETTINGS_KEYS = ("league_size", "roster_size", "qb_starters", "rb_starters", "wr_starters",
                 "te_starters", "flex_starters", "bench_slots")

def resolve_settings(requested):
    """League settings come with each request so concurrent users and multiple
    machines never share state. Falls back to stored defaults for old clients."""
    settings = get_league_settings()
    if isinstance(requested, dict):
        for key in SETTINGS_KEYS:
            try:
                if requested.get(key) is not None:
                    settings[key] = max(0, int(requested[key]))
            except (TypeError, ValueError):
                pass
    settings["league_size"] = max(2, settings["league_size"])
    return settings

def get_ranked_players(roster, round_number, drafted_ids, league_settings):
    from logic import rank_players

    all_players = load_players()
    drafted = set(drafted_ids)
    available = [p for p in all_players if p["player_id"] not in drafted]

    raw_trending = get_trending_cached()
    max_count = max((t.get("count", 1) for t in raw_trending), default=1)
    trending_scores = {
        t["player_id"]: min(10.0, (t.get("count", 0) / max_count) * 10)
        for t in raw_trending
    }

    return rank_players(available, all_players, roster, round_number, league_settings, trending_scores)

@app.route('/')
def home():
    return {"status": "Draft Assistant API is running"}

@app.route('/sync-players')
def sync_players():
    count = sync_players_to_db()
    return {"message": f"Synced {count} players to database"}

@app.route('/players')
def players():
    players = load_players()
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

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    roster = data.get('roster', [])
    round_number = data.get('round_number', 1)
    drafted_ids = data.get('drafted_ids', [])
    generate_explanations = data.get('generate_explanations', True)
    settings = resolve_settings(data.get('league_settings'))

    ranked = get_ranked_players(roster, round_number, drafted_ids, settings)

    if generate_explanations:
        contexts = build_explanation_contexts(ranked, roster, settings)

        def add_explanation(item):
            player, context = item
            try:
                player["explanation"] = explain_pick(player, roster, round_number, context)
            except Exception as e:  # one failed explanation shouldn't sink the whole list
                print(f"Explanation failed for {player.get('full_name')}: {e}")
                player["explanation"] = None
            return player
        with ThreadPoolExecutor(max_workers=10) as executor:
            ranked[:10] = list(executor.map(add_explanation, zip(ranked[:10], contexts)))
    else:
        for player in ranked[:10]:
            player["explanation"] = None

    return jsonify({"recommendations": ranked[:10]})

SLOT_LABELS = {"QB": "QB", "RB": "RB", "WR": "WR", "TE": "TE", "FLEX": "FLEX", "BENCH": "Bench"}

def projected_slot(position, roster, settings):
    """Mirror of the frontend's assignSlot: where this player would land on the roster."""
    counts = {}
    for p in roster:
        counts[p.get("slot")] = counts.get(p.get("slot"), 0) + 1
    starters = settings.get(f"{position.lower()}_starters", 0) if position else 0
    if counts.get(position, 0) < starters:
        return f"an open starting {position} spot"
    if position != "QB" and counts.get("FLEX", 0) < settings.get("flex_starters", 0):
        return "the open FLEX spot"
    if counts.get("BENCH", 0) < settings.get("bench_slots", 0):
        return "a bench spot (starting lineup at his position is already full)"
    return "no open roster spot"

def summarize_roster(roster, settings):
    rows = []
    for slot in ["QB", "RB", "WR", "TE", "FLEX", "BENCH"]:
        total = settings.get("bench_slots" if slot == "BENCH" else f"{slot.lower()}_starters", 0)
        if not total:
            continue
        names = []
        for p in roster:
            if p.get("slot") != slot:
                continue
            name = p.get("full_name") or f"unnamed {p.get('position') or 'player'}"
            names.append(f"{name} ({p.get('position')})" if slot in ("FLEX", "BENCH") else name)
        filled = ", ".join(names) if names else "none"
        rows.append(f"{SLOT_LABELS[slot]} {len(names)}/{total}: {filled}")
    return rows

def build_explanation_contexts(ranked, roster, settings, top_n=10):
    # Available players at each position, best consensus rank first
    by_position = {}
    for p in ranked:
        rank = p.get("search_rank") or 9999999
        if rank < 9999999:
            by_position.setdefault(p.get("position"), []).append(p)
    for players in by_position.values():
        players.sort(key=lambda p: p["search_rank"])

    roster_summary = summarize_roster(roster, settings)
    total_rounds = settings.get("roster_size")
    top = ranked[:top_n]
    # Highest recommendation at each position, so each note can frame the tradeoff
    best_by_position = {}
    for i, p in enumerate(top):
        best_by_position.setdefault(p.get("position"), (i + 1, p))
    contexts = []
    for i, player in enumerate(top):
        alternatives = [
            {"name": p["full_name"], "position": pos, "rec_rank": r}
            for pos, (r, p) in best_by_position.items()
            if pos != player.get("position")
        ]
        same_pos = by_position.get(player.get("position"), [])
        ids = [p["player_id"] for p in same_pos]
        idx = ids.index(player["player_id"]) if player["player_id"] in ids else None
        nxt = same_pos[idx + 1] if idx is not None and idx + 1 < len(same_pos) else None
        contexts.append({
            "rec_rank": i + 1,
            "rec_total": len(top),
            "total_rounds": total_rounds,
            "pos_rank_available": idx + 1 if idx is not None else None,
            "next_same_position": {"name": nxt["full_name"], "rank": nxt["search_rank"]} if nxt else None,
            "projected_slot": projected_slot(player.get("position"), roster, settings),
            "roster_summary": roster_summary,
            "alternatives": alternatives,
        })
    return contexts

@app.route('/rank-all', methods=['POST'])
def rank_all():
    data = request.json
    roster = data.get('roster', [])
    round_number = data.get('round_number', 1)
    drafted_ids = data.get('drafted_ids', [])
    settings = resolve_settings(data.get('league_settings'))

    ranked = get_ranked_players(roster, round_number, drafted_ids, settings)
    
    return jsonify({"players": ranked})

@app.route('/autodraft', methods=['POST'])
def autodraft():
    data = request.json
    roster = data.get('roster', [])
    round_number = data.get('round_number', 1)
    drafted_ids = data.get('drafted_ids', [])
    settings = resolve_settings(data.get('league_settings'))

    ranked = get_ranked_players(roster, round_number, drafted_ids, settings)
    
    if not ranked:
        return jsonify({"pick": None})
    
    return jsonify({"pick": ranked[0]})

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))