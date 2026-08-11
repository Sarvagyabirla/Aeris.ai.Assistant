from enum import IntEnum
import logging

log = logging.getLogger(__name__)


class PermissionLevel(IntEnum):
    SAFE = 0
    LOW_RISK = 1
    MEDIUM_RISK = 2
    HIGH_RISK = 3
    SENSITIVE = 4


class PermissionRequiredError(Exception):
    """Raised when a tool requires explicit user confirmation."""
    def __init__(self, tool_name: str, level: PermissionLevel, details: str):
        self.tool_name = tool_name
        self.level = level
        self.details = details
        super().__init__(f"User confirmation required for {tool_name} (Level: {level.name}) - {details}")


class KillSwitch:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KillSwitch, cls).__new__(cls)
            cls._instance._activated = False
        return cls._instance

    def activate(self):
        log.warning("KILL SWITCH ACTIVATED. Halting computer control operations.")
        self._activated = True

    def reset(self):
        log.info("Kill switch reset.")
        self._activated = False

    def toggle(self):
        if self._activated:
            self.reset()
        else:
            self.activate()

    @property
    def is_active(self) -> bool:
        return self._activated


# Singleton kill switch
kill_switch = KillSwitch()


class PermissionManager:
    # A registry of temporarily granted permissions per conversation session
    # Format: { "tool_name": { "action_details": True } }
    # For now, we will handle confirmations by raising PermissionRequiredError 
    # if it's HIGH_RISK or SENSITIVE, and let the agent loop prompt the user.
    # The user's response will then allow the agent to retry with a confirmation flag.
    
    @staticmethod
    def check_execution_allowed(tool_name: str, permission_level: int, confirmed: bool = False, details: str = "") -> bool:
        """Check if execution is allowed based on security settings."""
        if kill_switch.is_active:
            log.warning(f"Execution blocked for {tool_name} by kill switch.")
            return False

        if permission_level >= PermissionLevel.HIGH_RISK and not confirmed:
            raise PermissionRequiredError(tool_name, PermissionLevel(permission_level), details)

        return True
