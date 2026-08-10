import psutil
import subprocess
import os
from aeris.tools.tool import Tool
from aeris.tools.security import PermissionLevel, PermissionManager
from aeris.tools.types import ToolResult
from aeris.config.settings import settings


class AppTool(Tool):
    name = "app_control"
    description = "Control applications: detect, launch, close, check status."
    permission_level = PermissionLevel.MEDIUM_RISK
    parameters = {
        "action": {"type": "string", "enum": ["launch", "close", "status", "list"]},
        "app_name": {
            "type": "string",
            "description": "Name of the executable (e.g. notepad.exe)",
        },
        "path": {
            "type": "string",
            "description": "Full path to the executable to launch",
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
                True, self.name, action, f"[DRY RUN] Would perform app action {kwargs}"
            )

        try:
            if action == "list":
                # Returns a limited list to avoid massive context
                apps = []
                for p in psutil.process_iter(["name"]):
                    try:
                        apps.append(p.info["name"])
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                # Deduplicate and sort
                apps = sorted(list(set(apps)))
                # Limit output size to prevent context overflow
                if len(apps) > 100:
                    apps = apps[:100] + ["... (truncated)"]
                return ToolResult(
                    True, self.name, action, f"Running apps: {', '.join(apps)}"
                )

            elif action == "status":
                app_name = kwargs.get("app_name", "").lower()
                if not app_name:
                    return ToolResult(
                        False, self.name, action, "", error="app_name required"
                    )

                found = False
                for p in psutil.process_iter(["name"]):
                    try:
                        if p.info["name"] and app_name in p.info["name"].lower():
                            found = True
                            break
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                return ToolResult(
                    True, self.name, action, f"App '{app_name}' running: {found}"
                )

            elif action == "close":
                app_name = kwargs.get("app_name", "").lower()
                if not app_name:
                    return ToolResult(
                        False, self.name, action, "", error="app_name required"
                    )

                closed_count = 0
                for p in psutil.process_iter(["name"]):
                    try:
                        if p.info["name"] and app_name in p.info["name"].lower():
                            p.terminate()
                            closed_count += 1
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                return ToolResult(
                    True,
                    self.name,
                    action,
                    f"Closed {closed_count} instances of '{app_name}'",
                )

            elif action == "launch":
                path = kwargs.get("path", "")
                if not path:
                    return ToolResult(
                        False, self.name, action, "", error="path required"
                    )

                # Check path validity
                if not os.path.exists(path):
                    return ToolResult(
                        False,
                        self.name,
                        action,
                        "",
                        error=f"Path does not exist: {path}",
                    )

                subprocess.Popen(path, shell=False)
                return ToolResult(True, self.name, action, f"Launched {path}")

            else:
                return ToolResult(
                    False, self.name, str(action), "", error=f"Unknown action {action}"
                )
        except Exception as e:
            return ToolResult(False, self.name, str(action), "", error=str(e))
