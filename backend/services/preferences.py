from typing import Dict

from sqlalchemy.orm import Session

from database.models import AppSetting
from services.json_utils import dumps, loads
from services.settings import get_settings

DEFAULT_TOOLS = {
    "calculator": True,
    "file": True,
    "code": True,
    "search": True,
}

DEFAULT_AGENTS = {
    "manager": True,
    "planner": True,
    "executor": True,
    "memory": True,
}


def ensure_settings(db: Session) -> AppSetting:
    row = db.get(AppSetting, 1)
    if row:
        return row

    settings = get_settings()
    row = AppSetting(
        id=1,
        model=settings.default_model,
        temperature=0.4,
        memory_limit=20,
        theme="light",
        tools_enabled_json=dumps(DEFAULT_TOOLS),
        agent_config_json=dumps(DEFAULT_AGENTS),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def settings_out(db: Session) -> Dict:
    row = ensure_settings(db)
    settings = get_settings()
    return {
        "model": row.model,
        "temperature": row.temperature,
        "memory_limit": row.memory_limit,
        "theme": "light",
        "tools_enabled": loads(row.tools_enabled_json, DEFAULT_TOOLS),
        "agent_config": loads(row.agent_config_json, DEFAULT_AGENTS),
        "supported_models": settings.supported_models,
    }
