from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    ollama_host: str = "http://localhost:11434"
    default_model: str = "llama3"
    database_url: str = "sqlite:///./storage/firstai.db"
    workspace_root: str = str(Path(__file__).resolve().parents[2])
    frontend_origin: str = "http://localhost:3000"
    supported_models: List[str] = ["deepseek-r1", "llama3", "qwen"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()
