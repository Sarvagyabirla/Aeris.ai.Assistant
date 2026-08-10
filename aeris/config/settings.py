import os
from dotenv import load_dotenv
from aeris.security.secrets import secret_manager
from aeris.core.exceptions import ConfigurationError


class Settings:
    def __init__(self):
        # Load from .env file if present
        load_dotenv()

        self.api_key = os.getenv("AERIS_API_KEY")
        self.model_name = os.getenv("AERIS_MODEL", "gemini-2.0-flash")
        self.app_name = os.getenv("AERIS_APP_NAME", "Aeris")
        self.log_level = os.getenv("AERIS_LOG_LEVEL", "INFO")

        # Part 2: Computer Control Settings
        self.dry_run = os.getenv("AERIS_DRY_RUN", "False").lower() == "true"
        self.kill_switch_enabled = (
            os.getenv("AERIS_KILL_SWITCH", "True").lower() == "true"
        )

        # Allowed paths for filesystem operations (defaults to home dir if not specified)
        allowed_paths_str = os.getenv("AERIS_ALLOWED_PATHS", "")
        if allowed_paths_str:
            self.allowed_paths = [p.strip() for p in allowed_paths_str.split(",")]
        else:
            self.allowed_paths = [os.path.expanduser("~")]

        # Allowed shell commands
        cmd_allowlist_str = os.getenv("AERIS_COMMAND_ALLOWLIST", "ping,echo,dir,ls")
        self.command_allowlist = [c.strip() for c in cmd_allowlist_str.split(",")]

        self.action_timeout = int(os.getenv("AERIS_ACTION_TIMEOUT", "10"))

        # Register secrets
        if self.api_key:
            secret_manager.register_secret(self.api_key)

    def validate(self):
        """Validate that all required configuration is present."""
        if not self.api_key:
            raise ConfigurationError(
                "AERIS_API_KEY is not set in environment or .env file."
            )


# Global settings instance loaded at startup
settings = Settings()
