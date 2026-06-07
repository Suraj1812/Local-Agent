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
DEFAULT_MODEL=qwen2.5:0.5b
REQUIRE_OLLAMA=true
OLLAMA_HOST=http://ollama.railway.internal:11434
DATABASE_URL=sqlite:////data/firstai.db
WORKSPACE_ROOT=/app
FRONTEND_ORIGIN=https://firstai-local-agent.vercel.app
ALLOWED_ORIGINS=https://firstai-local-agent.vercel.app,https://firstai-local-agent-l1zxglbi8-suraj-singhs-projects-da72b281.vercel.app
ALLOWED_ORIGIN_REGEX=https://.*\.vercel\.app
```

For persistent SQLite storage, mount a Railway volume at `/data`. The production service has a 500 MB Railway volume mounted at `/data`.

Liveness health check:

```text
/api/health
```

AI readiness and model test:

```text
/api/health/ready
/api/ollama/health
/api/ollama/test
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

## Ollama: Railway

Production AI responses require a reachable Ollama HTTP service. Railway service-to-service traffic should use the private domain and explicit Ollama port:

```text
http://ollama.railway.internal:11434
```

The production project uses a separate Railway service:

```text
Service: ollama
Build path: ollama/
Variable: OLLAMA_HOST=0.0.0.0:11434
Variable: OLLAMA_MODEL=qwen2.5:0.5b
Volume mount: /root/.ollama
Model: qwen2.5:0.5b
```

Manual model install command inside the Ollama service, if needed:

```bash
ollama pull qwen2.5:0.5b
```

Keep `REQUIRE_OLLAMA=true` on the backend only after `/api/ollama/test` succeeds. Vercel does not call Ollama directly; all AI requests go through the FastAPI backend. Larger models such as `llama3.2:3b` or `deepseek-r1` need a larger Railway volume than the current 500 MB model volume.

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

## Local Ollama

The app never uses paid AI APIs. For local development:

```bash
ollama serve
ollama pull qwen2.5:0.5b
```

Use:

```text
OLLAMA_HOST=http://localhost:11434
DEFAULT_MODEL=qwen2.5:0.5b
REQUIRE_OLLAMA=false
```

## Production Verification

Verified on June 7, 2026:

- Vercel production deployment status: Ready
- Vercel Git deployment source: `Suraj1812/Local-Agent` on `main`
- Railway backend deployment status: Success
- Railway health check returns `200`
- CORS allows `https://firstai-local-agent.vercel.app`
- Frontend homepage returns `200` and renders light-only UI
- Backend settings, dashboard, knowledge, logs, conversations, and agent run endpoints respond
- `/api/health/ready` returns `ready` with `qwen2.5:0.5b` loaded through `ollama.railway.internal`
- `/api/ollama/test` returns `OK.`
- AP agent response returns structured invoice risk output with no raw markdown headings or fallback text
- Mobile viewport has no horizontal overflow

Additional AP endpoints:

```text
/api/ap/overview
/api/ap/invoices
/api/ap/agents
/api/ap/matching/run
/api/ap/architecture
```
