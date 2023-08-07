"""Wrapper around logging module to colourise outputs, log to console, and log to file. Designed to be used as a
submodule"""
# TODO: Log errors to API.

import os
import logging
from logging import Logger
from typing import Any
from datetime import datetime

from .logging_level import LoggingLevel, convert_logging_level

# Requires config.py in root directory. If we are somehow standalone we just set to some defaults.
try:
    from config import LOGGING_DIRECTORY, CONFIGURED_LOGGING_LEVEL
except ImportError:
    LOGGING_DIRECTORY = "logs"
    CONFIGURED_LOGGING_LEVEL = LoggingLevel.INFO


class BirdbotLogger:
    def __init__(self, logging_directory: str = LOGGING_DIRECTORY, logging_level: LoggingLevel = CONFIGURED_LOGGING_LEVEL) -> None:
        self.logging_directory = logging_directory
        self.logging_level = logging_level

        self.birdbot_logger = self._setup_logger()

    def _setup_logger(self) -> Logger:
        """Configures logger"""

        birdbot_logger = logging.getLogger("birdbot_logger")
        logger_filename = self.generate_log_file_name(error=False)
        file_handler = logging.FileHandler(logger_filename)
        birdbot_logger.setLevel(convert_logging_level(self.logging_level))
        birdbot_logger.addHandler(file_handler)

        return birdbot_logger

    def write_to_console(self, message: str, logging_level: LoggingLevel = LoggingLevel.INFO) -> None:
        """Writes message to console"""

        if logging_level >= self.logging_level:
            print(self.format_text(message, colour=True, logging_level=logging_level))

    @staticmethod
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

    def generate_log_file_name(self, error: bool) -> str:
        """Generates log file name from current date"""

        current_date = datetime.now()

        if not os.path.exists(self.logging_directory):
            os.makedirs(self.logging_directory)

        if error:
            logging_filename = os.path.join(self.logging_directory, current_date.strftime("%d-%m-%y-birdbot-error.log"))
        else:
            logging_filename = os.path.join(self.logging_directory, current_date.strftime("%d-%m-%y-birdbot.log"))

        return logging_filename


birdbot_logger = BirdbotLogger()


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


def log_error(message: Any) -> None:
    """Logs error messages"""

    birdbot_logger.write_to_console(message, LoggingLevel.ERROR)
    try:
        logging.getLogger("birdbot_logger").error(birdbot_logger.format_text(message))
    except Exception as error:
        print(f"Error while logging: {error}")
