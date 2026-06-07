import asyncio
from typing import Any, AsyncGenerator, Dict, List, Optional

import httpx

from services.settings import get_settings
from services.text_utils import extract_json


class OllamaService:
    def __init__(self):
        self.settings = get_settings()
        self._generate_lock = asyncio.Lock()

    @property
    def host(self) -> str:
        return self.settings.ollama_host.rstrip("/")

    async def status(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "available": False,
            "host": self.host,
            "configured_model": self.settings.default_model,
            "model_ready": False,
            "models": [],
            "version": None,
            "detail": "Ollama service is not reachable.",
        }
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(6, connect=2)) as client:
                version_response = await client.get(f"{self.host}/api/version")
                version_response.raise_for_status()
                tags_response = await client.get(f"{self.host}/api/tags")
                tags_response.raise_for_status()
            models = [
                item.get("name")
                for item in tags_response.json().get("models", [])
                if isinstance(item, dict) and item.get("name")
            ]
            payload.update(
                {
                    "available": True,
                    "version": version_response.json().get("version"),
                    "models": models,
                    "model_ready": self._has_model(models, self.settings.default_model),
                    "detail": "Ollama is reachable.",
                }
            )
            if not payload["model_ready"]:
                payload["detail"] = f"Configured model '{self.settings.default_model}' is not installed."
        except Exception as exc:
            payload["detail"] = str(exc)[:180]
        return payload

    async def ready(self) -> bool:
        payload = await self.status()
        return bool(payload["available"] and payload["model_ready"])

    @staticmethod
    def _has_model(models: List[str], requested_model: str) -> bool:
        requested = requested_model.strip()
        if requested in models:
            return True
        if ":" not in requested:
            return f"{requested}:latest" in models
        return False

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.4,
        num_predict: int = 240,
    ) -> str:
        async with self._generate_lock:
            async with httpx.AsyncClient(timeout=httpx.Timeout(150, connect=8, read=150)) as client:
                response = await client.post(
                    f"{self.host}/api/generate",
                    json={
                        "model": model or self.settings.default_model,
                        "prompt": prompt,
                        "stream": False,
                        "keep_alive": "10m",
                        "options": {"temperature": temperature, "num_predict": num_predict, "num_ctx": 1024},
                    },
                )
                response.raise_for_status()
                return response.json().get("response", "")

    async def generate_json(
        self,
        prompt: str,
        fallback: Any,
        model: Optional[str] = None,
        temperature: float = 0.4,
        num_predict: int = 260,
    ) -> Any:
        try:
            text = await self.generate(
                prompt, model=model, temperature=temperature, num_predict=num_predict
            )
            return extract_json(text) or fallback
        except Exception:
            return fallback

    async def stream_generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.4,
        num_predict: int = 260,
    ) -> AsyncGenerator[str, None]:
        async with httpx.AsyncClient(timeout=httpx.Timeout(120, connect=8, read=120)) as client:
            async with client.stream(
                "POST",
                f"{self.host}/api/generate",
                json={
                    "model": model or self.settings.default_model,
                    "prompt": prompt,
                    "stream": True,
                    "options": {"temperature": temperature, "num_predict": num_predict, "num_ctx": 2048},
                },
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        payload: Dict[str, Any] = httpx.Response(200, content=line).json()
                        if payload.get("response"):
                            yield payload["response"]
                    except Exception:
                        continue


ollama_service = OllamaService()
