import json
import re
from typing import Any, List, Optional


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def title_from_goal(goal: str) -> str:
    clean = compact(goal)
    if not clean:
        return "New conversation"
    return clean[:57] + "..." if len(clean) > 60 else clean


def extract_json(text: str) -> Optional[Any]:
    try:
        return json.loads(text)
    except Exception:
        match = re.search(r"(\[[\s\S]*\]|\{[\s\S]*\})", text or "")
        if not match:
            return None
        try:
            return json.loads(match.group(1))
        except Exception:
            return None


def chunk_text(text: str, size: int = 1200, overlap: int = 150) -> List[str]:
    clean = compact(text)
    chunks = []
    start = 0
    while start < len(clean):
        end = min(start + size, len(clean))
        chunks.append(clean[start:end])
        if end == len(clean):
            break
        start = max(0, end - overlap)
    return chunks


def tokenize(text: str) -> List[str]:
    return [token for token in re.sub(r"[^a-z0-9\s]", " ", (text or "").lower()).split() if len(token) > 2]
