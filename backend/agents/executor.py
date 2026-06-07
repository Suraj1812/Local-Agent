import asyncio
import re
from typing import Any, Dict

from services.ollama import ollama_service
from tools.registry import tool_registry


def select_tool(task: Dict[str, Any], goal: str) -> str:
    text = f"{goal} {task.get('title', '')}".lower()
    tokens = set(re.findall(r"[a-z0-9_+-]+", text))
    if tokens & {"search", "research", "knowledge", "summarize", "summary"}:
        return "search"
    if tokens & {"calculate", "calculation", "math", "stat", "stats", "statistics"}:
        return "calculator"
    if tokens & {"build", "code", "component", "generate", "login", "react", "typescript", "ui", "validation"}:
        return "code"
    return "search"


class ExecutorAgent:
    async def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        tool_name = select_tool(task, context["goal"])
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

        prompt = f"""
You are Executor Agent. Summarize the task result without exposing hidden chain-of-thought.
Goal: {context["goal"]}
Task: {task.get("title")}
Tool: {tool_name}
Tool result: {str(tool_result)[:2500]}
"""
        try:
            response = await ollama_service.generate(
                prompt,
                model=context["settings"]["model"],
                temperature=context["settings"]["temperature"],
            )
        except Exception:
            if isinstance(tool_result, dict) and tool_result.get("error"):
                response = f"Checked '{task.get('title')}'. The {tool_name} tool could not complete: {tool_result['error']}."
            else:
                response = f"Completed '{task.get('title')}' using the {tool_name} tool."

        return {"tool": tool_name, "tool_result": tool_result, "response": response}
