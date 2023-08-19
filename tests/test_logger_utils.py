import sys
import unittest
from unittest.mock import patch, MagicMock, Mock
from freezegun import freeze_time

# Mock config file
sys.modules["config"] = Mock()

from logging_utils import BirdbotLoggerUtils, COLOUR_GREEN, COLOUR_YELLOW, COLOUR_RESET, COLOUR_RED  # noqa: E402
from logging_level import LoggingLevel  # noqa: E402


class Test(unittest.TestCase):
    @freeze_time("2023-08-19 00:00:00")
    @patch("requests.post")
    def test_send_log_to_api_normal_conditions(self, mock_requests: MagicMock) -> None:
        """Tests send_log_to_api under normal conditions"""

        log_error = MagicMock()
        log_notice = MagicMock()
        mock_requests.return_value.status_code = 200

        logging_level_under_test = LoggingLevel.INFO
        birdbot_logger = BirdbotLoggerUtils(
            logging_directory="logs",
            logging_level=logging_level_under_test,
            enable_remote_logging=True,
            remote_logging_rate_limit=100,
            logging_api_url="http://test.com",
            device_id="test_device_id",
        )

        # Run test
        birdbot_logger.send_log_to_api("test", log_error, log_notice)

        # Check results
        mock_requests.assert_called_once_with(
            "http://test.com",
            json={
                "device_id": "test_device_id",
                "log_timestamp": 1692403200000,
                "log_message": "test",
            },
            timeout=10,
        )
        log_error.assert_not_called()
        log_notice.assert_called_once_with("Successfully sent log to API")
        self.assertEqual(birdbot_logger.last_log_message_sent_ts, 1692403200000)

    @freeze_time("2023-08-19 00:00:00")
    @patch("requests.post")
    def test_send_log_to_api_failed_call(self, mock_requests: MagicMock) -> None:
        """Tests send_log_to_api when the call fails."""

        log_error = MagicMock()
        log_notice = MagicMock()
        mock_requests.return_value.status_code = 404
        mock_requests.return_value.text = "Not found"

        logging_level_under_test = LoggingLevel.INFO
        birdbot_logger = BirdbotLoggerUtils(
            logging_directory="logs",
            logging_level=logging_level_under_test,
            enable_remote_logging=True,
            remote_logging_rate_limit=100,
            logging_api_url="http://test.com",
            device_id="test_device_id",
        )

        # Run test
        birdbot_logger.send_log_to_api("test", log_error, log_notice)

        # Check results
        mock_requests.assert_called_once_with(
            "http://test.com",
            json={
                "device_id": "test_device_id",
                "log_timestamp": 1692403200000,
                "log_message": "test",
            },
            timeout=10,
        )
        log_error.assert_called_once_with("Failed to send log to API: 404 - Not found", False)
        log_notice.assert_not_called()
        self.assertEqual(birdbot_logger.last_log_message_sent_ts, 1692403200000)

    @patch("requests.post")
    def test_send_log_to_api_hitting_rate_limit(self, mock_requests: MagicMock) -> None:
        """Tests send_log_to_api when the call fails."""

        logging_level_under_test = LoggingLevel.INFO
        birdbot_logger = BirdbotLoggerUtils(
            logging_directory="logs",
            logging_level=logging_level_under_test,
            enable_remote_logging=True,
            remote_logging_rate_limit=5000,  # 500 seconds
            logging_api_url="http://test.com",
            device_id="test_device_id",
        )

        with freeze_time("2023-08-19 00:00:00"):
            log_error = MagicMock()
            log_notice = MagicMock()
            mock_requests.return_value.status_code = 200
            mock_requests.return_value.text = "Success"

            # Run test
            birdbot_logger.send_log_to_api("test", log_error, log_notice)

            # Check results
            mock_requests.assert_called_once_with(
                "http://test.com",
                json={
                    "device_id": "test_device_id",
                    "log_timestamp": 1692403200000,
                    "log_message": "test",
                },
                timeout=10,
            )
            log_error.assert_not_called()
            log_notice.assert_called_once_with("Successfully sent log to API")
            self.assertEqual(birdbot_logger.last_log_message_sent_ts, 1692403200000)

        with freeze_time("2023-08-19 00:00:01"):
            log_error = MagicMock()
            log_notice = MagicMock()
            mock_requests.reset_mock()

            # Run test
            birdbot_logger.send_log_to_api("test", log_error, log_notice)

            # Check results
            mock_requests.assert_not_called()
            log_error.assert_called_once_with("Rate limit reached for remote logging", False)
            log_notice.assert_not_called()
            self.assertEqual(birdbot_logger.last_log_message_sent_ts, 1692403200000)

    @patch("requests.post")
    def test_send_log_to_api_rate_limit_ok(self, mock_requests: MagicMock) -> None:
        """Tests send_log_to_api with multiple calls, but not hitting the rate limit."""

        logging_level_under_test = LoggingLevel.INFO
        birdbot_logger = BirdbotLoggerUtils(
            logging_directory="logs",
            logging_level=logging_level_under_test,
            enable_remote_logging=True,
            remote_logging_rate_limit=5000,  # 500 seconds
            logging_api_url="http://test.com",
            device_id="test_device_id",
        )

        with freeze_time("2023-08-19 00:00:00"):
            log_error = MagicMock()
            log_notice = MagicMock()
            mock_requests.return_value.status_code = 200
            mock_requests.return_value.text = "Success"

            # Run test
            birdbot_logger.send_log_to_api("test", log_error, log_notice)

            # Check results
            mock_requests.assert_called_once_with(
                "http://test.com",
                json={
                    "device_id": "test_device_id",
                    "log_timestamp": 1692403200000,
                    "log_message": "test",
                },
                timeout=10,
            )
            log_error.assert_not_called()
            log_notice.assert_called_once_with("Successfully sent log to API")
            self.assertEqual(birdbot_logger.last_log_message_sent_ts, 1692403200000)

        with freeze_time("2023-08-19 01:00:0"):
            log_error = MagicMock()
            log_notice = MagicMock()
            mock_requests.reset_mock()
            mock_requests.return_value.status_code = 200
            mock_requests.return_value.text = "Success"

            # Run test
            birdbot_logger.send_log_to_api("test", log_error, log_notice)

            # Check results
            mock_requests.assert_called_once_with(
                "http://test.com",
                json={
                    "device_id": "test_device_id",
                    "log_timestamp": 1692406800000,
                    "log_message": "test",
                },
                timeout=10,
            )
            log_error.assert_not_called()
            log_notice.assert_called_once_with("Successfully sent log to API")
            self.assertEqual(birdbot_logger.last_log_message_sent_ts, 1692406800000)

    @freeze_time("2023-08-19 00:00:00")
    @patch("builtins.print")
    def test_write_to_console_level_debug_message_info(self, mock_print: MagicMock) -> None:
        """Test we DO log to console when logging level is DEBUG, and given log message is INFO."""

        logging_level_under_test = LoggingLevel.DEBUG
        birdbot_logger = BirdbotLoggerUtils(
            logging_directory="logs",
            logging_level=logging_level_under_test,
            enable_remote_logging=True,
            remote_logging_rate_limit=100,
            logging_api_url="",
            device_id="test_device_id",
        )
        birdbot_logger.write_to_console("test", LoggingLevel.INFO)
        mock_print.assert_called_once_with("19-08-2023 00:00:00: INFO: test")

    @freeze_time("2023-08-19 00:00:00")
    @patch("builtins.print")
    def test_write_to_console_level_debug_message_debug(self, mock_print: MagicMock) -> None:
        """Test we DO log to console when logging level is DEBUG, and given log message is DEBUG."""

        logging_level_under_test = LoggingLevel.DEBUG
        birdbot_logger = BirdbotLoggerUtils(
            logging_directory="logs",
            logging_level=logging_level_under_test,
            enable_remote_logging=True,
            remote_logging_rate_limit=100,
            logging_api_url="",
            device_id="test_device_id",
        )
        birdbot_logger.write_to_console("test", LoggingLevel.DEBUG)
        mock_print.assert_called_once_with("19-08-2023 00:00:00: DEBUG: test")

    @freeze_time("2023-08-19 00:00:00")
    @patch("builtins.print")
    def test_write_to_console_level_info_message_debug(self, mock_print: MagicMock) -> None:
        """Test we DO NOT log to console when logging level is INFO, and given log message is DEBUG."""

        logging_level_under_test = LoggingLevel.INFO
        birdbot_logger = BirdbotLoggerUtils(
            logging_directory="logs",
            logging_level=logging_level_under_test,
            enable_remote_logging=True,
            remote_logging_rate_limit=100,
            logging_api_url="",
            device_id="test_device_id",
        )
        birdbot_logger.write_to_console("test", LoggingLevel.DEBUG)
        mock_print.assert_not_called()

    @freeze_time("2023-08-19 00:00:00")
    @patch("builtins.print")
    def test_write_to_console_level_info_message_info(self, mock_print: MagicMock) -> None:
        """Test we DO log to console when logging level is INFO, and given log message is INFO."""

        logging_level_under_test = LoggingLevel.INFO
        birdbot_logger = BirdbotLoggerUtils(
            logging_directory="logs",
            logging_level=logging_level_under_test,
            enable_remote_logging=True,
            remote_logging_rate_limit=100,
            logging_api_url="",
            device_id="test_device_id",
        )
        birdbot_logger.write_to_console("test", LoggingLevel.INFO)
        mock_print.assert_called_once_with("19-08-2023 00:00:00: INFO: test")

    @freeze_time("2023-08-19 00:00:00")
    @patch("builtins.print")
    def test_write_to_console_level_info_message_notice(self, mock_print: MagicMock) -> None:
        """Test we DO log to console when logging level is INFO, and given log message is NOTICE. Additionally
        tests that we colourise the NOTICE log correctly."""

        logging_level_under_test = LoggingLevel.INFO
        birdbot_logger = BirdbotLoggerUtils(
            logging_directory="logs",
            logging_level=logging_level_under_test,
            enable_remote_logging=True,
            remote_logging_rate_limit=100,
            logging_api_url="",
            device_id="test_device_id",
        )
        birdbot_logger.write_to_console("test", LoggingLevel.NOTICE)
        mock_print.assert_called_once_with(f"19-08-2023 00:00:00: NOTICE: {COLOUR_GREEN}test{COLOUR_RESET}")

    @freeze_time("2023-08-19 00:00:00")
    @patch("builtins.print")
    def test_write_to_console_level_info_message_warning(self, mock_print: MagicMock) -> None:
        """Test we DO log to console when logging level is INFO, and given log message is WARNING. Additionally
        tests that we colourise the WARNING log correctly."""

        logging_level_under_test = LoggingLevel.INFO
        birdbot_logger = BirdbotLoggerUtils(
            logging_directory="logs",
            logging_level=logging_level_under_test,
            enable_remote_logging=True,
            remote_logging_rate_limit=100,
            logging_api_url="",
            device_id="test_device_id",
        )
        birdbot_logger.write_to_console("test", LoggingLevel.WARNING)
        mock_print.assert_called_once_with(f"19-08-2023 00:00:00: WARNING: {COLOUR_YELLOW}test{COLOUR_RESET}")

    @freeze_time("2023-08-19 00:00:00")
    @patch("builtins.print")
    def test_write_to_console_level_info_message_error(self, mock_print: MagicMock) -> None:
        """Test we DO log to console when logging level is INFO, and given log message is ERROR. Additionally
        tests that we colourise the ERROR log correctly."""

        logging_level_under_test = LoggingLevel.INFO
        birdbot_logger = BirdbotLoggerUtils(
            logging_directory="logs",
            logging_level=logging_level_under_test,
            enable_remote_logging=True,
            remote_logging_rate_limit=100,
            logging_api_url="",
            device_id="test_device_id",
        )
        birdbot_logger.write_to_console("test", LoggingLevel.ERROR)
        mock_print.assert_called_once_with(f"19-08-2023 00:00:00: ERROR: {COLOUR_RED}test{COLOUR_RESET}")

    @freeze_time("2023-08-19 00:00:00")
    @patch("builtins.print")
    def test_write_to_console_level_notice_message_info(self, mock_print: MagicMock) -> None:
        """Test we DO NOT log to console when logging level is NOTICE, and given log message is INFO."""

        logging_level_under_test = LoggingLevel.NOTICE
        birdbot_logger = BirdbotLoggerUtils(
            logging_directory="logs",
            logging_level=logging_level_under_test,
            enable_remote_logging=True,
            remote_logging_rate_limit=100,
            logging_api_url="",
            device_id="test_device_id",
        )
        birdbot_logger.write_to_console("test", LoggingLevel.INFO)
        mock_print.assert_not_called()

    @freeze_time("2023-08-19 00:00:00")
    @patch("builtins.print")
    def test_write_to_console_level_notice_message_warning(self, mock_print: MagicMock) -> None:
        """Test we DO log to console when logging level is NOTICE, and given log message is WARNING."""

        logging_level_under_test = LoggingLevel.NOTICE
        birdbot_logger = BirdbotLoggerUtils(
            logging_directory="logs",
            logging_level=logging_level_under_test,
            enable_remote_logging=True,
            remote_logging_rate_limit=100,
            logging_api_url="",
            device_id="test_device_id",
        )
        birdbot_logger.write_to_console("test", LoggingLevel.WARNING)
        mock_print.assert_called_once_with(f"19-08-2023 00:00:00: WARNING: {COLOUR_YELLOW}test{COLOUR_RESET}")

    @freeze_time("2023-08-19 00:00:00")
    @patch("builtins.print")
    def test_write_to_console_level_warning_message_notice(self, mock_print: MagicMock) -> None:
        """Test we DO NOT log to console when logging level is WARNING, and given log message is NOTICE."""

        logging_level_under_test = LoggingLevel.WARNING
        birdbot_logger = BirdbotLoggerUtils(
            logging_directory="logs",
            logging_level=logging_level_under_test,
            enable_remote_logging=True,
            remote_logging_rate_limit=100,
            logging_api_url="",
            device_id="test_device_id",
        )
        birdbot_logger.write_to_console("test", LoggingLevel.NOTICE)
        mock_print.assert_not_called()

    @freeze_time("2023-08-19 00:00:00")
    @patch("builtins.print")
    def test_write_to_console_level_warning_message_error(self, mock_print: MagicMock) -> None:
        """Test we DO log to console when logging level is WARNING, and given log message is ERROR."""

        logging_level_under_test = LoggingLevel.WARNING
        birdbot_logger = BirdbotLoggerUtils(
            logging_directory="logs",
            logging_level=logging_level_under_test,
            enable_remote_logging=True,
            remote_logging_rate_limit=100,
            logging_api_url="",
            device_id="test_device_id",
        )
        birdbot_logger.write_to_console("test", LoggingLevel.ERROR)
        mock_print.assert_called_once_with(f"19-08-2023 00:00:00: ERROR: {COLOUR_RED}test{COLOUR_RESET}")

    @freeze_time("2023-08-19 00:00:00")
    @patch("builtins.print")
    def test_write_to_console_level_error_message_warning(self, mock_print: MagicMock) -> None:
        """Test we DO NOT log to console when logging level is ERROR, and given log message is WARNING."""

        logging_level_under_test = LoggingLevel.ERROR
        birdbot_logger = BirdbotLoggerUtils(
            logging_directory="logs",
            logging_level=logging_level_under_test,
            enable_remote_logging=True,
            remote_logging_rate_limit=100,
            logging_api_url="",
            device_id="test_device_id",
        )
        birdbot_logger.write_to_console("test", LoggingLevel.WARNING)
        mock_print.assert_not_called()

    @freeze_time("2023-08-19 00:00:00")
    @patch("builtins.print")
    def test_write_to_console_level_error_message_error(self, mock_print: MagicMock) -> None:
        """Test we DO NOT log to console when logging level is ERROR, and given log message is ERROR."""

        logging_level_under_test = LoggingLevel.ERROR
        birdbot_logger = BirdbotLoggerUtils(
            logging_directory="logs",
            logging_level=logging_level_under_test,
            enable_remote_logging=True,
            remote_logging_rate_limit=100,
            logging_api_url="",
            device_id="test_device_id",
        )
        birdbot_logger.write_to_console("test", LoggingLevel.ERROR)
        mock_print.assert_called_once_with(f"19-08-2023 00:00:00: ERROR: {COLOUR_RED}test{COLOUR_RESET}")
