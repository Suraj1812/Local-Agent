from pathlib import Path
from typing import Any, Dict

from services.settings import get_settings

MAX_FILE_BYTES = 1_000_000


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
            if not path.is_file():
                raise ValueError("File does not exist")
            if path.stat().st_size > MAX_FILE_BYTES:
                raise ValueError("File is too large to read")
            return {"path": str(path), "content": path.read_text(encoding="utf-8")}

        if operation == "write":
            content = str(payload.get("content", ""))
            if len(content.encode("utf-8")) > MAX_FILE_BYTES:
                raise ValueError("File content is too large")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return {"path": str(path), "status": "written"}

        if operation == "edit":
            if not path.is_file():
                raise ValueError("File does not exist")
            if path.stat().st_size > MAX_FILE_BYTES:
                raise ValueError("File is too large to edit")
            search = str(payload.get("search", ""))
            replace = str(payload.get("replace", ""))
            if not search:
                raise ValueError("Search text is required")
            current = path.read_text(encoding="utf-8")
            if search not in current:
                raise ValueError("Search text was not found")
            path.write_text(current.replace(search, replace), encoding="utf-8")
            return {"path": str(path), "status": "edited"}

        raise ValueError("Unsupported file operation")
