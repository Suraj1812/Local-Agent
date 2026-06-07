from typing import Dict

from tools.calculator import CalculatorTool
from tools.code_tool import CodeTool
from tools.file_tool import FileTool
from tools.search_tool import SearchTool


class ToolRegistry:
    def __init__(self):
        self.tools = {}
        self.register(CalculatorTool())
        self.register(FileTool())
        self.register(CodeTool())
        self.register(SearchTool())

    def register(self, tool):
        self.tools[tool.name] = tool

    def list(self, enabled: Dict[str, bool]):
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "enabled": enabled.get(tool.name, True),
            }
            for tool in self.tools.values()
        ]

    def get(self, name: str, enabled: Dict[str, bool]):
        if enabled.get(name, True) is False:
            raise ValueError(f"{name} tool is disabled")
        return self.tools[name]


tool_registry = ToolRegistry()
