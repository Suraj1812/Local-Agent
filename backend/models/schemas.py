from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class GoalRequest(BaseModel):
    goal: str = Field(min_length=1, max_length=5000)
    conversation_id: Optional[int] = None


class AgentTask(BaseModel):
    id: int
    title: str
    priority: str = "medium"


class AgentActivity(BaseModel):
    current_goal: str
    current_task: Optional[str] = None
    completed_tasks: List[Dict[str, Any]] = []
    active_tool: Optional[str] = None
    execution_progress: int = 0
    reasoning_steps: List[str] = []
    status: str = "idle"


class MessageOut(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    metadata: Dict[str, Any]
    created_at: datetime


class ConversationOut(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageOut] = []


class AgentResponse(BaseModel):
    conversation: ConversationOut
    response: str
    plan: List[AgentTask]
    activity: AgentActivity


class SettingsIn(BaseModel):
    model: Optional[str] = None
    temperature: Optional[float] = Field(default=None, ge=0, le=1)
    memory_limit: Optional[int] = Field(default=None, ge=5, le=100)
    theme: Optional[str] = None
    tools_enabled: Optional[Dict[str, bool]] = None
    agent_config: Optional[Dict[str, bool]] = None


class SettingsOut(BaseModel):
    model: str
    temperature: float
    memory_limit: int
    theme: str
    tools_enabled: Dict[str, bool]
    agent_config: Dict[str, bool]
    supported_models: List[str]


class DocumentOut(BaseModel):
    id: int
    filename: str
    mime_type: str
    chunks: int = 0
    created_at: Optional[datetime] = None
