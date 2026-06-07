import asyncio
import re
from typing import Any, Dict

from tools.registry import tool_registry


def select_tool(task: Dict[str, Any], goal: str) -> str:
    text = f"{goal} {task.get('title', '')}".lower()
    tokens = set(re.findall(r"[a-z0-9_+-]+", text))
    if tokens & {"search", "knowledge", "document", "documents", "uploaded", "memory"}:
        return "search"
    if tokens & {"calculate", "calculation", "math", "stat", "stats", "statistics"}:
        return "calculator"
    if re.search(r"\d+(?:\.\d+)?\s*%\s*(?:of|x|\*)\s*\d+(?:\.\d+)?", text):
        return "calculator"
    if re.search(r"\d+\s*[\+\-\*/%]\s*\d+", text):
        return "calculator"
    if tokens & {"build", "code", "component", "generate", "login", "react", "typescript", "ui", "validation"}:
        return "code"
    return "model"


class ExecutorAgent:
    async def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        tool_name = select_tool(task, context["goal"])
        if tool_name == "model":
            return {
                "tool": None,
                "tool_result": {"status": "direct_model_answer"},
                "response": "Ready for a direct model answer.",
            }

        try:
            tool = tool_registry.get(tool_name, context["settings"]["tools_enabled"])
        except Exception:
            tool_name = "search"
            tool = tool_registry.get(tool_name, context["settings"]["tools_enabled"])

        try:
            if tool_name == "calculator":
                tool_result = await asyncio.wait_for(
                    tool.execute({"expression": context["goal"][:500]}, context), timeout=12
                )
            elif tool_name == "code":
                tool_result = await asyncio.wait_for(
                    tool.execute({"operation": "generate", "task": task.get("title", "")[:500]}, context), timeout=30
                )
            else:
                tool_result = await asyncio.wait_for(
                    tool.execute({"query": context["goal"][:500], "limit": 5}, context), timeout=15
                )
        except Exception as exc:
            tool_result = {"error": str(exc)[:300], "status": "tool_failed"}

        if isinstance(tool_result, dict) and tool_result.get("error"):
            response = f"The {tool_name} tool could not complete: {tool_result['error']}."
        elif tool_name == "calculator" and isinstance(tool_result, dict):
            response = f"Calculated {tool_result.get('expression')} = {tool_result.get('result')}."
        else:
            response = f"{tool_name} result: {tool_result}"

        return {"tool": tool_name, "tool_result": tool_result, "response": response}
