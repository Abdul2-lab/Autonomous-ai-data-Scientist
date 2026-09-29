import logging
import logging.handlers
import os
from app.config import settings


def setup_logging():
    logger = logging.getLogger("app")
    if logger.handlers:
        return logger  # already configured

    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    console = logging.StreamHandler()
    console.setFormatter(fmt)
    logger.addHandler(console)

    os.makedirs(settings.LOG_DIR, exist_ok=True)
    file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(settings.LOG_DIR, "app.log"), maxBytes=2_000_000, backupCount=3
    )
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    # Never log secrets: this logger must only ever receive messages that
    # have already been scrubbed of API keys by calling code.
    return logger
