import logging

# Configure root logger for the banking_system
logger = logging.getLogger("banking_system")
logger.setLevel(logging.INFO)

# Console handler
_ch = logging.StreamHandler()
_ch.setLevel(logging.INFO)
_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
_ch.setFormatter(_formatter)
logger.addHandler(_ch)

class Logger:
    """
    Simple wrapper around Python's logging module for injection into services.
    """
    def __init__(self, name: str = "banking_system"):
        self._logger = logging.getLogger(name)

    def info(self, message: str) -> None:
        """Log an information message."""
        self._logger.info(message)

    def warning(self, message: str) -> None:
        """Log a warning message."""
        self._logger.warning(message)

    def error(self, message: str) -> None:
        """Log an error message."""
        self._logger.error(message)

    def debug(self, message: str) -> None:
        """Log a debug message."""
        self._logger.debug(message)

    def critical(self, message: str) -> None:
        """Log a critical message."""
        self._logger.critical(message)
