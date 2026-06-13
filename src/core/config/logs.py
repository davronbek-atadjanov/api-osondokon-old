import logging
import os
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent.parent.parent / "assets" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


class ExactLevelFilter(logging.Filter):
    def __init__(self, level: int) -> None:
        self.level = level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno == self.level


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "filters": {
        "only_info": {
            "()": ExactLevelFilter,
            "level": logging.INFO,
        },
        "only_warning": {
            "()": ExactLevelFilter,
            "level": logging.WARNING,
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "info_file": {
            "level": "INFO",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "info.log"),
            "when": "midnight",
            "backupCount": 30,
            "formatter": "verbose",
            "filters": ["only_info"],
        },
        "warning_file": {
            "level": "WARNING",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "warning.log"),
            "when": "midnight",
            "backupCount": 30,
            "formatter": "verbose",
            "filters": ["only_warning"],
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "errors.log"),
            "when": "midnight",
            "backupCount": 30,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "info_file", "warning_file", "error_file"],
            "level": "INFO",
            "propagate": True,
        },
    },
}
