import time
from typing import List, Dict, Any, Optional


class Message:
    """Represents a single message in a conversation."""

    def __init__(
        self,
        role: str,
        content: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        image: Optional[Any] = None,
        tool_calls: Optional[List[Any]] = None,
        tool_responses: Optional[List[Any]] = None,
    ):
        self.role = role
        self.content = content
        self.timestamp = time.time()
        self.metadata = metadata or {}
        self.image = image
        self.tool_calls = tool_calls or []
        self.tool_responses = tool_responses or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "has_image": self.image is not None,
            "tool_calls_count": len(self.tool_calls),
            "tool_responses_count": len(self.tool_responses),
        }


class Conversation:
    """Manages the history of messages for a session."""

    def __init__(self):
        self._messages: List[Message] = []

    def add_message(
        self,
        role: str,
        content: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        image: Optional[Any] = None,
        tool_calls: Optional[List[Any]] = None,
        tool_responses: Optional[List[Any]] = None,
    ) -> Message:
        msg = Message(
            role=role,
            content=content,
            metadata=metadata,
            image=image,
            tool_calls=tool_calls,
            tool_responses=tool_responses,
        )
        self._messages.append(msg)
        return msg

    def get_messages(self) -> List[Message]:
        return self._messages.copy()

    def clear(self):
        self._messages.clear()
