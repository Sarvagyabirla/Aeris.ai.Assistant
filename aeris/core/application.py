
from aeris.core.conversation import Conversation
from aeris.core.context import ContextManager
from aeris.core.events import event_manager, Events
from aeris.ai.gemini_provider import GeminiProvider
from aeris.memory.interface import SessionMemory
from aeris.tools.registry import ToolRegistry
from aeris.app_logger.logger import log
from aeris.tools.computer import get_all_computer_tools


class AerisCore:
    def __init__(self):
        self.conversation = Conversation()
        self.context_manager = ContextManager(self.conversation)
        self.provider = GeminiProvider()
        self.memory = SessionMemory()
        self.tool_registry = ToolRegistry()
        self.is_online = False
        self.agent = None

    async def initialize(self):
        """Startup sequence."""
        log.info("Initializing Aeris Core...")

        # Initialize Agent with current provider
        from aeris.core.agent import AerisAgent

        self.agent = AerisAgent(
            self.provider, self.conversation, self.context_manager, self.tool_registry
        )

        # Register tools
        for tool in get_all_computer_tools():
            self.tool_registry.register(tool)
        log.info(f"Registered {len(self.tool_registry.get_all_tools())} tools.")

        # Validate AI provider connection
        self.is_online = await self.provider.validate_connection()
        if self.is_online:
            log.info(
                f"Connected to AI Provider: {self.provider.get_model_information()}"
            )
        else:
            log.error(
                "Failed to connect to AI Provider. Running in degraded offline mode."
            )

        await event_manager.emit(Events.APPLICATION_STARTED)
        return self.is_online

    async def process_user_message(self, text: str) -> str:
        """Process a message from the user."""
        log.info("Processing user message.")

        if not self.is_online:
            err = "Aeris is currently offline and cannot process requests."
            self.conversation.add_message("system", content=err)
            return err

        return await self.agent.run(text)
