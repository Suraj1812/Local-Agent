from typing import Any, AsyncGenerator, Dict, Optional

import httpx

from services.settings import get_settings
from services.text_utils import extract_json


class OllamaService:
    def __init__(self):
        self.settings = get_settings()

    async def generate(self, prompt: str, model: Optional[str] = None, temperature: float = 0.4) -> str:
        async with httpx.AsyncClient(timeout=httpx.Timeout(45, connect=8)) as client:
            response = await client.post(
                f"{self.settings.ollama_host}/api/generate",
                json={
                    "model": model or self.settings.default_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": temperature},
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
    ) -> Any:
        try:
            text = await self.generate(prompt, model=model, temperature=temperature)
            return extract_json(text) or fallback
        except Exception:
            return fallback

    async def stream_generate(
        self, prompt: str, model: Optional[str] = None, temperature: float = 0.4
    ) -> AsyncGenerator[str, None]:
        async with httpx.AsyncClient(timeout=httpx.Timeout(90, connect=8)) as client:
            async with client.stream(
                "POST",
                f"{self.settings.ollama_host}/api/generate",
                json={
                    "model": model or self.settings.default_model,
                    "prompt": prompt,
                    "stream": True,
                    "options": {"temperature": temperature},
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
