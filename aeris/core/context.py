from typing import List
from aeris.core.conversation import Conversation, Message

class ContextManager:
    """Manages context selection for the AI provider."""
    
    def __init__(self, conversation: Conversation):
        self.conversation = conversation
        
    def get_prompt_context(self, system_prompt: str = "") -> List[Message]:
        """
        Retrieves the messages that should be sent to the API.
        Currently simple, but extensible for summarizing/trimming later.
        """
        messages = self.conversation.get_messages()
        
        # In the future, we can trim or summarize here before returning.
        
        # If there's a system prompt, we could prepend it, but usually the 
        # provider handles the system instruction specifically. 
        # This just returns the conversation history.
        return messages
