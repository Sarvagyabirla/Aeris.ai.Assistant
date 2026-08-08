class AerisError(Exception):
    """Base exception for all Aeris errors."""
    pass

class ConfigurationError(AerisError):
    """Raised when there is an issue with application configuration."""
    pass

class ProviderError(AerisError):
    """Raised when the AI provider encounters an error."""
    pass

class ToolExecutionError(AerisError):
    """Raised when a tool fails to execute."""
    pass
