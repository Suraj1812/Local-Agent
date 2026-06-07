from pathlib import Path
from typing import Any, Dict

from services.settings import get_settings


class FileTool:
    name = "file"
    description = "Read, write, and edit files inside the workspace"

    def _safe_path(self, target: str) -> Path:
        root = Path(get_settings().workspace_root).resolve()
        path = (root / target).resolve()
        if root not in path.parents and path != root:
            raise ValueError("File access is limited to the workspace")
        return path

    async def execute(self, payload: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        operation = payload.get("operation", "read")
        path = self._safe_path(payload.get("path", "."))

        if operation == "read":
            return {"path": str(path), "content": path.read_text(encoding="utf-8")}

        if operation == "write":
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(payload.get("content", ""), encoding="utf-8")
            return {"path": str(path), "status": "written"}

        if operation == "edit":
            current = path.read_text(encoding="utf-8")
            path.write_text(current.replace(payload.get("search", ""), payload.get("replace", "")), encoding="utf-8")
            return {"path": str(path), "status": "edited"}

        raise ValueError("Unsupported file operation")
