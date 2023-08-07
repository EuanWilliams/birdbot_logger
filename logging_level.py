import logging
from enum import IntEnum


class LoggingLevel(IntEnum):
    """Logging levels. NOT used by python's logging module, instead used natively"""

    DEBUG = 0
    INFO = 1
    NOTICE = 2
    WARNING = 3
    ERROR = 4


def convert_logging_level(logging_level: LoggingLevel) -> int:
    """Converts LoggingLevel to logging module level"""

    if logging_level == LoggingLevel.DEBUG:
        return logging.DEBUG
    elif logging_level == LoggingLevel.INFO:
        return logging.INFO
    elif logging_level == LoggingLevel.NOTICE:
        # We don't have a NOTICE level in logging module, so we use INFO instead
        return logging.INFO
    elif logging_level == LoggingLevel.WARNING:
        return logging.WARNING
    elif logging_level == LoggingLevel.ERROR:
        return logging.ERROR
    else:
        return logging.INFO
