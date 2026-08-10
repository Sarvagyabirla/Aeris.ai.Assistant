from typing import List
from aeris.core.conversation import Conversation, Message
from aeris.memory.persistent import PersistentMemory


class ContextManager:
    """Manages context selection for the AI provider."""

    def __init__(self, conversation: Conversation):
        self.conversation = conversation
        self.persistent_memory = PersistentMemory()

    def get_prompt_context(self) -> List[Message]:
        """
        Retrieves the messages that should be sent to the API.
        """
        return self.conversation.get_messages()

    def get_system_instruction(self) -> str:
        """Constructs the system instruction including persistent memory."""
        base_instruction = "You are Aeris, a modular, autonomous AI assistant. You have access to tools to interact with the computer."
        memory_str = self.persistent_memory.get_context_string()
        if memory_str:
            base_instruction += f"\n\n[MEMORY CONTEXT]\n{memory_str}"
        return base_instruction
