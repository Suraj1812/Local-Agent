from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    ollama_host: str = "http://localhost:11434"
    default_model: str = "qwen2.5:0.5b"
    require_ollama: bool = False
    database_url: str = "sqlite:///./storage/firstai.db"
    workspace_root: str = str(Path(__file__).resolve().parents[2])
    frontend_origin: str = "http://localhost:3000"
    allowed_origins: str = ""
    allowed_origin_regex: Optional[str] = r"https://.*\.vercel\.app"
    supported_models: List[str] = ["qwen2.5:0.5b", "llama3.2:3b", "llama3", "deepseek-r1", "qwen2.5"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()
