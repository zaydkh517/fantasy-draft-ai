[README.md](https://github.com/user-attachments/files/29522579/README.md)
<div align="center">

# 🏈 AI Fantasy Draft Engine

**AI-powered player recommendations for your fantasy football draft**

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)

**[Live Demo](https://fantasy-draft-ai-assistant.vercel.app) · [GitHub](https://github.com/zaydkh517/fantasy-draft-ai)**

</div>

---

## 🚀 What It Does

Most fantasy draft tools just show you a ranking list. This one actually thinks.

The AI Fantasy Draft Engine analyzes 2,800+ NFL players in real time and recommends who to draft based on your specific roster, the current round, and what your league needs — then explains every pick in plain English using GPT-4o-mini.

---

## ✨ Features

- **Smart Recommendations** — Multi-factor ranking algorithm scoring players on consensus ranking, age-based potential, positional need, yards/targets/snaps trends, experience, and depth chart standing
- **Round-Based Strategy** — Scoring weights shift dynamically across 4 draft phases (early, middle, late, very late) to reflect real draft strategy
- **AI Explanations** — Natural language reasoning for each recommendation powered by GPT-4o-mini, only generated on your turn to save time
- **Snake Draft Support** — Tracks pick order with full snake draft reversal logic
- **Auto Draft** — Simulates other teams' picks with need-based logic until it's your turn
- **Live Roster Management** — Automatically assigns players to QB/RB/WR/TE/FLEX/Bench slots
- **Draft Board** — Tracks every pick made by every team throughout the draft
- **All Players Tab** — Searchable, position-filtered list of all available players ranked by your algorithm
- **League Customization** — Fully configurable league size, roster composition, and draft position

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| Database | SQLite |
| Frontend | React |
| Player Data | Sleeper REST API |
| Stats Data | Sleeper Stats API (2024/2025 seasons) |
| AI | OpenAI GPT-4o-mini |
| Backend Deployment | Railway |
| Frontend Deployment | Vercel |

---

## 🧠 How The Algorithm Works

Players are scored across 5 factors that shift in weight depending on the draft round:

| Score | What It Measures |
|-------|-----------------|
| **Base Score** | Consensus community ranking from Sleeper ADP |
| **Potential Score** | Age curve, yards/targets/snaps trends, experience, depth chart role |
| **Sleeper Score** | How undervalued a player is relative to their potential |
| **Need Score** | How much your current roster needs that position |
| **Overall Score** | Combined weighted score across all factors |

Early rounds (1-3) weight consensus heavily. Late rounds (13+) weight upside and sleeper value — finding gems the market is sleeping on.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/sync-players` | Fetch and cache players + stats from Sleeper API |
| `GET` | `/players` | Get all players from database |
| `POST` | `/recommend` | Get top 10 recommendations with optional AI explanations |
| `POST` | `/rank-all` | Get all available players ranked by algorithm |
| `POST` | `/autodraft` | Get best pick for a simulated team |
| `POST` | `/draft` | Mark a player as drafted |
| `GET` | `/drafted` | Get all drafted players |
| `POST` | `/settings` | Save league settings |
| `GET` | `/settings` | Get league settings |
| `POST` | `/reset` | Reset draft state |

---

## 👤 Author

**Zayd Khan** · [LinkedIn](https://www.linkedin.com/in/zayd-khan-124bb1368) · [GitHub](https://github.com/zaydkh517)

</div>
