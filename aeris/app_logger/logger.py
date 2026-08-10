import logging
from aeris.security.secrets import secret_manager
from aeris.config.settings import settings


class SecretRedactionFilter(logging.Filter):
    """Filter that redacts secrets from log records."""

    def filter(self, record):
        if isinstance(record.msg, str):
            record.msg = secret_manager.redact(record.msg)
        if isinstance(record.args, tuple):
            new_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    new_args.append(secret_manager.redact(arg))
                else:
                    new_args.append(arg)
            record.args = tuple(new_args)
        return True


def setup_logger():
    """Configure and return the root logger."""
    logger = logging.getLogger("aeris")

    level_name = settings.log_level.upper()
    level = getattr(logging, level_name, logging.INFO)
    logger.setLevel(level)

    # Prevent adding multiple handlers if setup is called multiple times
    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter)
        ch.addFilter(SecretRedactionFilter())
        logger.addHandler(ch)

        # File handler
        try:
            fh = logging.FileHandler("aeris.log")
            fh.setLevel(level)
            fh.setFormatter(formatter)
            fh.addFilter(SecretRedactionFilter())
            logger.addHandler(fh)
        except Exception as e:
            print(f"Failed to set up file logger: {e}")

    return logger


log = setup_logger()
