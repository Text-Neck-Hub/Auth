import os
import logging


LOG_DIR = "/app/logs"
os.makedirs(LOG_DIR, exist_ok=True)


class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[94m",
        "INFO": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "CRITICAL": "\033[41m",
    }
    RESET = "\033[0m"

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        message = super().format(record)
        return f"{log_color}{message}{self.RESET}"


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "colored": {
            "()": ColoredFormatter,
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "colored",
            "level": "DEBUG",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "debug.log"),
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 5,
            "formatter": "verbose",
            "level": "DEBUG",
            "encoding": "utf-8",
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "error.log"),
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 5,
            "formatter": "verbose",
            "level": "ERROR",
            "encoding": "utf-8",
        },
    },
    "loggers": {

        "prod": {
            "handlers": ["console", "file", "error_file"],
            "level": "DEBUG",
            "propagate": False,
        },

        "": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
