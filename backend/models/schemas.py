from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

ALLOWED_TOOLS = {"calculator", "file", "code", "search"}
ALLOWED_AGENTS = {"manager", "planner", "executor", "memory"}


class GoalRequest(BaseModel):
    goal: str = Field(min_length=2, max_length=3000)
    conversation_id: Optional[int] = Field(default=None, gt=0)

    @field_validator("goal", mode="before")
    @classmethod
    def clean_goal(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("Goal must be text")
        cleaned = " ".join(value.strip().split())
        if not cleaned:
            raise ValueError("Goal cannot be empty")
        return cleaned


class AgentTask(BaseModel):
    id: int
    title: str
    priority: str = "medium"


class AgentActivity(BaseModel):
    current_goal: str
    current_task: Optional[str] = None
    completed_tasks: List[Dict[str, Any]] = Field(default_factory=list)
    active_tool: Optional[str] = None
    execution_progress: int = 0
    reasoning_steps: List[str] = Field(default_factory=list)
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
    messages: List[MessageOut] = Field(default_factory=list)


class AgentResponse(BaseModel):
    conversation: ConversationOut
    response: str
    plan: List[AgentTask]
    activity: AgentActivity


class SettingsIn(BaseModel):
    model: Optional[str] = Field(default=None, min_length=1, max_length=80)
    temperature: Optional[float] = Field(default=None, ge=0, le=1)
    memory_limit: Optional[int] = Field(default=None, ge=5, le=100)
    theme: Optional[Literal["light"]] = None
    tools_enabled: Optional[Dict[str, bool]] = Field(default=None, max_length=20)
    agent_config: Optional[Dict[str, bool]] = Field(default=None, max_length=20)

    @field_validator("model", mode="before")
    @classmethod
    def clean_model(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not isinstance(value, str):
            raise ValueError("Model must be text")
        return value.strip()

    @field_validator("tools_enabled")
    @classmethod
    def validate_tools(cls, value: Optional[Dict[str, bool]]) -> Optional[Dict[str, bool]]:
        if value is None:
            return value
        unknown = set(value) - ALLOWED_TOOLS
        if unknown:
            raise ValueError(f"Unsupported tools: {', '.join(sorted(unknown))}")
        return value

    @field_validator("agent_config")
    @classmethod
    def validate_agents(cls, value: Optional[Dict[str, bool]]) -> Optional[Dict[str, bool]]:
        if value is None:
            return value
        unknown = set(value) - ALLOWED_AGENTS
        if unknown:
            raise ValueError(f"Unsupported agents: {', '.join(sorted(unknown))}")
        return value


class SettingsOut(BaseModel):
    model: str
    temperature: float
    memory_limit: int
    theme: str
    tools_enabled: Dict[str, bool]
    agent_config: Dict[str, bool]
    supported_models: List[str]
    require_ollama: bool = False


class DocumentOut(BaseModel):
    id: int
    filename: str
    mime_type: str
    chunks: int = 0
    created_at: Optional[datetime] = None
