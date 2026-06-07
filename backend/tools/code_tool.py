from typing import Any, Dict

from services.ollama import ollama_service


class CodeTool:
    name = "code"
    description = "Generate, refactor, and explain code with Ollama"

    async def execute(self, payload: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        goal = " ".join(str(context.get("goal", "")).strip().split())[:1200]
        task = " ".join(str(payload.get("task", "")).strip().split())[:300]
        prompt = f"""
Goal: {goal}
Task: {task}

Return concise, usable code. No extra explanation unless needed.
"""
        try:
            response = await ollama_service.generate(
                prompt,
                model=context["settings"]["model"],
                temperature=context["settings"]["temperature"],
                num_predict=120,
            )
            return {"response": response}
        except Exception as exc:
            return {"error": f"Code generation could not reach the local model: {str(exc)[:180]}"}
