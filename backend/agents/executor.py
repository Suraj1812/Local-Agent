from typing import Any, Dict

from services.ollama import ollama_service
from tools.registry import tool_registry


def select_tool(task: Dict[str, Any]) -> str:
    text = task.get("title", "").lower()
    if "search" in text or "research" in text or "knowledge" in text:
        return "search"
    if "calculate" in text or "math" in text or "stat" in text:
        return "calculator"
    if "code" in text or "ui" in text or "generate" in text or "validation" in text:
        return "code"
    return "search"


class ExecutorAgent:
    async def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        tool_name = select_tool(task)
        tool = tool_registry.get(tool_name, context["settings"]["tools_enabled"])

        if tool_name == "calculator":
            tool_result = await tool.execute({"expression": context["goal"]}, context)
        elif tool_name == "code":
            tool_result = await tool.execute({"operation": "generate", "task": task.get("title")}, context)
        else:
            tool_result = await tool.execute({"query": context["goal"], "limit": 5}, context)

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
            response = f"Completed '{task.get('title')}' using the {tool_name} tool."

        return {"tool": tool_name, "tool_result": tool_result, "response": response}
