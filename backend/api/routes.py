import json
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
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
from services.preferences import DEFAULT_AGENTS, DEFAULT_TOOLS, ensure_settings, settings_out
from services.settings import get_settings
from tools.registry import tool_registry

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "mode": "local", "service": "firstai-backend"}


@router.post("/agent/run")
async def run_agent(payload: GoalRequest, db: Session = Depends(get_db)):
    return await manager_agent.run(db, payload.goal, payload.conversation_id)


@router.post("/agent/stream")
async def stream_agent(payload: GoalRequest, db: Session = Depends(get_db)):
    async def event_stream():
        async for event in manager_agent.run_events(db, payload.goal, payload.conversation_id):
            yield f"data: {json.dumps(event, default=str)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


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
    return await add_document(db, file)


@router.get("/knowledge/search")
def knowledge_search(q: str, db: Session = Depends(get_db)):
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
    if payload.model is not None:
        row.model = payload.model
    if payload.temperature is not None:
        row.temperature = payload.temperature
    if payload.memory_limit is not None:
        row.memory_limit = payload.memory_limit
    if payload.theme is not None:
        row.theme = payload.theme
    if payload.tools_enabled is not None:
        row.tools_enabled_json = dumps(payload.tools_enabled)
    if payload.agent_config is not None:
        row.agent_config_json = dumps(payload.agent_config)
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
    row.theme = "dark"
    row.tools_enabled_json = dumps(DEFAULT_TOOLS)
    row.agent_config_json = dumps(DEFAULT_AGENTS)
    db.commit()
    current = settings_out(db)
    return {**current, "tools": tool_registry.list(current["tools_enabled"])}
