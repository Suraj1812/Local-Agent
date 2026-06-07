# FirstAI

FirstAI is a local-first Agentic AI workspace powered by Ollama. The home screen is intentionally minimal: ask anything, get a real model-backed answer, and avoid fake demo responses or noisy internal status text.

## Stack

- Frontend: Next.js 15 App Router, TypeScript, Tailwind CSS, Zustand
- Backend: Python, FastAPI, SQLAlchemy, Pydantic
- Storage: SQLite locally, Railway volume in production
- AI: Ollama with local/open-source models
- Deployment: Vercel frontend, Railway backend, Railway Ollama service

## Local Setup

Install Ollama and pull the lightweight default model:

```bash
ollama pull qwen2.5:0.5b
```

Install and run the app:

```bash
npm run install:all
npm run dev
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000/api
- Ollama: http://localhost:11434

## Environment

Use `.env.example` as the base. The important values are:

```text
OLLAMA_HOST=http://localhost:11434
DEFAULT_MODEL=qwen2.5:0.5b
REQUIRE_OLLAMA=false
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
```

Production runs with `REQUIRE_OLLAMA=true`, so the backend only serves agent requests when the Ollama service and configured model are ready.

## Key API Endpoints

```text
GET  /api/health
GET  /api/health/ready
GET  /api/ollama/test
POST /api/agent/stream
POST /api/agent/run
POST /api/knowledge/upload
GET  /api/settings
```

## Behavior

- General questions go through Ollama instead of fixed static responses.
- Math-style prompts are routed through the calculator tool before the final answer.
- Missing-source-data questions ask for the needed data instead of inventing vendor, invoice, or risk details.
- The UI removes the old AP dashboard, metrics, logo block, side panels, and finance brief from the home screen.

Docs:

- `DEPLOYMENT.md`
- `docs/product-architecture.md`
