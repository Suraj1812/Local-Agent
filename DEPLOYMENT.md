# Deployment

This project is split into two deployable services:

- `backend/`: FastAPI API deployed on Railway
- `frontend/`: Next.js app deployed on Vercel

## Backend: Railway

Railway uses `backend/railway.json`.

Recommended service variables:

```text
DEFAULT_MODEL=llama3
OLLAMA_HOST=http://localhost:11434
DATABASE_URL=sqlite:////data/firstai.db
WORKSPACE_ROOT=/app
FRONTEND_ORIGIN=https://your-vercel-domain.vercel.app
ALLOWED_ORIGIN_REGEX=https://.*\.vercel\.app
```

For persistent SQLite storage, mount a Railway volume at `/data`.

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
NEXT_PUBLIC_API_BASE_URL=https://your-railway-backend-domain.up.railway.app/api
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
