import logging
from datetime import datetime
from pathlib import Path

_LOGGER_INITIALIZED = False

def get_logger(name: str) -> logging.Logger:
    """
    Returns a named logger.
    Logging is initialized ONLY ONCE with a single file + console output.
    """
    global _LOGGER_INITIALIZED

    if not _LOGGER_INITIALIZED:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = log_dir / f"{name}_{timestamp}.log"

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # File handler
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)

        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)

        root_logger.info(f"Logging initialized → {log_file}")
        _LOGGER_INITIALIZED = True

    return logging.getLogger(name)
