from abc import ABC, abstractmethod
from typing import AsyncGenerator
from aeris.ai.types import AIRequest, AIResponse


class AIProvider(ABC):
    """Abstract base class for AI Providers."""

    @abstractmethod
    async def send_message(self, request: AIRequest) -> AIResponse:
        """Send a message to the AI model and get a complete response."""

    @abstractmethod
    async def stream_message(
        self, request: AIRequest
    ) -> AsyncGenerator[AIResponse, None]:
        """Stream a response from the AI model."""

    @abstractmethod
    async def validate_connection(self) -> bool:
        """Check if the provider is correctly configured and reachable."""

    @abstractmethod
    def get_model_information(self) -> str:
        """Return information about the currently configured model."""
