# FirstAI Local Agent

FirstAI is a local, self-hosted agentic AI application built with Next.js 15, FastAPI, SQLite, SQLAlchemy, Pydantic, and Ollama. It uses no paid AI APIs and does not depend on LangChain.

## Stack

- Frontend: Next.js 15 App Router, TypeScript, Tailwind CSS, Zustand, shadcn-style UI primitives
- Backend: Python, FastAPI, SQLite, SQLAlchemy, Pydantic
- AI brain: Ollama with local models such as DeepSeek-R1, Llama 3, and Qwen
- Agent framework: custom Manager, Planner, Executor, and Memory agents

## Setup

Install Ollama and pull at least one model:

```bash
ollama pull llama3
```

Install the app:

```bash
npm run install:all
```

Run both frontend and backend:

```bash
npm run dev
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000/api

## Local-Only Behavior

- Conversations, tasks, memories, logs, and knowledge documents are stored in `storage/firstai.db`.
- PDF, DOCX, Markdown, and TXT uploads are parsed locally.
- Knowledge search uses a lightweight local hashed embedding index stored in SQLite.
- If Ollama is not running, the app still works with a deterministic local fallback so the agent workflow remains visible.
