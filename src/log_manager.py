import logging
import logging.config
from pathlib import Path

class LevelFilter(logging.Filter):
    def __init__(self, level):
        super().__init__()
        self.level = level

    def filter(self, record):
        return record.levelno == self.level

class LogManager:
    __CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "info_formatter": {
                "format": "\033[38;5;242m%(asctime)s\033[0m \033[0;92m[%(name)s/INFO]\033[0m \033[38;5;39m[%(funcName)s]\033[0m %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "debug_formatter": {
                "format": "\033[38;5;242m%(asctime)s\033[0m \033[0;36m[%(name)s/DEBUG]\033[0m \033[38;5;39m[%(filename)s]\033[0m %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "warning_formatter": {
                "format": "\033[38;5;242m%(asctime)s\033[0m \033[0;33m[%(name)s/WARNING]\033[0m \033[38;5;39m[%(filename)s]\033[0m %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "error_formatter": {
                "format": "\033[38;5;242m%(asctime)s\033[0m \033[0;31m[%(name)s/ERROR]\033[0m \033[38;5;39m[%(filename)s]\033[0m %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "plain_text": {
                "format": "%(asctime)s [%(name)s/%(levelname)s] [%(funcName)s:%(lineno)d] %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "filters": {
            "info_only": {
                "()": LevelFilter,
                "level": logging.INFO
            },
            "debug_only": {
                "()": LevelFilter,
                "level": logging.DEBUG
            },
            "warning_only": {
                "()": LevelFilter,
                "level": logging.WARNING
            },
            "error_only": {
                "()": LevelFilter,
                "level": logging.ERROR
            }
        },
        "handlers": {
            "console_info": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "info_formatter",
                "filters": ["info_only"],
                "stream": "ext://sys.stdout"
            },
            "console_debug": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "debug_formatter",
                "filters": ["debug_only"],
                "stream": "ext://sys.stdout"
            },
            "console_warning": {
                "class": "logging.StreamHandler",
                "level": "WARNING",
                "formatter": "warning_formatter",
                "filters": ["warning_only"],
                "stream": "ext://sys.stdout"
            },
            "console_error": {
                "class": "logging.StreamHandler",
                "level": "ERROR",
                "formatter": "error_formatter",
                "filters": ["error_only"],
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.FileHandler",
                "level": "DEBUG",
                "formatter": "plain_text",
                "filename": "logs/alien_invasion.log",
                "encoding": "utf-8",
                "mode": "w"
            }
        },
        "loggers": {
            "": {
                "handlers": ["console_info", "console_debug", "console_warning", "console_error", "file"],
                "level": "DEBUG",
                "propagate": False
            }
        }
    }

    @staticmethod
    def init():
        """Setup logging configuration."""

        Path("logs").mkdir(exist_ok=True)
        logging.config.dictConfig(LogManager.__CONFIG)
        logging.captureWarnings(True)
