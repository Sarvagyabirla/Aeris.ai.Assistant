from abc import ABC, abstractmethod
from typing import Any, Dict

class Tool(ABC):
    """Base class for all Aeris tools."""
    
    name: str = "UnknownTool"
    description: str = "No description provided."
    parameters: Dict[str, Any] = {}
    permission_level: int = 0  # 0: Safe, 1: Requires confirmation, 2: Dangerous

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool's core logic."""
        pass

    def validate(self, **kwargs) -> bool:
        """Validate input parameters before execution."""
        # Simple base validation could check against self.parameters schema
        return True
