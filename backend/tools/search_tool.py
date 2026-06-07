from typing import Any, Dict

from services.knowledge import search_knowledge
from services.memory_store import long_term_memories


class SearchTool:
    name = "search"
    description = "Search local knowledge and memory"

    async def execute(self, payload: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        db = context["db"]
        query = payload.get("query", "")
        memories = [
            memory
            for memory in long_term_memories(db, payload.get("limit", 5))
            if query.lower() in f"{memory['key']} {memory['value']}".lower()
        ]
        return {"query": query, "knowledge": search_knowledge(db, query), "memories": memories}
