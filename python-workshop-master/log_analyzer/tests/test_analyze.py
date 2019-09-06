import io
import unittest
import unittest.mock

from .. import (
    analyze,
    logfile,
)
from .factories import LogEntryFactory


class TestGetStats(unittest.TestCase):
    def setUp(self):
        super().setUp()

        self.parser_mock = unittest.mock.Mock(
            name='Parser',
            spec=logfile.Parser(io.StringIO()),
        )
        self.parser_mock.get_entries.return_value = []
        self.parser_mock.invalid_log_entry_count = 0
        self.parser_mock.message_counts_by_type = {}

        get_parser_patcher = unittest.mock.patch(
            'log_analyzer.analyze.get_parser',
            return_value=self.parser_mock,
        )

        self.get_parser_mock = get_parser_patcher.start()
        self.addCleanup(get_parser_patcher.stop)

    def test_empty_log(self):
        stats = analyze.get_stats(unittest.mock.sentinel.log_file_path)

        with self.subTest('logfile path'):
            self.get_parser_mock.assert_called_once_with(unittest.mock.sentinel.log_file_path)

        with self.subTest('stats'):
            self.assertEqual(
                stats,
                analyze.LogStats(
                    message_count=0,
                    invalid_log_entry_count=0,
                    message_counts_by_type={},
                ),
            )

    def test_log(self):
        create_log_entry = LogEntryFactory()

        self.parser_mock.get_entries.return_value = [
            create_log_entry(message_type='msg1'),
            create_log_entry(message_type='msg2'),
            create_log_entry(message_type='msg1'),
            create_log_entry(message_type='msg3'),
            create_log_entry(message_type='msg3'),
            create_log_entry(message_type='msg1'),
        ]

        stats = analyze.get_stats(unittest.mock.sentinel.log_file_path)

        with self.subTest('logfile path'):
            self.get_parser_mock.assert_called_once_with(unittest.mock.sentinel.log_file_path)

        with self.subTest('stats'):
            self.assertEqual(
                stats,
                analyze.LogStats(
                    message_count=6,
                    invalid_log_entry_count=0,
                    message_counts_by_type={
                        'msg1': 3,
                        'msg2': 1,
                        'msg3': 2,
                    },
                ),
            )
