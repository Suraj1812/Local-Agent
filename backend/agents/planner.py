from typing import Any, Dict, List


def default_plan(goal: str) -> List[Dict[str, Any]]:
    lower = goal.lower()
    if any(token in lower for token in ("calculate", "math", "percent", "ratio", "total", "+", "-", "*", "/", "%")):
        return [
            {"id": 1, "title": "Calculate the requested value", "priority": "high"},
            {"id": 2, "title": "Explain the answer clearly", "priority": "medium"},
        ]
    if "code" in lower or "build" in lower or "login" in lower:
        return [
            {"id": 1, "title": "Understand the software request", "priority": "high"},
            {"id": 2, "title": "Generate the best practical answer", "priority": "high"},
        ]
    if "knowledge" in lower or "uploaded" in lower or "document" in lower or "memory" in lower:
        return [
            {"id": 1, "title": "Search available local context", "priority": "high"},
            {"id": 2, "title": "Answer from the relevant evidence", "priority": "high"},
        ]
    return [
        {"id": 1, "title": "Understand the question", "priority": "high"},
        {"id": 2, "title": "Answer with the local model", "priority": "high"},
    ]


def normalize_plan(plan: Any, default_tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not isinstance(plan, list):
        return default_tasks

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

    return normalized if len(normalized) >= 3 else default_tasks


class PlannerAgent:
    async def plan(self, goal: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        return default_plan(goal)
