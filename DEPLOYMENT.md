# Deployment

This project is split into two deployable services:

- `backend/`: FastAPI API deployed on Railway
- `frontend/`: Next.js app deployed on Vercel

## Live Production URLs

- Frontend: https://firstai-local-agent.vercel.app
- Backend: https://firstai-backend-production.up.railway.app
- Backend health: https://firstai-backend-production.up.railway.app/api/health
- GitHub: https://github.com/Suraj1812/Local-Agent

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
- Railway backend deployment status: Success
- Railway health check returns `200`
- CORS allows `https://firstai-local-agent.vercel.app`
- Frontend homepage returns `200`
- Backend settings, dashboard, knowledge, logs, conversations, and agent run endpoints respond
- Agent fallback path works when cloud Ollama is not reachable
