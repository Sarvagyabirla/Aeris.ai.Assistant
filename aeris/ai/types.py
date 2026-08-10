from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
from aeris.core.conversation import Message


@dataclass
class AIRequest:
    messages: List[Message]
    system_instruction: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    tools: List[Any] = field(default_factory=list)


@dataclass
class AIResponse:
    content: str
    tool_calls: List[Any] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    is_success: bool = True
