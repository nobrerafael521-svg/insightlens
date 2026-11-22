import logging
import os
from logging.handlers import RotatingFileHandler

from .config import get_app_config

_LOGGER_CONFIGURED = False


def setup_logging() -> None:
    global _LOGGER_CONFIGURED
    if _LOGGER_CONFIGURED:
        return

    app_cfg = get_app_config()
    logs_dir = app_cfg.paths.get("logs_dir", "logs")
    os.makedirs(logs_dir, exist_ok=True)

    log_level_str = os.getenv("INSIGHTLENS_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, log_level_str, logging.INFO)

    log_path = os.path.join(logs_dir, "insightlens.log")

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    _LOGGER_CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    setup_logging()
    return logging.getLogger(name)
