from typing import Dict, Optional, List
from aeris.tools.tool import Tool

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        """Register a new tool."""
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[Tool]:
        """Retrieve a tool by name."""
        return self._tools.get(name)

    def get_all_tools(self) -> List[Tool]:
        """Return a list of all registered tools."""
        return list(self._tools.values())
        
    def get_schemas(self) -> List[Dict]:
        """Get the schemas of all tools for the AI provider."""
        schemas = []
        for tool in self._tools.values():
            schemas.append({
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            })
        return schemas
