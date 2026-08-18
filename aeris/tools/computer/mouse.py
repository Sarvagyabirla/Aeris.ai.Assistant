
from aeris.tools.tool import Tool
from aeris.tools.security import PermissionLevel, PermissionManager
from aeris.tools.types import ToolResult
from aeris.config.settings import settings


class MouseTool(Tool):
    name = "mouse_control"
    description = "Control the mouse: move, click, scroll."
    permission_level = PermissionLevel.LOW_RISK
    parameters = {
        "action": {"type": "string", "enum": ["move", "click", "double_click", "right_click", "scroll"]},
        "x": {"type": "integer", "description": "X coordinate (for move/click)"},
        "y": {"type": "integer", "description": "Y coordinate (for move/click)"},
        "button": {"type": "string", "enum": ["left", "right", "middle"], "description": "Mouse button (default: left)"},
        "clicks": {"type": "integer", "description": "Number of clicks (default: 1)"},
        "amount": {"type": "integer", "description": "Scroll amount (positive = up, negative = down)"},
    }
    required_params = ["action"]  # x, y, button, clicks, amount are optional

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
                f"[DRY RUN] Would perform mouse action {kwargs}",
            )

        try:
            import pyautogui
            # Important: pyautogui has a failsafe if you move the mouse to a corner,
            # we respect that as an extra safety measure.
            if action == "move":
                x = kwargs.get("x", 0)
                y = kwargs.get("y", 0)
                pyautogui.moveTo(x, y, duration=0.2)
                return ToolResult(True, self.name, action, f"Moved to {x}, {y}")
            elif action == "click":
                button = kwargs.get("button", "left")
                clicks = kwargs.get("clicks", 1)
                pyautogui.click(button=button, clicks=clicks)
                return ToolResult(
                    True, self.name, action, f"Clicked {button} {clicks} times"
                )
            elif action == "scroll":
                amount = kwargs.get("amount", 0)
                pyautogui.scroll(amount)
                return ToolResult(True, self.name, action, f"Scrolled {amount}")
            else:
                return ToolResult(
                    False, self.name, str(action), "", error=f"Unknown action {action}"
                )
        except Exception as e:
            return ToolResult(False, self.name, str(action), "", error=str(e))
