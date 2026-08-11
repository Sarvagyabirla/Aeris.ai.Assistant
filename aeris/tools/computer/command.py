import subprocess
import shlex
import os
from aeris.tools.tool import Tool
from aeris.tools.security import PermissionLevel, PermissionManager
from aeris.tools.types import ToolResult
from aeris.config.settings import settings


class CommandTool(Tool):
    name = "command_execution"
    description = "Execute basic allowed shell commands."
    permission_level = PermissionLevel.HIGH_RISK
    parameters = {
        "action": {"type": "string", "enum": ["execute"]},
        "command": {"type": "string", "description": "Command to execute"},
        "confirmed": {"type": "boolean", "description": "Set to True only if the user has explicitly confirmed this action."}
    }

    async def execute(self, **kwargs) -> ToolResult:
        action = kwargs.get("action")
        command = kwargs.get("command", "")
        confirmed = kwargs.get("confirmed", False)

        if not command:
            return ToolResult(False, self.name, action, "", error="command required")

        if not PermissionManager.check_execution_allowed(
            self.name, self.permission_level, confirmed=confirmed, details=command
        ):
            return ToolResult(
                False,
                self.name,
                str(action),
                "Blocked by security manager",
                error="Blocked",
            )

        # Parse command safely
        try:
            parts = shlex.split(command, posix=os.name != "nt")
        except ValueError as e:
            return ToolResult(
                False, self.name, action, "", error=f"Invalid command format: {e}"
            )

        if not parts:
            return ToolResult(False, self.name, action, "", error="Empty command")

        base_cmd = parts[0].lower()

        # Check against allowlist
        if base_cmd not in [cmd.lower() for cmd in settings.command_allowlist]:
            return ToolResult(
                False,
                self.name,
                action,
                "",
                error=f"Command '{base_cmd}' is not in the allowlist",
            )

        if settings.dry_run:
            return ToolResult(
                True, self.name, action, f"[DRY RUN] Would execute command: {command}"
            )

        try:
            # DO NOT USE shell=True to prevent command injection
            process = subprocess.run(
                parts, capture_output=True, text=True, timeout=settings.action_timeout, shell=False
            )

            output = process.stdout
            if process.stderr:
                output += f"\nSTDERR: {process.stderr}"

            # Limit output to avoid context overflow
            if len(output) > 5000:
                output = output[:5000] + "\n... (truncated)"

            return ToolResult(
                process.returncode == 0,
                self.name,
                action,
                f"Exited with code {process.returncode}\n{output}",
            )

        except subprocess.TimeoutExpired:
            return ToolResult(
                False,
                self.name,
                action,
                "",
                error=f"Command timed out after {settings.action_timeout} seconds",
            )
        except Exception as e:
            return ToolResult(False, self.name, action, "", error=str(e))
