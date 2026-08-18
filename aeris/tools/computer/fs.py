import os
import shutil
from pathlib import Path
from aeris.tools.tool import Tool
from aeris.tools.security import PermissionLevel, PermissionManager
from aeris.tools.types import ToolResult
from aeris.config.settings import settings


class FileSystemTool(Tool):
    name = "fs_control"
    description = (
        "Control the filesystem safely: list, read, write, create, delete, move."
    )
    permission_level = PermissionLevel.MEDIUM_RISK
    parameters = {
        "action": {
            "type": "string",
            "enum": ["list", "read", "write", "create_dir", "delete", "move", "copy"],
        },
        "path": {"type": "string"},
        "dest_path": {"type": "string"},
        "content": {"type": "string"},
        "confirmed": {"type": "boolean", "description": "Set to True only if the user has explicitly confirmed this action."}
    }
    required_params = ["action", "path"]  # dest_path/content/confirmed are action-specific

    def _is_path_allowed(self, target_path: str) -> bool:
        """Check if a path is within the allowed paths."""
        try:
            # Resolve symlinks and absolute path
            target = Path(os.path.realpath(target_path)).resolve()
            for allowed in settings.allowed_paths:
                allowed_path = Path(os.path.realpath(allowed)).resolve()
                # Check if target is same as or child of allowed path
                if target == allowed_path or allowed_path in target.parents:
                    return True
            return False
        except Exception:
            return False

    async def execute(self, **kwargs) -> ToolResult:
        action = kwargs.get("action")
        confirmed = kwargs.get("confirmed", False)
        
        # Deletes and moves out of standard flow might be HIGH_RISK
        req_level = (
            PermissionLevel.HIGH_RISK if action in ["delete", "move"] else self.permission_level
        )

        path = kwargs.get("path", "")
        if not path:
            return ToolResult(False, self.name, str(action), "", error="path required")
            
        details = f"{action} on {path}"

        if not PermissionManager.check_execution_allowed(self.name, req_level, confirmed=confirmed, details=details):
            return ToolResult(
                False,
                self.name,
                str(action),
                "Blocked by security manager",
                error="Blocked",
            )

        if not self._is_path_allowed(path):
            return ToolResult(
                False,
                self.name,
                str(action),
                "",
                error=f"Path not in allowed_paths: {path}",
            )

        dest_path = kwargs.get("dest_path", "")
        if action in ["move", "copy"]:
            if not dest_path:
                return ToolResult(
                    False, self.name, str(action), "", error="dest_path required"
                )
            if not self._is_path_allowed(dest_path):
                return ToolResult(
                    False,
                    self.name,
                    str(action),
                    "",
                    error=f"Destination path not in allowed_paths: {dest_path}",
                )

        if settings.dry_run:
            return ToolResult(
                True,
                self.name,
                str(action),
                f"[DRY RUN] Would perform FS action {kwargs}",
            )

        try:
            if action == "list":
                if not os.path.exists(path) or not os.path.isdir(path):
                    return ToolResult(
                        False,
                        self.name,
                        action,
                        "",
                        error="Path is not a valid directory",
                    )
                items = os.listdir(path)
                # Cap the output
                if len(items) > 100:
                    items = items[:100] + ["... (truncated)"]
                return ToolResult(
                    True, self.name, action, f"Directory contents: {items}"
                )

            elif action == "read":
                if not os.path.exists(path) or not os.path.isfile(path):
                    return ToolResult(
                        False, self.name, action, "", error="Path is not a valid file"
                    )
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Cap content length
                    if len(content) > 10000:
                        content = content[:10000] + "\n... (truncated)"
                return ToolResult(True, self.name, action, content)

            elif action == "write":
                content = kwargs.get("content", "")
                # Ensure directory exists
                os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                return ToolResult(
                    True, self.name, action, f"Wrote {len(content)} chars to {path}"
                )

            elif action == "create_dir":
                os.makedirs(path, exist_ok=True)
                return ToolResult(True, self.name, action, f"Created directory {path}")

            elif action == "delete":
                if not os.path.exists(path):
                    return ToolResult(
                        False, self.name, action, "", error="Path does not exist"
                    )
                if os.path.isfile(path):
                    os.remove(path)
                else:
                    shutil.rmtree(path)
                return ToolResult(True, self.name, action, f"Deleted {path}")

            elif action == "move":
                shutil.move(path, dest_path)
                return ToolResult(
                    True, self.name, action, f"Moved {path} to {dest_path}"
                )

            elif action == "copy":
                if os.path.isfile(path):
                    shutil.copy2(path, dest_path)
                else:
                    shutil.copytree(path, dest_path)
                return ToolResult(
                    True, self.name, action, f"Copied {path} to {dest_path}"
                )

            else:
                return ToolResult(
                    False, self.name, str(action), "", error=f"Unknown action {action}"
                )
        except Exception as e:
            return ToolResult(False, self.name, str(action), "", error=str(e))
