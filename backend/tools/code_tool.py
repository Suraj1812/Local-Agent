from typing import Any, Dict

from services.ollama import ollama_service


class CodeTool:
    name = "code"
    description = "Generate, refactor, and explain code with Ollama"

    async def execute(self, payload: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
You are a local Code Agent. Use no paid services.
Goal: {context.get("goal", "")}
Task: {payload.get("task", "")}
Operation: {payload.get("operation", "generate")}

Return concise markdown with useful code when relevant.
"""
        try:
            response = await ollama_service.generate(
                prompt,
                model=context["settings"]["model"],
                temperature=context["settings"]["temperature"],
            )
            return {"response": response}
        except Exception:
            return {
                "response": "Ollama is not reachable. Draft the code by defining components, state, validation, edge cases, and tests."
            }
