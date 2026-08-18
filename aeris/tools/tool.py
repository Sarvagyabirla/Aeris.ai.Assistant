from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class Tool(ABC):
    """
    Base class for all Aeris tools.

    Class attributes to define:
        name: str              — Unique tool identifier (used as function name in API)
        description: str       — Human and AI-readable description of what the tool does
        parameters: dict       — OpenAPI-style property schema for each parameter
        required_params: list  — Names of parameters that are REQUIRED (others are optional)
        permission_level: int  — PermissionLevel value (SAFE=0 up to SENSITIVE=4)
    """

    name: str = "UnknownTool"
    description: str = "No description provided."
    parameters: Dict[str, Any] = {}
    required_params: List[str] = []   # Empty = no parameters required (all optional)
    permission_level: int = 0

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool's core logic."""

    def validate(self, **kwargs) -> bool:
        """Validate input parameters before execution."""
        return True
