# Deployment

This project is split into two deployable services:

- `backend/`: FastAPI finance/AP API deployed on Railway
- `frontend/`: Next.js AP automation command center deployed on Vercel

Architecture docs:

- `docs/ledgent-ap-platform.md`
- `docs/ledgent-ap-github-issues.md`

## Live Production URLs

- Frontend: https://firstai-local-agent.vercel.app
- Backend: https://firstai-backend-production.up.railway.app
- Backend health: https://firstai-backend-production.up.railway.app/api/health
- GitHub: https://github.com/Suraj1812/Local-Agent
- Custom domains: not configured

## Backend: Railway

Railway uses `backend/railway.json`.

Recommended service variables:

```text
DEFAULT_MODEL=llama3
OLLAMA_HOST=http://localhost:11434
DATABASE_URL=sqlite:////data/firstai.db
WORKSPACE_ROOT=/app
FRONTEND_ORIGIN=https://firstai-local-agent.vercel.app
ALLOWED_ORIGINS=https://firstai-local-agent.vercel.app,https://firstai-local-agent-l1zxglbi8-suraj-singhs-projects-da72b281.vercel.app
ALLOWED_ORIGIN_REGEX=https://.*\.vercel\.app
```

For persistent SQLite storage, mount a Railway volume at `/data`. The production service has a 500 MB Railway volume mounted at `/data`.

Health check:

```text
/api/health
```

Start command:

```bash
uvicorn main:app --host 0.0.0.0 --port ${PORT}
```

Manual deploy command from the repo:

```bash
cd backend
railway up . --path-as-root --detach --service firstai-backend
```

`--path-as-root` is important because the repository root also has a Node package for local orchestration. Without it, Railway can infer the wrong runtime.

Production guardrails:

- CORS allows the Vercel frontend and Vercel preview deployments
- Security headers are added on every response
- Heavy agent and upload paths have request limits
- Goals, settings, search queries, and uploads are validated
- Uploads are limited to readable PDF, DOCX, text, markdown, CSV, and JSON files up to 10 MB
- Ollama waits are bounded so unreachable local models do not hang the service

## Frontend: Vercel

Vercel uses `frontend/vercel.json`.

Required production variable:

```text
NEXT_PUBLIC_API_BASE_URL=https://firstai-backend-production.up.railway.app/api
```

Build command:

```bash
npm run build
```

Production UI:

- Light theme only
- Single agent command bar with compact icon controls
- Flat invoice queue with contextual finance intelligence
- Queue, exception, and agent views without decorative panels
- Dynamic `/icon` app icon route
- Metadata configured for title, description, app name, and Open Graph
- Frontend requests have timeouts and user-friendly error messages

The Vercel project is connected to `Suraj1812/Local-Agent`; pushes to `main`
create production deployments automatically.

## Local Verification

```bash
npm run backend:check
npm run build --prefix frontend
npm run dev
```

Open:

```text
http://localhost:3000
```

## Ollama Note

The app never uses paid AI APIs. In a cloud deployment, the Railway backend cannot reach Ollama running on your laptop at `localhost`. For full AI model responses in production, set `OLLAMA_HOST` to a reachable self-hosted Ollama endpoint or deploy Ollama as a separate service with enough CPU/RAM and persistent model storage. If Ollama is unreachable, the backend keeps the agent workflow usable through its local fallback planner/executor.

## Production Verification

Verified on June 7, 2026:

- Vercel production deployment status: Ready
- Vercel Git deployment source: `Suraj1812/Local-Agent` on `main`
- Railway backend deployment status: Success
- Railway health check returns `200`
- CORS allows `https://firstai-local-agent.vercel.app`
- Frontend homepage returns `200` and renders light-only UI
- Backend settings, dashboard, knowledge, logs, conversations, and agent run endpoints respond
- Agent streaming and fallback paths work when cloud Ollama is not reachable
- Mobile viewport has no horizontal overflow

Additional AP endpoints:

```text
/api/ap/overview
/api/ap/invoices
/api/ap/agents
/api/ap/matching/run
/api/ap/architecture
```
