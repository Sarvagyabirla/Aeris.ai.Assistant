
import os
import time
from aeris.tools.tool import Tool
from aeris.tools.security import PermissionLevel, PermissionManager
from aeris.tools.types import ToolResult
from aeris.config.settings import settings


class ScreenTool(Tool):
    name = "screen_control"
    description = "Control screen awareness: take screenshot, get dimensions."
    permission_level = PermissionLevel.SAFE
    parameters = {
        "action": {"type": "string", "enum": ["dimensions", "screenshot"]},
        "save_path": {
            "type": "string",
            "description": "Optional path to save screenshot",
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
                f"[DRY RUN] Would perform screen action {kwargs}",
            )

        try:
            import pyautogui
            from PIL import ImageGrab
            if action == "dimensions":
                width, height = pyautogui.size()
                return ToolResult(
                    True, self.name, action, f"Screen dimensions: {width}x{height}"
                )
            elif action == "screenshot":
                save_path = kwargs.get("save_path")
                # Do not automatically upload anywhere. Just save locally.
                if not save_path:
                    # Save to a default temp location in allowed paths
                    save_path = os.path.join(
                        settings.allowed_paths[0], f"screenshot_{int(time.time())}.png"
                    )

                # Check allowed path
                allowed = False
                for p in settings.allowed_paths:
                    if save_path.startswith(p):
                        allowed = True
                        break
                if not allowed:
                    return ToolResult(
                        False,
                        self.name,
                        action,
                        "",
                        error=f"Cannot save screenshot outside allowed paths: {save_path}",
                    )

                screenshot = ImageGrab.grab()
                screenshot.save(save_path)
                return ToolResult(
                    True, self.name, action, f"Screenshot saved to {save_path}"
                )
            else:
                return ToolResult(
                    False, self.name, str(action), "", error=f"Unknown action {action}"
                )
        except Exception as e:
            return ToolResult(False, self.name, str(action), "", error=str(e))
