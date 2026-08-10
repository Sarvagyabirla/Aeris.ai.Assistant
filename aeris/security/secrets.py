from typing import Set


class SecretManager:
    def __init__(self):
        self._secrets: Set[str] = set()

    def register_secret(self, secret: str):
        if secret and len(secret) > 3:  # Don't redact tiny strings by accident
            self._secrets.add(secret)

    def get_all_secrets(self) -> Set[str]:
        return self._secrets

    def redact(self, text: str) -> str:
        redacted_text = text
        for secret in self._secrets:
            redacted_text = redacted_text.replace(secret, "***REDACTED***")
        return redacted_text


# Singleton
secret_manager = SecretManager()
