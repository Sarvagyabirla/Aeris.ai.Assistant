import os
from dotenv import load_dotenv
from aeris.security.secrets import secret_manager
from aeris.core.exceptions import ConfigurationError

class Settings:
    def __init__(self):
        # Load from .env file if present
        load_dotenv()
        
        self.api_key = os.getenv("AERIS_API_KEY")
        self.model_name = os.getenv("AERIS_MODEL", "gemini-2.5-flash")
        self.app_name = os.getenv("AERIS_APP_NAME", "Aeris")
        self.log_level = os.getenv("AERIS_LOG_LEVEL", "INFO")
        
        # Register secrets
        if self.api_key:
            secret_manager.register_secret(self.api_key)
            
    def validate(self):
        """Validate that all required configuration is present."""
        if not self.api_key:
            raise ConfigurationError("AERIS_API_KEY is not set in environment or .env file.")

# Global settings instance loaded at startup
settings = Settings()
