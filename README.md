# Advisory Engine Rome: Personal Decision Intelligence System

A production-oriented multi-agent Personal Decision Intelligence System (PDIS) built with FastAPI, OpenAI, Supabase/Postgres + pgvector, React/Vite, Tailwind CSS, and Render.

## What it does

- Maintains structured user memory: goals, constraints, decisions, outcomes, behavioral patterns.
- Maintains semantic memory with OpenAI embeddings stored in `pgvector`.
- Runs four decision agents concurrently:
  - Strategist: long-term goal alignment.
  - Operator: execution feasibility.
  - Critic: behavioral risk and bias detection.
  - Risk Manager: hard-constraint and downside review.
- Produces structured JSON recommendations with versioned decisions and scored alternatives.
- Learns from `/feedback` by storing outcomes and updating behavioral patterns.

## Repository layout

```text
backend/
  agents/       Agent prompt templates and implementations
  db/           Supabase/Postgres schema
  memory/       Semantic memory store and retrieval
  models/       Pydantic request/response models
  routes/       FastAPI routes
  services/     Decision engine, OpenAI client, user model, database wrapper
frontend/
  src/components
  src/pages
  src/services
examples/
render.yaml
```

## Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="postgresql://..."
export OPENAI_API_KEY="sk-..."
uvicorn app:app --reload
```

Run `backend/db/schema.sql` in Supabase SQL editor before starting production traffic.

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Set `VITE_API_URL` to the deployed backend URL in production.

## Required environment variables

Backend:

- `DATABASE_URL`
- `OPENAI_API_KEY`
- `OPENAI_MODEL` (defaults to `gpt-4.1`)
- `OPENAI_EMBEDDING_MODEL` (defaults to `text-embedding-3-small`)
- `CORS_ORIGINS`
- `DEFAULT_USER_ID`

Frontend:

- `VITE_API_URL`

## Deployment

`render.yaml` defines:

- `pdis-backend`: FastAPI web service.
- `pdis-frontend`: static Vite site.

Connect this repository in Render and use the blueprint. Add `DATABASE_URL` from Supabase and `OPENAI_API_KEY` in Render environment settings.
