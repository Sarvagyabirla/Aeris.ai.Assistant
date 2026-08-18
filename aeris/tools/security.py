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
    """Raised when a tool requires explicit user confirmation before execution."""

    def __init__(self, tool_name: str, level: PermissionLevel, details: str):
        self.tool_name = tool_name
        self.level = level
        self.details = details
        super().__init__(
            f"User confirmation required for '{tool_name}' "
            f"(Level: {level.name}) — {details}"
        )


class KillSwitch:
    """
    Global emergency stop.

    When activated:
    - All computer-control tool executions are blocked.
    - UI shows STOPPED state.
    - New actions are rejected until reset() is called.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KillSwitch, cls).__new__(cls)
            cls._instance._activated = False
        return cls._instance

    def activate(self):
        log.warning("KILL SWITCH ACTIVATED — all computer control operations halted.")
        self._activated = True
        self._emit_event("KILL_SWITCH_ACTIVATED")

    def reset(self):
        log.info("Kill switch reset — computer control operations resumed.")
        self._activated = False
        self._emit_event("KILL_SWITCH_RESET")

    def toggle(self):
        if self._activated:
            self.reset()
        else:
            self.activate()
        self._emit_event("KILL_SWITCH_TOGGLED", active=self._activated)

    @property
    def is_active(self) -> bool:
        return self._activated

    def _emit_event(self, event_type: str, **kwargs):
        """Fire events without creating import cycles."""
        try:
            from aeris.core.events import event_manager
            import asyncio

            loop = None
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                pass

            if loop and loop.is_running():
                asyncio.ensure_future(
                    event_manager.emit(event_type, **kwargs), loop=loop
                )
            # If no loop is running (e.g. in tests), skip silently
        except Exception:
            pass  # Never let event emission crash security code


# Singleton kill switch
kill_switch = KillSwitch()


class PermissionManager:
    """
    Checks whether a tool execution is allowed given the current security state.

    Rules:
    - If kill switch is active → always block.
    - If permission_level >= HIGH_RISK and confirmed=False → raise PermissionRequiredError.
    - Otherwise → allow.
    """

    @staticmethod
    def check_execution_allowed(
        tool_name: str,
        permission_level: int,
        confirmed: bool = False,
        details: str = "",
    ) -> bool:
        """
        Returns True if execution is allowed.
        Raises PermissionRequiredError if explicit confirmation is required.
        Returns False if blocked by kill switch.
        """
        if kill_switch.is_active:
            log.warning(
                f"Execution blocked for '{tool_name}' — kill switch is active."
            )
            return False

        if permission_level >= PermissionLevel.HIGH_RISK and not confirmed:
            raise PermissionRequiredError(
                tool_name, PermissionLevel(permission_level), details
            )

        return True
