from typing import List, Dict, Any, Callable
from aeris.core.events import event_manager, Events

class UIState:
    def __init__(self):
        self.core_status = "OFFLINE"
        self.current_task = "Ready"
        self.ai_activity_feed: List[str] = []
        self.system_metrics = {"cpu": 0.0, "ram": 0.0, "disk": 0.0, "battery": 100.0}
        self.kill_switch_active = False
        self.dry_run = False
        
        self._listeners: List[Callable] = []
        
        # Subscribe to events
        event_manager.subscribe(Events.APPLICATION_STARTED, self._on_app_started)
        event_manager.subscribe(Events.AI_REQUEST_STARTED, self._on_ai_thinking)
        event_manager.subscribe(Events.AI_RESPONSE_RECEIVED, self._on_ai_idle)
        event_manager.subscribe(Events.TOOL_EXECUTION_STARTED, self._on_tool_started)
        event_manager.subscribe(Events.TOOL_EXECUTION_COMPLETED, self._on_tool_completed)
        event_manager.subscribe(Events.TOOL_EXECUTION_FAILED, self._on_tool_failed)
        event_manager.subscribe(Events.PERMISSION_STATE_CHANGED, self._on_permission)
        event_manager.subscribe(Events.SYSTEM_METRICS_UPDATED, self._on_metrics)
        event_manager.subscribe(Events.ERROR_OCCURRED, self._on_error)

    def _notify(self):
        for listener in self._listeners:
            listener()
            
    def subscribe(self, callback: Callable):
        if callback not in self._listeners:
            self._listeners.append(callback)

    def _on_app_started(self, **kwargs):
        self.core_status = "IDLE"
        self.current_task = "Ready"
        self.add_activity("Aeris Application Started")
        self._notify()
        
    def _on_ai_thinking(self, **kwargs):
        self.core_status = "THINKING"
        self.current_task = "Thinking..."
        self.add_activity("AI is thinking...")
        self._notify()

    def _on_ai_idle(self, **kwargs):
        if self.core_status not in ["WAITING_FOR_PERMISSION"]:
            self.core_status = "IDLE"
            self.current_task = "Waiting for input"
        self.add_activity("AI response received.")
        self._notify()

    def _on_tool_started(self, tool_name: str, args: Dict, **kwargs):
        self.core_status = "EXECUTING"
        self.current_task = f"Executing {tool_name}"
        self.add_activity(f"Tool Started: {tool_name}")
        self._notify()
        
    def _on_tool_completed(self, tool_name: str, result: Any, **kwargs):
        self.core_status = "SUCCESS"
        self.current_task = f"Completed {tool_name}"
        self.add_activity(f"Tool Completed: {tool_name}")
        self._notify()
        
    def _on_tool_failed(self, tool_name: str, error: str, **kwargs):
        self.core_status = "ERROR"
        self.current_task = f"Failed {tool_name}"
        self.add_activity(f"Tool Failed: {tool_name} - {error}")
        self._notify()

    def _on_permission(self, tool_name: str, state: str, details: str, **kwargs):
        self.core_status = "WAITING_FOR_PERMISSION"
        self.current_task = f"Permission required for {tool_name}"
        self.add_activity(f"Permission Request: {tool_name} - {details}")
        self._notify()
        
    def _on_metrics(self, cpu: float, ram: float, disk: float, battery: float, **kwargs):
        self.system_metrics = {"cpu": cpu, "ram": ram, "disk": disk, "battery": battery}
        self._notify()

    def _on_error(self, error: str, **kwargs):
        self.core_status = "ERROR"
        self.add_activity(f"System Error: {error}")
        self._notify()

    def add_activity(self, msg: str):
        import time
        t = time.strftime("%H:%M:%S")
        self.ai_activity_feed.append(f"[{t}] {msg}")
        if len(self.ai_activity_feed) > 50:
            self.ai_activity_feed.pop(0)

# Singleton state instance
ui_state = UIState()
