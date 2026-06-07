from typing import Any, Dict, List

from services.ollama import ollama_service


def fallback_plan(goal: str) -> List[Dict[str, Any]]:
    lower = goal.lower()
    if "code" in lower or "build" in lower or "login" in lower:
        return [
            {"id": 1, "title": "Analyze the software request", "priority": "high"},
            {"id": 2, "title": "Generate the UI and data flow", "priority": "high"},
            {"id": 3, "title": "Add validation and edge cases", "priority": "medium"},
            {"id": 4, "title": "Review and return final code", "priority": "medium"},
        ]
    if "research" in lower or "summarize" in lower:
        return [
            {"id": 1, "title": "Define the research scope", "priority": "high"},
            {"id": 2, "title": "Search local knowledge", "priority": "high"},
            {"id": 3, "title": "Synthesize findings", "priority": "medium"},
            {"id": 4, "title": "Return summary", "priority": "medium"},
        ]
    return [
        {"id": 1, "title": "Understand the goal", "priority": "high"},
        {"id": 2, "title": "Create an ordered task list", "priority": "high"},
        {"id": 3, "title": "Execute tasks with tools", "priority": "medium"},
        {"id": 4, "title": "Evaluate and respond", "priority": "medium"},
    ]


def normalize_plan(plan: Any, fallback: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not isinstance(plan, list):
        return fallback

    normalized: List[Dict[str, Any]] = []
    for index, raw_task in enumerate(plan[:6], start=1):
        if not isinstance(raw_task, dict):
            continue
        title = " ".join(str(raw_task.get("title", "")).strip().split())
        if len(title) < 4:
            continue
        priority = str(raw_task.get("priority", "medium")).lower().strip()
        if priority not in {"high", "medium", "low"}:
            priority = "medium"
        normalized.append({"id": index, "title": title[:140], "priority": priority})

    return normalized if len(normalized) >= 3 else fallback


class PlannerAgent:
    async def plan(self, goal: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        fallback = fallback_plan(goal)
        prompt = f"""
You are Planner Agent in a local agentic AI system.
Return only JSON, no prose. Create 3 to 6 tasks with id, title, priority.

Goal:
{goal}

Relevant memory:
{context.get("memories", [])}
"""
        result = await ollama_service.generate_json(
            prompt,
            fallback=fallback,
            model=context["settings"]["model"],
            temperature=context["settings"]["temperature"],
        )
        return normalize_plan(result, fallback)
