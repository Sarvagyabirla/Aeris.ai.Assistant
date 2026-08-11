from typing import Callable, Dict, List, Any
import asyncio


class EventManager:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    async def emit(self, event_type: str, **kwargs: Any):
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                if asyncio.iscoroutinefunction(callback):
                    await callback(**kwargs)
                else:
                    callback(**kwargs)


# Singleton event manager
event_manager = EventManager()


# Predefined Event Types
class Events:
    APPLICATION_STARTED = "APPLICATION_STARTED"
    USER_MESSAGE_RECEIVED = "USER_MESSAGE_RECEIVED"
    AI_REQUEST_STARTED = "AI_REQUEST_STARTED"
    AI_RESPONSE_RECEIVED = "AI_RESPONSE_RECEIVED"
    TOOL_EXECUTION_STARTED = "TOOL_EXECUTION_STARTED"
    TOOL_EXECUTION_COMPLETED = "TOOL_EXECUTION_COMPLETED"
    TOOL_EXECUTION_FAILED = "TOOL_EXECUTION_FAILED"
    SYSTEM_METRICS_UPDATED = "SYSTEM_METRICS_UPDATED"
    PERMISSION_STATE_CHANGED = "PERMISSION_STATE_CHANGED"
    KILL_SWITCH_TOGGLED = "KILL_SWITCH_TOGGLED"
    TASK_STARTED = "TASK_STARTED"
    TASK_COMPLETED = "TASK_COMPLETED"
    TASK_FAILED = "TASK_FAILED"
    ERROR_OCCURRED = "ERROR_OCCURRED"
