import logging
from logging.config import dictConfig


def setup_logging(log_level=logging.INFO, log_file=None):
    handlers = {}

    if not log_file:
        handlers["console"] = {
            "level": log_level,
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "stream": "ext://sys.stdout",
        }

    if log_file:
        handlers["file"] = {
            "level": log_level,
            "class": "logging.FileHandler",
            "formatter": "standard",
            "filename": log_file,
            "mode": "a",
        }

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
        },
        "handlers": handlers,
        "root": {"level": log_level, "handlers": list(handlers.keys())},
        "loggers": {
            "mypackage": {
                "level": log_level,
                "handlers": list(handlers.keys()),
                "propagate": False,
            }
        },
    }

    dictConfig(logging_config)
