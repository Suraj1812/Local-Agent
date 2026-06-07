from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from database.models import AgentLog
from services.json_utils import dumps, loads


def log_event(
    db: Session,
    action: str,
    detail: str,
    conversation_id: Optional[int] = None,
    level: str = "info",
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    db.add(
        AgentLog(
            conversation_id=conversation_id,
            level=level,
            action=action,
            detail=detail,
            metadata_json=dumps(metadata or {}),
        )
    )
    db.commit()


def list_logs(db: Session, limit: int = 80):
    rows = db.query(AgentLog).order_by(AgentLog.created_at.desc()).limit(limit).all()
    return [
        {
            "id": row.id,
            "conversation_id": row.conversation_id,
            "level": row.level,
            "action": row.action,
            "detail": row.detail,
            "metadata": loads(row.metadata_json, {}),
            "created_at": row.created_at,
        }
        for row in rows
    ]
