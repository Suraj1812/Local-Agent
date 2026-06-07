import json
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from agents.manager import manager_agent
from database.models import AgentLog, AppSetting, Conversation, Document, Memory, Task
from database.session import get_db
from models.schemas import GoalRequest, SettingsIn
from services.conversations import serialize_conversation
from services.json_utils import dumps
from services.knowledge import add_document, list_documents, search_knowledge
from services.logging import list_logs
from services.ollama import ollama_service
from services.preferences import DEFAULT_AGENTS, DEFAULT_TOOLS, ensure_settings, settings_out
from services.settings import get_settings
from tools.registry import tool_registry

router = APIRouter()

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
ALLOWED_UPLOAD_SUFFIXES = {".pdf", ".docx", ".txt", ".md", ".csv", ".json"}
ALLOWED_UPLOAD_MIME_PARTS = {
    "pdf",
    "plain",
    "markdown",
    "json",
    "csv",
    "wordprocessingml",
}


@router.get("/health")
def health():
    return {"status": "ok", "mode": "local-agent", "service": "firstai-backend"}


@router.get("/health/ready")
async def readiness():
    settings = get_settings()
    ollama = await ollama_service.status()
    ready = bool(ollama["available"] and ollama["model_ready"])
    payload = {
        "status": "ready" if ready or not settings.require_ollama else "degraded",
        "service": "firstai-backend",
        "require_ollama": settings.require_ollama,
        "ollama": ollama,
    }
    if settings.require_ollama and not ready:
        raise HTTPException(status_code=503, detail=payload)
    return payload


@router.get("/ollama/health")
async def ollama_health():
    return await ollama_service.status()


@router.get("/ollama/test")
async def ollama_test():
    status = await ollama_service.status()
    if not status["available"] or not status["model_ready"]:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "AI model service is not ready.",
                "ollama": status,
            },
        )
    response = await ollama_service.generate(
        "Reply with OK.",
        temperature=0.1,
        num_predict=8,
    )
    return {
        "status": "ok",
        "model": status["configured_model"],
        "response": " ".join(response.strip().split())[:500],
    }


@router.post("/agent/run")
async def run_agent(payload: GoalRequest, db: Session = Depends(get_db)):
    await _ensure_ai_ready_if_required()
    return await manager_agent.run(db, payload.goal, payload.conversation_id)


@router.post("/agent/stream")
async def stream_agent(payload: GoalRequest, db: Session = Depends(get_db)):
    await _ensure_ai_ready_if_required()

    async def event_stream():
        async for event in manager_agent.run_events(db, payload.goal, payload.conversation_id):
            yield f"data: {json.dumps(event, default=str)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


async def _ensure_ai_ready_if_required():
    settings = get_settings()
    if not settings.require_ollama:
        return
    status = await ollama_service.status()
    if not status["available"] or not status["model_ready"]:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "AI model service is not ready.",
                "ollama": status,
            },
        )


@router.get("/conversations")
def conversations(db: Session = Depends(get_db)):
    rows = db.query(Conversation).order_by(Conversation.updated_at.desc()).all()
    return [serialize_conversation(db, row, with_messages=False) for row in rows]


@router.get("/conversations/{conversation_id}")
def conversation(conversation_id: int, db: Session = Depends(get_db)):
    row = db.get(Conversation, conversation_id)
    if not row:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return serialize_conversation(db, row)


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    task_breakdown = (
        db.query(Task.status, func.count(Task.id).label("count")).group_by(Task.status).all()
    )
    return {
        "totals": {
            "conversations": db.query(Conversation).count(),
            "tasks": db.query(Task).count(),
            "completed_tasks": db.query(Task).filter(Task.status == "completed").count(),
            "memories": db.query(Memory).count(),
            "documents": db.query(Document).count(),
        },
        "task_breakdown": [{"status": row.status, "count": row.count} for row in task_breakdown],
        "recent_activity": list_logs(db, limit=8),
    }


@router.get("/knowledge")
def documents(db: Session = Depends(get_db)):
    return list_documents(db)


@router.post("/knowledge/upload")
async def upload_knowledge(file: UploadFile = File(...), db: Session = Depends(get_db)):
    filename = (file.filename or "").strip()
    suffix = f".{filename.rsplit('.', 1)[-1].lower()}" if "." in filename else ""
    mime = (file.content_type or "").lower()
    size = getattr(file, "size", None)

    if not filename:
        raise HTTPException(status_code=400, detail="File name is required")
    if suffix not in ALLOWED_UPLOAD_SUFFIXES and not any(part in mime for part in ALLOWED_UPLOAD_MIME_PARTS):
        raise HTTPException(status_code=400, detail="Unsupported file type")
    if size is not None and size > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File is too large")
    return await add_document(db, file)


@router.get("/knowledge/search")
def knowledge_search(q: str = Query(min_length=2, max_length=500), db: Session = Depends(get_db)):
    return search_knowledge(db, q)


@router.get("/logs")
def logs(db: Session = Depends(get_db)):
    return list_logs(db)


@router.get("/settings")
def read_settings(db: Session = Depends(get_db)):
    current = settings_out(db)
    return {**current, "tools": tool_registry.list(current["tools_enabled"])}


@router.put("/settings")
def update_settings(payload: SettingsIn, db: Session = Depends(get_db)):
    row = ensure_settings(db)
    settings = get_settings()
    if payload.model is not None:
        if payload.model not in settings.supported_models:
            raise HTTPException(status_code=400, detail="Unsupported model")
        row.model = payload.model
    if payload.temperature is not None:
        row.temperature = payload.temperature
    if payload.memory_limit is not None:
        row.memory_limit = payload.memory_limit
    if payload.theme is not None:
        row.theme = "light"
    if payload.tools_enabled is not None:
        row.tools_enabled_json = dumps({**DEFAULT_TOOLS, **payload.tools_enabled})
    if payload.agent_config is not None:
        row.agent_config_json = dumps({**DEFAULT_AGENTS, **payload.agent_config})
    db.commit()
    current = settings_out(db)
    return {**current, "tools": tool_registry.list(current["tools_enabled"])}


@router.post("/settings/reset")
def reset_settings(db: Session = Depends(get_db)):
    settings = get_settings()
    row = db.get(AppSetting, 1)
    if not row:
        row = AppSetting(id=1)
        db.add(row)
    row.model = settings.default_model
    row.temperature = 0.4
    row.memory_limit = 20
    row.theme = "light"
    row.tools_enabled_json = dumps(DEFAULT_TOOLS)
    row.agent_config_json = dumps(DEFAULT_AGENTS)
    db.commit()
    current = settings_out(db)
    return {**current, "tools": tool_registry.list(current["tools_enabled"])}
