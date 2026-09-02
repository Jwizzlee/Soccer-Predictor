# Sports Predictor

Soccer prop research tool: search players, pull recent match stats from API-Football, and get Over/Under picks from GPT-4o-mini. Clerk handles auth, Stripe handles subscriptions.

## What it does

1. Search players (Premier League, La Liga)
2. Pick a prop — goals, assists, shots, shots on target — and set a line
3. Backend fetches the last N games, computes hit rate and averages
4. GPT-4o-mini returns a recommendation with short reasoning
5. Results save to your history; click a past pick to reload that player and prop

The backend is split by sport (`soccer` is live; `nba` / `nfl` folders are placeholders).

### How it's wired

```
React (Vite, TanStack Query, Clerk)
        │  REST + JWT
FastAPI
  ├── Clerk auth + Stripe billing
  ├── Prediction flow → OpenAI
  ├── Soccer provider → API-Football
  └── SQLite (billing.db) — subscriptions + history
```

**Season:** Live soccer data uses `SPORTS_API_SEASON=2024` in settings. The free API-Football plan only exposes certain seasons — don't bump this to the current year unless you have a paid key.

## Stack

| Layer | Tech |
|-------|------|
| Frontend | React, TypeScript, Vite, TanStack Query, Tailwind, Clerk |
| Backend | FastAPI, Python 3.11, httpx, aiosqlite, Pydantic |
| AI | OpenAI GPT-4o-mini |
| External | API-Football, Stripe |

## Rate limits (free API-Football plan)

- 10 requests/minute
- In-memory TTL cache: search + fixture lists (1h), player stats per fixture (12h)
- 429 responses retry once after 2.5s; if we're mid-batch, we return whatever games loaded
- `last_n_games` capped at 5 so a single analysis stays under the per-minute cap
- 0.6s pause between uncached `/fixtures/players` calls

## Project layout

```
backend/app/
  api/v1/endpoints/   predict, players, billing
  services/sports/soccer/   API-Football client + provider
  services/prediction_store.py
  data/billing.db     (gitignored)
frontend/src/
  pages/Dashboard.tsx
  components/predictions/
```

## Setup

**Requires:** Python 3.11+, Node 20+, API-Football key, OpenAI key, Clerk app, Stripe test account.

### Environment files

From the repo root, copy the example env files and fill in your keys (`SPORTS_API_SEASON=2024` on the backend).

```bash
# Windows (PowerShell)
Copy-Item backend/.env.example backend/.env
Copy-Item frontend/.env.example frontend/.env

# macOS / Linux
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### Backend

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt          # Windows
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

Docs: http://localhost:8000/docs

`USE_MOCK_SPORTS_DATA=true` skips API-Football (player IDs `1001`–`1004`).

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

### Stripe webhooks (local)

```bash
stripe listen --forward-to localhost:8000/api/v1/billing/webhook
```

Put the `whsec_...` value in `STRIPE_WEBHOOK_SECRET` and restart the backend.

## API (main routes)

| Method | Path | Auth |
|--------|------|------|
| GET | `/api/v1/leagues?sport=soccer` | — |
| GET | `/api/v1/players/search` | — |
| POST | `/api/v1/predict` | Clerk + subscription |
| GET | `/api/v1/predictions/history` | Clerk |
| POST | `/api/v1/billing/webhook` | Stripe signature |

Admin emails in `ADMIN_EMAIL_WHITELIST` skip the subscription check.

## Verify

```bash
cd frontend && npm run build

cd backend
.\.venv\Scripts\python.exe scripts\verify_project.py
```

## Status

| Done | Not yet |
|------|---------|
| Soccer props, PL + La Liga | NBA / NFL providers |
| Hit-rate UI, history, clickable picks | — |
| Clerk + Stripe | — |

---

For research and entertainment only — not betting or financial advice.
