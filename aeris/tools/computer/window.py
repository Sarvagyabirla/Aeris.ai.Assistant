
from aeris.tools.tool import Tool
from aeris.tools.security import PermissionLevel, PermissionManager
from aeris.tools.types import ToolResult
from aeris.config.settings import settings


class WindowTool(Tool):
    name = "window_control"
    description = "Control windows: list, focus, minimize, maximize, close."
    permission_level = PermissionLevel.MEDIUM_RISK
    parameters = {
        "action": {
            "type": "string",
            "enum": ["list", "focus", "minimize", "maximize", "restore", "close"],
        },
        "title": {
            "type": "string",
            "description": "Title (or partial title) of the window",
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
        title = kwargs.get("title", "")

        if settings.dry_run:
            return ToolResult(
                True,
                self.name,
                action,
                f"[DRY RUN] Would perform window action {kwargs}",
            )

        try:
            import pygetwindow as gw
            if action == "list":
                windows = gw.getAllTitles()
                # Filter empty titles
                windows = [w for w in windows if w.strip()]
                return ToolResult(
                    True, self.name, action, f"Visible windows: {', '.join(windows)}"
                )

            if not title:
                return ToolResult(
                    False, self.name, action, "", error="title required for this action"
                )

            windows = gw.getWindowsWithTitle(title)
            if not windows:
                return ToolResult(
                    False,
                    self.name,
                    action,
                    "",
                    error=f"No window found matching '{title}'",
                )

            window = windows[0]

            if action == "focus":
                window.activate()
                return ToolResult(
                    True, self.name, action, f"Focused window '{window.title}'"
                )
            elif action == "minimize":
                window.minimize()
                return ToolResult(
                    True, self.name, action, f"Minimized window '{window.title}'"
                )
            elif action == "maximize":
                window.maximize()
                return ToolResult(
                    True, self.name, action, f"Maximized window '{window.title}'"
                )
            elif action == "restore":
                window.restore()
                return ToolResult(
                    True, self.name, action, f"Restored window '{window.title}'"
                )
            elif action == "close":
                window.close()
                return ToolResult(
                    True, self.name, action, f"Closed window '{window.title}'"
                )
            else:
                return ToolResult(
                    False, self.name, str(action), "", error=f"Unknown action {action}"
                )
        except Exception as e:
            # Note: pygetwindow.activate() on Windows can throw PyGetWindowException if it fails
            return ToolResult(False, self.name, str(action), "", error=str(e))
