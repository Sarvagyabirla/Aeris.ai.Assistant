from dataclasses import dataclass
from typing import Optional


@dataclass
class ToolResult:
    """Standardized result returned by all tools."""

    success: bool
    tool: str
    action: str
    result: str
    error: Optional[str] = None
    duration: float = 0.0

    def to_dict(self):
        return {
            "success": self.success,
            "tool": self.tool,
            "action": self.action,
            "result": self.result,
            "error": self.error,
            "duration": self.duration,
        }
