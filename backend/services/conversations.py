from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from database.models import Conversation, Message
from services.json_utils import dumps, loads
from services.text_utils import title_from_goal


def serialize_message(message: Message) -> Dict[str, Any]:
    return {
        "id": message.id,
        "conversation_id": message.conversation_id,
        "role": message.role,
        "content": message.content,
        "metadata": loads(message.metadata_json, {}),
        "created_at": message.created_at,
    }


def serialize_conversation(db: Session, conversation: Conversation, with_messages: bool = True) -> Dict[str, Any]:
    messages: List[Dict[str, Any]] = []
    if with_messages:
        rows = (
            db.query(Message)
            .filter(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.asc(), Message.id.asc())
            .all()
        )
        messages = [serialize_message(message) for message in rows]
    return {
        "id": conversation.id,
        "title": conversation.title,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "messages": messages,
    }


def ensure_conversation(db: Session, conversation_id: Optional[int], goal: str) -> Conversation:
    if conversation_id:
        existing = db.get(Conversation, conversation_id)
        if existing:
            return existing
    conversation = Conversation(title=title_from_goal(goal))
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def add_message(
    db: Session, conversation_id: int, role: str, content: str, metadata: Optional[Dict[str, Any]] = None
) -> Message:
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        metadata_json=dumps(metadata or {}),
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message
