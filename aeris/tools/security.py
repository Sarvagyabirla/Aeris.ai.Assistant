from enum import IntEnum
import logging

log = logging.getLogger(__name__)


class PermissionLevel(IntEnum):
    SAFE = 0
    LOW_RISK = 1
    MEDIUM_RISK = 2
    HIGH_RISK = 3


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

    @property
    def is_active(self) -> bool:
        return self._activated


# Singleton kill switch
kill_switch = KillSwitch()


class PermissionManager:
    @staticmethod
    def check_execution_allowed(tool_name: str, permission_level: int) -> bool:
        """Check if execution is allowed based on security settings."""
        if kill_switch.is_active:
            log.warning(f"Execution blocked for {tool_name} by kill switch.")
            return False

        # In a real system, HIGH_RISK would block and wait for UI confirmation.
        # For Part 2 foundation, we assume the caller handles the UI confirmation
        # before passing to execution, or we block it if it's high risk and not confirmed.
        # We will return True if allowed, False if it needs explicit override (not implemented yet).

        return True
