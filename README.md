# FirstAI AP Automation

FirstAI is a local-first AI finance platform redesigned for Accounts Payable automation. It demonstrates invoice ingestion, invoice-to-PO matching, 2-way and 3-way matching, exception detection, journal preview, ERP sync readiness, audit-oriented data models, and specialized finance agents.

The product direction is aligned with autonomous finance platforms such as Ledgent.AI: AI agents that understand documents, apply finance policy, resolve exceptions, and prepare ERP execution with auditability.

## Stack

- Frontend: Next.js 15 App Router, TypeScript, Tailwind CSS, Zustand, shadcn-style UI primitives
- Backend: Python, FastAPI, SQLite today with PostgreSQL target, SQLAlchemy, Pydantic
- AI brain: Ollama with local models such as DeepSeek-R1, Llama 3, and Qwen
- Agent framework: custom Manager, Planner, Executor, Memory, plus AP-specialized agent surfaces
- Deployment: Vercel frontend and Railway backend

## AP Modules

- Invoice Upload
- Invoice OCR and Document Intelligence
- Vendor Management
- Purchase Orders
- Goods Receipts
- Invoice Matching
- Exception Center
- Approval Workflows
- Journal Entries
- ERP Sync
- Audit Logs
- Analytics Dashboard
- Agent Monitoring

## Local Setup

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

## Key API Endpoints

```text
GET  /api/health
GET  /api/ap/overview
GET  /api/ap/invoices
GET  /api/ap/agents
POST /api/ap/matching/run
GET  /api/ap/architecture
POST /api/agent/stream
POST /api/knowledge/upload
```

## Architecture Docs

- `docs/ledgent-ap-platform.md`
- `docs/ledgent-ap-github-issues.md`

## Local-First Behavior

- Conversations, tasks, memories, logs, and knowledge documents are stored locally.
- PDF, DOCX, Markdown, CSV, JSON, and TXT uploads are parsed locally.
- Knowledge search uses a lightweight local hashed embedding index.
- If Ollama is not running, the app still works with deterministic fallback planning and execution.
