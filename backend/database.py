import sqlite3
import json
import os

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "draft.db")

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
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
            yards_2025 INTEGER,
            yards_2024 INTEGER,
            targets_2025 INTEGER,
            targets_2024 INTEGER,
            snaps_2025 INTEGER,
            snaps_2024 INTEGER
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS drafted_players (
            player_id TEXT PRIMARY KEY,
            drafted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS league_settings (
            id INTEGER PRIMARY KEY,
            league_size INTEGER,
            roster_size INTEGER,
            qb_starters INTEGER,
            rb_starters INTEGER,
            wr_starters INTEGER,
            te_starters INTEGER,
            flex_starters INTEGER,
            bench_slots INTEGER
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
            yards_2025, yards_2024, targets_2025, targets_2024, snaps_2025, snaps_2024)
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
            player.get("yards_2025", 0),
            player.get("yards_2024", 0),
            player.get("targets_2025", 0),
            player.get("targets_2024", 0),
            player.get("snaps_2025", 0),
            player.get("snaps_2024", 0)
        ))
    
    conn.commit()
    conn.close()

def get_players_from_db():
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
            "yards_2025": row[9],
            "yards_2024": row[10],
            "targets_2025": row[11],
            "targets_2024": row[12],
            "snaps_2025": row[13],
            "snaps_2024": row[14]
        })
    
    return players

def mark_player_drafted(player_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO drafted_players (player_id) VALUES (?)', (player_id,))
    conn.commit()
    conn.close()

def get_drafted_players():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT player_id FROM drafted_players')
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def reset_draft():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM drafted_players')
    conn.commit()
    conn.close()

def save_league_settings(settings):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS league_settings (
            id INTEGER PRIMARY KEY,
            league_size INTEGER,
            roster_size INTEGER,
            qb_starters INTEGER,
            rb_starters INTEGER,
            wr_starters INTEGER,
            te_starters INTEGER,
            flex_starters INTEGER,
            bench_slots INTEGER
        )
    ''')
    
    cursor.execute('DELETE FROM league_settings')
    
    cursor.execute('''
        INSERT INTO league_settings 
        (league_size, roster_size, qb_starters, rb_starters, wr_starters, te_starters, flex_starters, bench_slots)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        settings["league_size"],
        settings["roster_size"],
        settings["qb_starters"],
        settings["rb_starters"],
        settings["wr_starters"],
        settings["te_starters"],
        settings["flex_starters"],
        settings["bench_slots"]
    ))
    
    conn.commit()
    conn.close()

def get_league_settings():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM league_settings LIMIT 1')
    row = cursor.fetchone()
    conn.close()
    
    if row is None:
        return {
            "league_size": 12,
            "roster_size": 16,
            "qb_starters": 1,
            "rb_starters": 3,
            "wr_starters": 3,
            "te_starters": 1,
            "flex_starters": 1,
            "bench_slots": 7
        }
    
    return {
        "league_size": row[1],
        "roster_size": row[2],
        "qb_starters": row[3],
        "rb_starters": row[4],
        "wr_starters": row[5],
        "te_starters": row[6],
        "flex_starters": row[7],
        "bench_slots": row[8]
    }