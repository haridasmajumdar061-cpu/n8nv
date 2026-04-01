# AI Life OS Platform

Production-oriented monorepo for an advanced automation platform inspired by n8n, plus adaptive AI Life OS modules.

## Stack

- Frontend: React + Vite + Tailwind + React Flow
- Backend: FastAPI + SQLAlchemy + JWT Auth
- Queue: Redis + Celery worker
- Database: PostgreSQL
- AI: OpenAI API
- Orchestration: Docker Compose

## Project Structure

- `frontend/` React app with drag-and-drop workflow builder and Life OS dashboard
- `backend/` FastAPI API, execution engine, scheduler, integrations, AI services
- `database/` bootstrap SQL + sample workflow JSON files
- `docker/` Dockerfiles

## Core Features Implemented

- Drag-and-drop workflow canvas (React Flow)
- Node model: trigger, action, AI node
- AI workflow generation endpoint (`prompt -> workflow JSON`)
- Workflow execution engine with log events
- Retry system using Celery task retries (exponential backoff)
- JWT auth (signup/login)
- PostgreSQL persistence (users, workflows, executions, logs, memories, plans)
- Real-time execution logs (WebSocket stream)
- Scheduling via cron expression on workflow (`*/5 * * * *` format)
- Integrations scaffold:
  - Gmail (send/read stub ready)
  - Telegram (real API call when token provided)
  - YouTube (read/upload scaffold)
- AI Life OS features:
  - Personal memory API
  - Smart daily planner
  - Income suggestion generator from skills
  - Focus mode orchestration endpoint
  - Voice assistant response endpoint

## API Overview

- `POST /api/auth/signup`
- `POST /api/auth/login`
- `GET /api/workflows`
- `POST /api/workflows`
- `PATCH /api/workflows/{workflow_id}`
- `POST /api/executions/run`
- `GET /api/executions/{execution_id}`
- `GET /api/executions/{execution_id}/logs`
- `WS /api/logs/stream/{execution_id}`
- `POST /api/ai/prompt-to-workflow`
- `POST /api/ai/improve-workflow`
- `POST /api/ai/auto-debug`
- `POST /api/integrations/gmail/send`
- `POST /api/integrations/gmail/read`
- `POST /api/integrations/google/oauth-url`
- `POST /api/integrations/google/exchange-code`
- `GET /api/integrations/google/callback`
- `POST /api/integrations/telegram/send`
- `POST /api/integrations/youtube/read`
- `POST /api/integrations/youtube/upload`
- `POST /api/life-os/memory`
- `GET /api/life-os/memory`
- `POST /api/life-os/planner`
- `POST /api/life-os/income-suggestions`
- `POST /api/life-os/focus-mode`
- `POST /api/life-os/voice-assistant`

## Run With Docker

1. Copy env values if needed (file already included):
   - `.env.example`
2. Start the stack:

```bash
docker compose up --build
```

3. Access apps:
   - Frontend: `http://localhost:5173`
   - Backend docs: `http://localhost:8000/docs`

## Local Development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Worker

```bash
cd backend
celery -A app.core.celery_app.celery_app worker -Q workflows -l info
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Sample Workflows

- `database/sample_workflows/gmail_to_telegram.json`
- `database/sample_workflows/daily_life_os.json`

## Notes for Production Hardening

- Add Alembic migrations and migration CI checks
- Add one-time nonce persistence to prevent OAuth state replay
- Complete YouTube resumable media chunk upload pipeline

## OAuth Notes

- Google OAuth `state` is HMAC-signed and time-limited before callback/code exchange.
- Set `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, and `GOOGLE_OAUTH_REDIRECT_URI` in `.env.example`.
- Add role-based access controls and refresh tokens
- Add metrics, tracing, and audit log policies
- Add integration tests for workflow execution graph and retry policies
