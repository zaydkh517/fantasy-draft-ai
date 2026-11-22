import sqlite3
import json
import os
import time
import threading

_players_cache = {"data": None, "at": 0.0}
_players_lock = threading.Lock()
PLAYERS_CACHE_TTL = 300  # seconds

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "draft.db")

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Draft and league settings now travel with each request; drop the old shared tables
    cursor.execute('DROP TABLE IF EXISTS drafted_players')
    cursor.execute('DROP TABLE IF EXISTS league_settings')

    # Older databases stored stats under year-named columns; players are re-synced
    # from Sleeper on startup, so rebuilding the table loses nothing
    columns = {row[1] for row in cursor.execute('PRAGMA table_info(players)')}
    if columns and "yards_last" not in columns:
        cursor.execute('DROP TABLE players')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            player_id TEXT PRIMARY KEY,
            full_name TEXT,
            position TEXT,
            team TEXT,
            age INTEGER,
            years_exp INTEGER,
            injury_status TEXT,
            depth_chart_order INTEGER,
            search_rank INTEGER,
            yards_last INTEGER,
            yards_prev INTEGER,
            targets_last INTEGER,
            targets_prev INTEGER,
            snaps_last INTEGER,
            snaps_prev INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()

def save_players(players):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    for player in players:
        cursor.execute('''
            INSERT OR REPLACE INTO players 
            (player_id, full_name, position, team, age, years_exp, injury_status, depth_chart_order, search_rank,
            yards_last, yards_prev, targets_last, targets_prev, snaps_last, snaps_prev)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            player["player_id"],
            player["full_name"],
            player["position"],
            player["team"],
            player["age"],
            player["years_exp"],
            player["injury_status"],
            player["depth_chart_order"],
            player["search_rank"],
            player.get("yards_last", 0),
            player.get("yards_prev", 0),
            player.get("targets_last", 0),
            player.get("targets_prev", 0),
            player.get("snaps_last", 0),
            player.get("snaps_prev", 0)
        ))
    
    conn.commit()
    conn.close()
    with _players_lock:
        _players_cache["data"] = None

def get_players_from_db():
    """Cached read of the players table. Returns copies so callers can mutate."""
    now = time.time()
    with _players_lock:
        cached = _players_cache["data"]
        if cached is None or now - _players_cache["at"] > PLAYERS_CACHE_TTL:
            cached = _load_players_from_db()
            _players_cache["data"] = cached
            _players_cache["at"] = now
    return [dict(p) for p in cached]

def _load_players_from_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM players')
    rows = cursor.fetchall()
    conn.close()
    
    players = []
    for row in rows:
        players.append({
            "player_id": row[0],
            "full_name": row[1],
            "position": row[2],
            "team": row[3],
            "age": row[4],
            "years_exp": row[5],
            "injury_status": row[6],
            "depth_chart_order": row[7],
            "search_rank": row[8],
            "yards_last": row[9],
            "yards_prev": row[10],
            "targets_last": row[11],
            "targets_prev": row[12],
            "snaps_last": row[13],
            "snaps_prev": row[14]
        })
    
    return players
