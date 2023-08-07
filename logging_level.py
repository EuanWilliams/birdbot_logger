from enum import IntEnum


class LoggingLevel(IntEnum):
    """Logging levels. NOT used by logging module."""

    DEBUG = 0
    INFO = 1
    NOTICE = 2
    WARNING = 3
    ERROR = 4
