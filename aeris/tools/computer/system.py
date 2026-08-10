import pyautogui
from aeris.tools.tool import Tool
from aeris.tools.security import PermissionLevel, PermissionManager
from aeris.tools.types import ToolResult
from aeris.config.settings import settings


class SystemTool(Tool):
    name = "system_control"
    description = "Control basic system settings like volume."
    permission_level = PermissionLevel.SAFE
    parameters = {
        "action": {
            "type": "string",
            "enum": ["volume_up", "volume_down", "volume_mute"],
        },
        "amount": {
            "type": "integer",
            "description": "Number of times to press the volume key",
        },
    }

    async def execute(self, **kwargs) -> ToolResult:
        if not PermissionManager.check_execution_allowed(
            self.name, self.permission_level
        ):
            return ToolResult(
                False,
                self.name,
                str(kwargs.get("action")),
                "Blocked by security manager",
                error="Blocked",
            )

        action = kwargs.get("action")

        if settings.dry_run:
            return ToolResult(
                True,
                self.name,
                action,
                f"[DRY RUN] Would perform system action {kwargs}",
            )

        try:
            if action in ["volume_up", "volume_down", "volume_mute"]:
                amount = kwargs.get("amount", 1)

                # Mute is usually a toggle, so amount doesn't make sense > 1
                if action == "volume_mute":
                    amount = 1

                for _ in range(amount):
                    pyautogui.press(action.replace("_", ""))
                return ToolResult(
                    True,
                    self.name,
                    action,
                    f"System volume action {action} executed {amount} times",
                )
            else:
                return ToolResult(
                    False, self.name, str(action), "", error=f"Unknown action {action}"
                )
        except Exception as e:
            return ToolResult(False, self.name, str(action), "", error=str(e))
