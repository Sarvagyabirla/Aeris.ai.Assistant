import pyperclip
from aeris.tools.tool import Tool
from aeris.tools.security import PermissionLevel, PermissionManager
from aeris.tools.types import ToolResult
from aeris.config.settings import settings


class ClipboardTool(Tool):
    name = "clipboard_control"
    description = "Control the clipboard: read, write, clear."
    permission_level = PermissionLevel.LOW_RISK
    parameters = {
        "action": {"type": "string", "enum": ["read", "write", "clear"]},
        "text": {"type": "string"},
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
                f"[DRY RUN] Would perform clipboard action {kwargs}",
            )

        try:
            if action == "read":
                content = pyperclip.paste()
                return ToolResult(
                    True,
                    self.name,
                    action,
                    f"Clipboard content read successfully.",
                    result=content,
                )
            elif action == "write":
                text = kwargs.get("text", "")
                pyperclip.copy(text)
                return ToolResult(True, self.name, action, "Text written to clipboard.")
            elif action == "clear":
                pyperclip.copy("")
                return ToolResult(True, self.name, action, "Clipboard cleared.")
            else:
                return ToolResult(
                    False, self.name, str(action), "", error=f"Unknown action {action}"
                )
        except Exception as e:
            return ToolResult(False, self.name, str(action), "", error=str(e))
