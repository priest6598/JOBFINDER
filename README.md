# PathAI

AI-powered job search copilot for the Indian market. Free forever for the basics, pay per use (credits) for the power tools.

## Stack

- **Frontend:** Next.js 14 (App Router) + TypeScript + Tailwind + shadcn-style primitives + Framer Motion + Zustand + TanStack Query
- **Backend:** FastAPI + SQLAlchemy 2.0 (async) + SQLite (dev) / Postgres (prod) + Anthropic Claude Sonnet 4.5
- **Auth:** JWT (email/password). Swappable to Supabase Auth later.

## Quick start

```bash
# Backend
cd backend
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # add ANTHROPIC_API_KEY
python -m app.seeds.seed    # seed demo jobs
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Backend: http://localhost:8000 · API docs: http://localhost:8000/docs
Frontend: http://localhost:3000

## Pricing model (v1)

| Tier | Price | What you get |
|---|---|---|
| **Free** | ₹0 | 20 job matches/day, 2 AI-tailored resumes & cover letters/mo, 1 text mock/wk, ghost score, career DNA |
| **Boost** | ₹49 / 5 credits | Super apply (3cr), voice mock (5cr), company prep pack (8cr), salary coach (4cr), LinkedIn rewrite (6cr) |
| **Pro** | ₹399/mo | Everything unlimited, priority alerts, intro marketplace |

See [SPEC.md](./SPEC.md) for the full product spec.

## Repo layout

```
backend/   FastAPI app — models, routes, services, seeds
frontend/  Next.js app — App Router, components, lib, types
SPEC.md    Original product spec
```
