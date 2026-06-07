from typing import Any, Dict, List

from sqlalchemy.orm import Session

from services.memory_store import remember


class MemoryAgent:
    def store_goal(self, db: Session, goal: str, plan: List[Dict[str, Any]], results: List[str]) -> None:
        remember(
            db,
            "long_term",
            f"Completed goal: {goal[:80]}",
            "\n\n".join(results),
            {"plan": plan},
        )
