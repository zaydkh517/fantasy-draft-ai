import sqlite3
import json

DATABASE = "draft.db"

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
            search_rank INTEGER
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS drafted_players (
            player_id TEXT PRIMARY KEY,
            drafted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            (player_id, full_name, position, team, age, years_exp, injury_status, depth_chart_order, search_rank)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            player["player_id"],
            player["full_name"],
            player["position"],
            player["team"],
            player["age"],
            player["years_exp"],
            player["injury_status"],
            player["depth_chart_order"],
            player["search_rank"]
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
            "search_rank": row[8]
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