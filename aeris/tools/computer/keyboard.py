
from aeris.tools.tool import Tool
from aeris.tools.security import PermissionLevel, PermissionManager
from aeris.tools.types import ToolResult
from aeris.config.settings import settings


class KeyboardTool(Tool):
    name = "keyboard_control"
    description = "Control the keyboard: type text, press keys."
    permission_level = PermissionLevel.LOW_RISK
    parameters = {
        "action": {"type": "string", "enum": ["type", "press", "hotkey"]},
        "text": {"type": "string", "description": "Text to type (for 'type' action)"},
        "keys": {"type": "array", "items": {"type": "string"}, "description": "Key names to press (for 'press'/'hotkey' actions, e.g. ['ctrl', 'c'])"},
    }
    required_params = ["action"]  # text/keys are action-specific

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

        # Don't log sensitive keys like passwords if we had them,
        # for now we assume general logging is handled at a higher level,
        # but we avoid logging the exact text in the result if possible.
        # But wait, result needs to be returned to AI. The AI generated it anyway.

        if settings.dry_run:
            return ToolResult(
                True,
                self.name,
                action,
                f"[DRY RUN] Would perform keyboard action {kwargs}",
            )

        try:
            import pyautogui
            if action == "type":
                text = kwargs.get("text", "")
                pyautogui.write(text, interval=0.01)
                return ToolResult(
                    True, self.name, action, f"Typed text length {len(text)}"
                )
            elif action == "press":
                keys = kwargs.get("keys", [])
                if keys:
                    pyautogui.press(keys)
                return ToolResult(True, self.name, action, f"Pressed keys {keys}")
            elif action == "hotkey":
                keys = kwargs.get("keys", [])
                if keys:
                    pyautogui.hotkey(*keys)
                return ToolResult(True, self.name, action, f"Pressed hotkey {keys}")
            else:
                return ToolResult(
                    False, self.name, str(action), "", error=f"Unknown action {action}"
                )
        except Exception as e:
            return ToolResult(False, self.name, str(action), "", error=str(e))
