import os
import logging
from typing import Any
from datetime import datetime

from config import LOGGING_DIRECTORY, CONFIGURED_LOGGING_LEVEL
from .logging_level import LoggingLevel


def generate_log_file_name(error: bool) -> str:
    """Generates log file name from current date"""

    current_date = datetime.now()

    if not os.path.exists(LOGGING_DIRECTORY):
        os.makedirs(LOGGING_DIRECTORY)

    if error:
        logging_filename = os.path.join(LOGGING_DIRECTORY, current_date.strftime("%d-%m-%y-birdbot-error.log"))
    else:
        logging_filename = os.path.join(LOGGING_DIRECTORY, current_date.strftime("%d-%m-%y-birdbot.log"))

    return logging_filename


def write_to_console(message: str, logging_level: LoggingLevel = LoggingLevel.INFO) -> None:
    """Writes message to console"""

    if logging_level >= CONFIGURED_LOGGING_LEVEL:
        print(format_text(message, colour=True, logging_level=logging_level))


def format_text(message: str, colour: bool = False, logging_level: LoggingLevel = LoggingLevel.INFO) -> str:
    time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    if colour:
        if logging_level == LoggingLevel.ERROR:
            message = "\x1b[31m" + message + "\x1b[0m"
        elif logging_level == LoggingLevel.WARNING:
            message = "\x1b[33m" + message + "\x1b[0m"
        elif logging_level == LoggingLevel.NOTICE:
            message = "\x1b[32m" + message + "\x1b[0m"
        else:
            message = message

    formatted_message = f"{time}: {logging_level.name}: {message}"

    return formatted_message


birdbot_logger = logging.getLogger("birdbot_logger")
logger_filename = generate_log_file_name(error=False)
file_handler = logging.FileHandler(logger_filename)
birdbot_logger.setLevel(CONFIGURED_LOGGING_LEVEL.name)
birdbot_logger.addHandler(file_handler)


def log_debug(message: Any) -> None:
    """Logs debug messages"""

    write_to_console(message, LoggingLevel.DEBUG)
    try:
        logging.getLogger("birdbot_logger").debug(format_text(message))
    except Exception as error:
        print(f"Error while logging: {error}")


def log_info(message: Any) -> None:
    """Logs information messages"""

    write_to_console(message, LoggingLevel.INFO)
    try:
        logging.getLogger("birdbot_logger").info(format_text(message))
    except Exception as error:
        print(f"Error while logging: {error}")


def log_notice(message: Any) -> None:
    """Logs information messages but in green"""

    write_to_console(message, LoggingLevel.NOTICE)
    try:
        logging.getLogger("birdbot_logger").info(format_text(message))
    except Exception as error:
        print(f"Error while logging: {error}")


def log_warning(message: Any) -> None:
    """Logs warning messages"""

    write_to_console(message, LoggingLevel.WARNING)
    try:
        logging.getLogger("birdbot_logger").warning(format_text(message))
    except Exception as error:
        print(f"Error while logging: {error}")


def log_error(message: Any) -> None:
    """Logs error messages"""

    write_to_console(message, LoggingLevel.ERROR)
    try:
        logging.getLogger("birdbot_logger").error(format_text(message))
    except Exception as error:
        print(f"Error while logging: {error}")
