from typing import Any, Dict, List

from sqlalchemy.orm import Session

from database.models import Memory, Message
from services.json_utils import dumps, loads


def recent_messages(db: Session, conversation_id: int, limit: int) -> List[Dict[str, Any]]:
    rows = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc(), Message.id.desc())
        .limit(limit)
        .all()
    )
    return [
        {"role": row.role, "content": row.content, "metadata": loads(row.metadata_json, {})}
        for row in reversed(rows)
    ]


def long_term_memories(db: Session, limit: int) -> List[Dict[str, Any]]:
    rows = (
        db.query(Memory)
        .filter(Memory.type == "long_term")
        .order_by(Memory.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {"id": row.id, "key": row.key, "value": row.value, "metadata": loads(row.metadata_json, {})}
        for row in rows
    ]


def remember(db: Session, memory_type: str, key: str, value: str, metadata: Dict[str, Any]) -> None:
    db.add(Memory(type=memory_type, key=key, value=value, metadata_json=dumps(metadata)))
    db.commit()
