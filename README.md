<div align="center">

# 🏈 AI Fantasy Draft Engine

**AI-powered player recommendations for your fantasy football draft**

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)

[Live Demo](https://fantasy-draft-ai-production.up.railway.app) · [GitHub](https://github.com/zaydkh517/fantasy-draft-ai)

</div>

---

## 🚀 What It Does

Most fantasy draft tools just show you a ranking list. This one actually thinks.

The AI Fantasy Draft Engine analyzes 2,800+ NFL players in real time and recommends who to draft based on your specific roster, the current round, and what your league needs — then explains every pick in plain English using GPT-4o-mini.

---

## ✨ Features

- **Smart Recommendations** — Multi-factor ranking algorithm scoring players on consensus ranking, age-based potential, positional need, and sleeper upside
- **Round-Based Strategy** — Scoring weights shift dynamically across 4 draft phases (early, middle, late, very late) to reflect real draft strategy
- **AI Explanations** — Natural language reasoning for every recommendation powered by GPT-4o-mini
- **League Customization** — Fully configurable league size, roster composition, and draft position
- **Live Player Data** — 2,800+ NFL player records fetched from the Sleeper API

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| Database | SQLite |
| Frontend | React |
| Player Data | Sleeper REST API |
| AI | OpenAI GPT-4o-mini |
| Deployment | Railway |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/sync-players` | Fetch and cache players from Sleeper API |
| `GET` | `/players` | Get all players from database |
| `POST` | `/recommend` | Get top 10 recommendations with AI explanations |
| `POST` | `/draft` | Mark a player as drafted |
| `GET` | `/drafted` | Get all drafted players |
| `POST` | `/settings` | Save league settings |
| `GET` | `/settings` | Get league settings |
| `POST` | `/reset` | Reset draft state |

---

## 👤 Author

**Zayd Khan** · [LinkedIn](https://www.linkedin.com/in/zayd-khan-124bb1368) · [GitHub](https://github.com/zaydkh517)

</div>
