import logging
import logging.config


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(levelname)s [%(name)s] - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "default",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
    "loggers": {
        "app": {  
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}

def setup_logging():
    """
    Configure application logging.

    Applies LOGGING_CONFIG via dictConfig.
    """
    # Apply the configuration dictionary
    logging.config.dictConfig(LOGGING_CONFIG)
