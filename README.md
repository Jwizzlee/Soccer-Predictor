# Sports Predictor

AI-powered soccer prop research engine that analyzes player form, computes supporting statistics, and generates Over/Under recommendations with confidence scoring. Built as a full-stack portfolio application with authentication, subscriptions, and production-minded API integrations.

> **Disclaimer:** For research and entertainment only. Not financial or betting advice.

---

## Overview

Sports Predictor helps users evaluate player props (goals, assists, shots, shots on target) by:

1. Searching players across configured leagues (Premier League, La Liga)
2. Pulling recent match stats from API-Football
3. Aggregating hit rates, averages, and game-by-game form
4. Sending structured context to **GPT-4o-mini** for a reasoned Over/Under pick
5. Persisting analysis history per authenticated user

The backend uses a **multi-sport factory pattern** (soccer live; NBA/NFL scaffolded) so new sports can be added without rewriting the prediction pipeline.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  React Dashboard (Vite + TanStack Query + Clerk)                │
│  Player search · Prop config · Visual prediction card · History │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST + JWT
┌────────────────────────────▼────────────────────────────────────┐
│  FastAPI (Python 3.11)                                          │
│  ┌──────────────┐  ┌─────────────────┐  ┌─────────────────────┐ │
│  │ Clerk auth   │  │ Stripe billing  │  │ Prediction service  │ │
│  │ + admin gate │  │ + webhooks      │  │ + LLM orchestration │ │
│  └──────────────┘  └─────────────────┘  └──────────┬──────────┘ │
│                                                     │           │
│  ┌──────────────────────────────────────────────────▼─────────┐ │
│  │ Sports provider factory → Soccer (API-Football) + mock mode  │ │
│  │ TTL cache · 429 retry · partial batch fallback               │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ aiosqlite (billing.db) — subscriptions + prediction history│ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
         │                              │
         ▼                              ▼
   API-Football (2024 season)      OpenAI GPT-4o-mini
```

**Season constraint:** All live soccer queries use `SPORTS_API_SEASON=2024` from settings to stay within API-Football's free-tier season access. Do not dynamically switch to the current calendar year without a paid plan.

---

## Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Frontend** | React 18, TypeScript, Vite, TanStack Query, Tailwind CSS, Clerk |
| **Backend** | FastAPI, Python 3.11, httpx, aiosqlite, Pydantic v2 |
| **AI** | OpenAI GPT-4o-mini (structured prop analysis) |
| **Integrations** | Clerk (auth), Stripe (subscriptions + webhooks), API-Football |
| **Data** | SQLite (`billing.db`) for billing cache and prediction history |

---

## Key Engineering Highlights

- **TTL caching layer** — Player search and fixture lists cached 1h; per-fixture player stats cached 12h. Reduces API-Football calls on repeat analyses.
- **Rate-limit resilience** — HTTP 429 retry with 2.5s backoff; partial fixture batches proceed when the per-minute cap is hit mid-loop; user-friendly errors when zero games load.
- **Request budgeting** — `last_n_games` capped at 5 (frontend + backend) to stay under the free tier's 10 req/min limit.
- **Async SQLite persistence** — `billing_subscriptions` and `prediction_history` tables via `aiosqlite`, initialized on app lifespan.
- **Non-blocking history writes** — Prediction logging failures are caught and logged; they never block the primary analysis response.
- **Stripe webhook verification** — Signature validation on `checkout.session.completed`, `customer.subscription.updated/deleted`.
- **Subscription gate** — `POST /api/v1/predict` requires active Stripe subscription (admin email whitelist bypass for development).

---

## Project Structure

```
sports-predictor/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/     # predict, players, billing, leagues
│   │   ├── core/                 # config, auth, exceptions
│   │   ├── models/               # Pydantic request/response models
│   │   ├── services/
│   │   │   ├── sports/soccer/    # API-Football client, provider, cache
│   │   │   ├── llm/              # OpenAI client + prompts
│   │   │   ├── billing_store.py
│   │   │   └── prediction_store.py
│   │   └── data/billing.db       # SQLite (gitignored)
│   └── scripts/verify_project.py
├── frontend/
│   └── src/
│       ├── components/predictions/  # PredictionCard, HitRateBar, RecentPicks
│       ├── hooks/                   # usePrediction, usePredictionHistory
│       └── pages/Dashboard.tsx
└── README.md
```

---

## Local Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- [API-Football](https://www.api-football.com/) API key
- [OpenAI](https://platform.openai.com/) API key
- [Clerk](https://clerk.com/) application (publishable + secret keys)
- [Stripe](https://stripe.com/) account (test mode)

### 1. Environment variables

**Backend** — copy and fill `backend/.env`:

```bash
cp backend/.env.example backend/.env
```

Key values:

```env
SPORTS_API_KEY=your_api_football_key
SPORTS_API_SEASON=2024
OPENAI_API_KEY=your_openai_key
USE_MOCK_SPORTS_DATA=false
CLERK_JWT_ISSUER=https://your-instance.clerk.accounts.dev
CLERK_SECRET_KEY=sk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PRICE_ID=price_...
STRIPE_WEBHOOK_SECRET=whsec_...
FRONTEND_URL=http://localhost:5173
CORS_ORIGINS=http://localhost:5173,http://localhost:5174
ADMIN_EMAIL_WHITELIST=your@email.com
```

**Frontend** — copy and fill `frontend/.env`:

```bash
cp frontend/.env.example frontend/.env
```

```env
VITE_API_URL=http://localhost:8000
VITE_CLERK_PUBLISHABLE_KEY=pk_test_...
```

Set `USE_MOCK_SPORTS_DATA=true` in backend `.env` to run without API-Football quota (mock player IDs `1001`–`1004`).

### 2. Backend

```bash
cd backend
python -m venv .venv

# Windows
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000

# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard: http://localhost:5173

### 4. Stripe webhook listener (local)

Forward Stripe events to the backend webhook endpoint:

```bash
stripe listen --forward-to localhost:8000/api/v1/billing/webhook
```

Copy the printed `whsec_...` secret into `STRIPE_WEBHOOK_SECRET` in `backend/.env`, then restart the backend.

---

## API Surface (MVP)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/api/v1/leagues?sport=soccer` | Public | League list (static config) |
| `GET` | `/api/v1/players/search` | Public | Player search by name |
| `POST` | `/api/v1/predict` | Clerk + subscription | Generate Over/Under analysis |
| `GET` | `/api/v1/predictions/history` | Clerk | Last 10 predictions for user |
| `GET` | `/api/v1/billing/subscription-status` | Clerk | Subscription state |
| `POST` | `/api/v1/billing/create-checkout-session` | Clerk | Stripe Checkout |
| `POST` | `/api/v1/billing/webhook` | Stripe signature | Subscription lifecycle |

---

## Verification

### Frontend build

```bash
cd frontend
npm run build
```

### Backend health check

```bash
cd backend
.\.venv\Scripts\python.exe scripts\verify_project.py   # Windows
# python scripts/verify_project.py                     # macOS/Linux
```

Checks:

- FastAPI app imports without broken dependencies
- SQLite stores connect and create schema
- Tables `billing_subscriptions` and `prediction_history` exist

---

## MVP Scope

| Feature | Status |
|---------|--------|
| Soccer props (goals, assists, shots, SOT) | ✅ |
| Premier League + La Liga | ✅ |
| AI recommendations with reasoning | ✅ |
| Visual hit-rate bars and form badges | ✅ |
| Prediction history + clickable recent picks | ✅ |
| Clerk auth + Stripe subscriptions | ✅ |
| API-Football rate-limit handling | ✅ |
| NBA / NFL | 🔜 Scaffolded |

---

## License

MIT (or adjust as needed for your portfolio).
