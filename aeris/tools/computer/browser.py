import webbrowser
from urllib.parse import urlparse
from aeris.tools.tool import Tool
from aeris.tools.security import PermissionLevel, PermissionManager
from aeris.tools.types import ToolResult
from aeris.config.settings import settings


class BrowserTool(Tool):
    name = "browser_control"
    description = "Control browser: open URLs safely."
    permission_level = PermissionLevel.MEDIUM_RISK
    parameters = {
        "action": {"type": "string", "enum": ["open"]},
        "url": {"type": "string"},
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

        if action == "open":
            url = kwargs.get("url", "")

            # Basic URL validation should happen before dry run
            parsed = urlparse(url)
            if not parsed.scheme or parsed.scheme not in ["http", "https"]:
                return ToolResult(
                    False, self.name, action, "", error="Invalid or unsafe URL scheme"
                )

        if settings.dry_run:
            return ToolResult(
                True,
                self.name,
                action,
                f"[DRY RUN] Would perform browser action {kwargs}",
            )

        try:
            if action == "open":
                url = kwargs.get("url", "")
                webbrowser.open(url)
                return ToolResult(True, self.name, action, f"Opened URL: {url}")
            else:
                return ToolResult(
                    False, self.name, str(action), "", error=f"Unknown action {action}"
                )
        except Exception as e:
            return ToolResult(False, self.name, str(action), "", error=str(e))
