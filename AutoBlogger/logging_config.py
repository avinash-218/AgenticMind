import logging
from datetime import datetime
from pathlib import Path

# Module-level flag to ensure logging is configured only once
_LOGGER_INITIALIZED = False

def get_logger(name: str) -> logging.Logger:
    """
    Create and return a named logger with a shared configuration.

    This function initializes logging only once per process:
    - Logs are written to both console and a timestamped file.
    - A single root logger configuration is reused across all modules.
    - Subsequent calls return a child logger with the given name.

    Parameters
    ----------
    name : str
        Name of the logger, typically `__name__` from the calling module.

    Returns
    -------
    logging.Logger
        A configured logger instance scoped to the given name.
    """
    global _LOGGER_INITIALIZED

    # Initialize logging configuration only on the first call
    if not _LOGGER_INITIALIZED:
        # Ensure logs directory exists
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Create a timestamped log file for this execution
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = log_dir / f"{name}_{timestamp}.log"

        # Common log format for both console and file outputs
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )

        # Configure the root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)

        # Console handler for real-time visibility
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # File handler for persistent logs
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)

        # Attach handlers to the root logger
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)

        # Log initialization event once
        root_logger.info(f"Logging initialized → {log_file}")

        # Prevent re-initialization in subsequent calls
        _LOGGER_INITIALIZED = True

    # Return a named child logger for the caller
    return logging.getLogger(name)
