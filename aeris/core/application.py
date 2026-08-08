import asyncio
from typing import Optional

from aeris.core.conversation import Conversation
from aeris.core.context import ContextManager
from aeris.core.events import event_manager, Events
from aeris.ai.gemini_provider import GeminiProvider
from aeris.ai.types import AIRequest
from aeris.memory.interface import SessionMemory
from aeris.tools.registry import ToolRegistry
from aeris.logging.logger import log

class AerisCore:
    def __init__(self):
        self.conversation = Conversation()
        self.context_manager = ContextManager(self.conversation)
        self.provider = GeminiProvider()
        self.memory = SessionMemory()
        self.tool_registry = ToolRegistry()
        self.is_online = False

    async def initialize(self):
        """Startup sequence."""
        log.info("Initializing Aeris Core...")
        
        # Validate AI provider connection
        self.is_online = await self.provider.validate_connection()
        if self.is_online:
            log.info(f"Connected to AI Provider: {self.provider.get_model_information()}")
        else:
            log.error("Failed to connect to AI Provider. Running in degraded offline mode.")
            
        await event_manager.emit(Events.APPLICATION_STARTED)
        return self.is_online

    async def process_user_message(self, text: str) -> str:
        """Process a message from the user."""
        log.info("Processing user message.")
        
        # 1. Add to conversation
        self.conversation.add_message("user", text)
        await event_manager.emit(Events.USER_MESSAGE_RECEIVED, message=text)
        
        if not self.is_online:
            err = "Aeris is currently offline and cannot process requests."
            self.conversation.add_message("system", err)
            return err

        # 2. Get Context
        messages = self.context_manager.get_prompt_context()
        
        # 3. Create Request
        request = AIRequest(messages=messages)
        
        # 4. Send to Provider
        await event_manager.emit(Events.AI_REQUEST_STARTED)
        response = await self.provider.send_message(request)
        await event_manager.emit(Events.AI_RESPONSE_RECEIVED)
        
        # 5. Handle Response
        if response.is_success:
            self.conversation.add_message("assistant", response.content)
            return response.content
        else:
            err_msg = f"Error communicating with AI: {response.error}"
            self.conversation.add_message("system", err_msg)
            return err_msg
