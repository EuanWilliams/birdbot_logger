"""Wrapper around logging module to colourise outputs, log to console, file and server. Designed to be implemented as a
submodule. Main entry point."""

import os
import logging
from typing import Any
from logging_utils import BirdbotLoggerUtils

if os.getenv("STANDALONE", None) is not None:
    from logging_level import LoggingLevel
else:
    from .logging_level import LoggingLevel  # type: ignore[no-redef]


birdbot_logger = BirdbotLoggerUtils()


# Not in the class so we can access cleanly from other modules without initialising
def log_debug(message: Any) -> None:
    """Logs debug messages"""

    birdbot_logger.write_to_console(message, LoggingLevel.DEBUG)
    try:
        logging.getLogger("birdbot_logger").debug(birdbot_logger.format_text(message))
    except Exception as error:
        print(f"Error while logging: {error}")


def log_info(message: Any) -> None:
    """Logs information messages"""

    birdbot_logger.write_to_console(message, LoggingLevel.INFO)
    try:
        logging.getLogger("birdbot_logger").info(birdbot_logger.format_text(message))
    except Exception as error:
        print(f"Error while logging: {error}")


def log_notice(message: Any) -> None:
    """Logs information messages but in green"""

    birdbot_logger.write_to_console(message, LoggingLevel.NOTICE)
    try:
        logging.getLogger("birdbot_logger").info(birdbot_logger.format_text(message))
    except Exception as error:
        print(f"Error while logging: {error}")


def log_warning(message: Any) -> None:
    """Logs warning messages"""

    birdbot_logger.write_to_console(message, LoggingLevel.WARNING)
    try:
        logging.getLogger("birdbot_logger").warning(birdbot_logger.format_text(message))
    except Exception as error:
        print(f"Error while logging: {error}")


def log_error(message: Any, send_to_api: bool = True) -> None:
    """Logs error messages. Send to api is used to prevent infinite loops when sending errors to api, overrides
    enable_remote_logging"""

    birdbot_logger.write_to_console(message, LoggingLevel.ERROR)
    try:
        logging.getLogger("birdbot_logger").error(birdbot_logger.format_text(message))
        if send_to_api and birdbot_logger.enable_remote_logging:
            birdbot_logger.send_log_to_api(message, log_error, log_notice)
    except Exception as error:
        print(f"Error while logging: {error}")
