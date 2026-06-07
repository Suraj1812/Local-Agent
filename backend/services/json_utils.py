import json
from typing import Any


def loads(value: str, fallback: Any):
    try:
        return json.loads(value or "")
    except Exception:
        return fallback


def dumps(value: Any) -> str:
    return json.dumps(value if value is not None else {}, ensure_ascii=False)
