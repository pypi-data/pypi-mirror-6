import unittest
import logging
from mock import patch, MagicMock

import soklog


class SoklogTest(unittest.TestCase):

    @patch('soklog.logging.getLogger')
    def test_init(self, mock):
        soklog.init(1, 2)

        mock.assert_called_with(2)
        self.assertEqual(1, soklog._DEFAULT.module)
        self.assertEqual(mock.return_value, soklog._DEFAULT.log)

    @patch('soklog.logging.getLogger')
    def test__get_args_as_string(self, mock):
        module = MagicMock()
        log = MagicMock()
        soklog_obj = soklog.SokLog(module, log)

        self.assertEqual('1 2 3', soklog_obj._get_args_as_string([1, 2, '3']))

    @patch.object(soklog._DEFAULT, 'log')
    def test_info(self, log_mock):
        soklog.info(1, 2, 3, something=4)
        log_mock.info.assert_called_with("1 2 3", something=4)

    @patch.object(soklog._DEFAULT, 'log')
    def test_warning(self, log_mock):
        soklog.warning(1, 2, 3, something=4)
        log_mock.warning.assert_called_with("1 2 3", something=4)

    @patch.object(soklog._DEFAULT, 'log')
    def test_debug(self, log_mock):
        with patch.object(soklog._DEFAULT, 'module', soklog):
            soklog.debug(1, 2, 3, something=4)
            log_mock.debug.assert_called_with(
                './tests.py:39 1 2 3', level=2, something=4)

    @patch.object(soklog._DEFAULT, 'log')
    def test_error(self, log_mock):
        soklog.error(1, 2, 3, something=4)
        log_mock.error.assert_called_with(1, 2, 3, something=4)

    @patch('soklog.logging.basicConfig')
    def test_start_stdout_logging(self, mock):
        soklog.start_stdout_logging()
        mock.assert_called_with(
            level=logging.DEBUG,
            format="%(asctime)-10s %(message)s",
            datefmt="%H:%M:%S"
        )

    @patch('soklog.logging')
    def test_start_file_logging(self, mock):
        with patch.object(soklog._DEFAULT, 'log') as log_mock:
            soklog.start_file_logging('somewhere')
            mock.FileHandler.assert_called_with('somewhere')
            mock.Formatter.assert_called_with("%(asctime)-10s %(message)s")

            hdlr = mock.FileHandler.return_value
            hdlr.setFormatter.assert_called_with(mock.Formatter.return_value)

            log_mock.addHandler.assert_called_with(hdlr)
            log_mock.setLevel.assert_called_with(mock.DEBUG)
