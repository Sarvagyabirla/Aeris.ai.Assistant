class AerisError(Exception):
    """Base exception for all Aeris errors."""



class ConfigurationError(AerisError):
    """Raised when there is an issue with application configuration."""



class ProviderError(AerisError):
    """Raised when the AI provider encounters an error."""



class ToolExecutionError(AerisError):
    """Raised when a tool fails to execute."""

