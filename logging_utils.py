import os
import time
import logging
from datetime import datetime
from typing import Callable

import requests

if os.getenv("STANDALONE", None) is not None:
    from logging_level import LoggingLevel, convert_logging_level
else:
    from .logging_level import LoggingLevel, convert_logging_level  # type: ignore[no-redef]

# As this is intended to be used as a submodule, the intention is that there is a config.py file in the root dir that
# contains the configuration values for this module along with other config values, allowing us to configure these in
# one place.
from config import CONFIGURED_LOGGING_LEVEL, LOGGING_DIRECTORY, ENABLE_REMOTE_LOGGING, REMOTE_LOGGING_RATE_LIMIT, LOGGING_API_URL, DEVICE_ID

COLOUR_GREEN = "\x1b[32m"
COLOUR_YELLOW = "\x1b[33m"
COLOUR_RED = "\x1b[31m"
COLOUR_RESET = "\x1b[0m"


class BirdbotLoggerUtils:
    def __init__(
        self,
        logging_directory: str = LOGGING_DIRECTORY,
        logging_level: LoggingLevel = CONFIGURED_LOGGING_LEVEL,
        enable_remote_logging: bool = ENABLE_REMOTE_LOGGING,
        remote_logging_rate_limit: int = REMOTE_LOGGING_RATE_LIMIT,
        logging_api_url: str = LOGGING_API_URL,
        device_id: str = DEVICE_ID,
    ) -> None:
        self.logging_directory = logging_directory
        self.logging_level = logging_level
        self.enable_remote_logging = enable_remote_logging
        self.remote_logging_rate_limit = remote_logging_rate_limit  # In milliseconds
        self.logging_api_url = logging_api_url
        self.device_id = device_id

        self.birdbot_logger = self._setup_logger()
        self.last_log_message_sent_ts = 0  # In milliseconds

    def _setup_logger(self) -> logging.Logger:
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
                message = COLOUR_RED + message + COLOUR_RESET
            elif logging_level == LoggingLevel.WARNING:
                message = COLOUR_YELLOW + message + COLOUR_RESET
            elif logging_level == LoggingLevel.NOTICE:
                message = COLOUR_GREEN + message + COLOUR_RESET
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

    def send_log_to_api(self, message: str, error_logger: Callable[[str, bool], None], notice_logger: Callable[[str], None]) -> None:
        """Sends log to API. error_logger is the log_error() function that is passed in to prevent circular imports.
        Same for notice_logger"""

        if self.remote_logging_rate_limit > 0:
            if self.last_log_message_sent_ts + self.remote_logging_rate_limit > round(time.time() * 1000):
                error_logger("Rate limit reached for remote logging", False)
                return

        data = {
            "device_id": self.device_id,
            "log_timestamp": round(time.time() * 1000),
            "log_message": message,
        }
        result = requests.post(self.logging_api_url, json=data, timeout=10)

        # Set this now to prevent spamming the API, regardless of success
        self.last_log_message_sent_ts = round(time.time() * 1000)

        if result.status_code != 200:
            error_logger(f"Failed to send log to API: {result.status_code} - {result.text}", False)
            return

        notice_logger("Successfully sent log to API")
