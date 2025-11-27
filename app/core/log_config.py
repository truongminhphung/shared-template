import logging
import logging.config
from app.core.middleware import request_id_var


class RequestIDFilter(logging.Filter):
    """
    Logging filter that adds the current request ID to log records.

    This allows the request ID to be included in all logs for that request,
    making it easy to trace a specific user's actions through the logs.
    """

    def filter(self, record):
        request_id = request_id_var.get()
        record.request_id = request_id if request_id else ""
        return True


class RequestIDFormatter(logging.Formatter):
    """
    Custom formatter that conditionally includes the request ID in the log message.

    If a request ID exists, it will be included as [request_id].
    If no request ID (e.g., startup logs), it will be omitted entirely.
    """

    def format(self, record):
        if record.request_id:
            record.msg_prefix = f"[{record.request_id}] "
        else:
            record.msg_prefix = ""
        return super().format(record)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": RequestIDFormatter,
            "format": "%(asctime)s - %(levelname)s [%(name)s] %(msg_prefix)s- %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "default",
            "filters": ["request_id_filter"],
        },
    },
    "filters": {
        "request_id_filter": {
            "()": RequestIDFilter,
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
