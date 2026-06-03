from flask import Flask
from flask_cors import CORS
from data import get_all_players, get_trending_players

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return {"status": "Draft Assistant API is running"}

@app.route('/players')
def players():
    data = get_all_players()
    return {"count": len(data), "sample": list(data.items())[:3]}

if __name__ == '__main__':
    app.run(debug=True)