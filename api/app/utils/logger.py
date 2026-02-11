import logging
import sys
from pathlib import Path
from typing import Optional

from app.config.settings import settings


def get_logger(
    name: str,
    level: Optional[int] = None,
    log_file: str = "ecommerce_api.log",
):
    """
    Create and configure a logger with file and console handlers.
    
    Args:
        name: Logger name (usually __name__)
        level: Logging level (defaults to settings.log_level)
        log_file: Log file name
        
    Returns:
        Configured logger instance
    """
    # Convert string level to logging level if not provided
    if level is None:
        level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_path = log_dir / log_file

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # ---- File handler (append-only) ----
    file_handler = logging.FileHandler(
        log_path,
        mode="a",
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    # ---- Stdout handler ----
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(level)
    stdout_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stdout_handler)

    return logger



