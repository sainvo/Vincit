import datetime
import io
import logging

import pytest

from .. import (
    logfile,
    types,
)


def test_parse_ping_pong_log(log_path):
    entries = logfile.parse(log_path('log_ping_pong.log'))

    assert entries == [
        types.LogEntry(datetime.datetime(2019, 8, 19, 14, 29, 24), 'ping', 1, 2, 'PING'),
        types.LogEntry(datetime.datetime(2019, 8, 19, 14, 29, 25), 'pong', 2, 1, 'PONG'),
        types.LogEntry(datetime.datetime(2019, 8, 19, 14, 30, 24), 'ping', 1, 3, 'PING'),
        types.LogEntry(datetime.datetime(2019, 8, 19, 14, 30, 25), 'pong', 3, 1, 'PONG'),
    ]


@pytest.mark.parametrize(
    'invalid_log_entry, expected_log_message',
    (
        (
            '2019-02-29 01:02:03 ping 1 2 PING',
            'Invalid timestamp "2019-02-29 01:02:03"',
        ),
        (
            '2019-02-28 01:02:03 ping 1 PING',
            'Invalid structure',
        ),
    ),
)
def test_invalid_log_entries_in_text_log(
    mocker,
    caplog,
    log_path,
    invalid_log_entry,
    expected_log_message,
):
    log_mock = io.StringIO()
    with open(log_path('log_ping_pong.log'), 'rt') as log:
        log_mock.write(log.read())

    log_mock.write(f'{invalid_log_entry}\n')

    log_mock.seek(0)

    open_mock = mocker.patch('log_analyzer.logfile.open', return_value=log_mock)

    with caplog.at_level(logging.WARNING, logger='log_analyzer'):
        entries = logfile.parse('test.log')

    open_mock.assert_called_once_with('test.log', 'rt')

    assert expected_log_message in caplog.text

    assert entries == [
        types.LogEntry(datetime.datetime(2019, 8, 19, 14, 29, 24), 'ping', 1, 2, 'PING'),
        types.LogEntry(datetime.datetime(2019, 8, 19, 14, 29, 25), 'pong', 2, 1, 'PONG'),
        types.LogEntry(datetime.datetime(2019, 8, 19, 14, 30, 24), 'ping', 1, 3, 'PING'),
        types.LogEntry(datetime.datetime(2019, 8, 19, 14, 30, 25), 'pong', 3, 1, 'PONG'),
    ]


def test_parse_json_log(log_path):
    entries = logfile.parse(log_path('log_ping_pong.jsonlog'))

    assert entries == [
        types.LogEntry(datetime.datetime(2019, 8, 19, 14, 29, 24), 'ping', 1, 2, 'PING'),
        types.LogEntry(datetime.datetime(2019, 8, 19, 14, 29, 25), 'pong', 2, 1, 'PONG'),
        types.LogEntry(datetime.datetime(2019, 8, 19, 14, 30, 24), 'ping', 1, 3, 'PING'),
        types.LogEntry(datetime.datetime(2019, 8, 19, 14, 30, 25), 'pong', 3, 1, 'PONG'),
    ]


@pytest.mark.parametrize(
    'invalid_log_entry, expected_log_message',
    (
        (
            # pylint: disable=line-too-long
            '{"timestamp": "2019-02-29 01:02:03", "message_type": "pong", "destination": 3, "sender": 1, "payload": "PONG"}',
            'Invalid timestamp "2019-02-29 01:02:03"',
        ),
        (
            '2019-02-01 01:02:03 ping 1 2 PING',
            'Failed to parse line: 2019-02-01 01:02:03 ping 1 2 PING',
        ),
    ),
)
def test_invalid_log_entries_in_json_log(
    mocker,
    caplog,
    log_path,
    invalid_log_entry,
    expected_log_message,
):
    log_mock = io.StringIO()
    with open(log_path('log_ping_pong.jsonlog'), 'rt') as log:
        log_mock.write(log.read())

    log_mock.write(f'{invalid_log_entry}\n')

    log_mock.seek(0)

    open_mock = mocker.patch('log_analyzer.logfile.open', return_value=log_mock)

    with caplog.at_level(logging.WARNING, logger='log_analyzer'):
        entries = logfile.parse('test.jsonlog')

    open_mock.assert_called_once_with('test.jsonlog', 'rt')

    assert expected_log_message in caplog.text

    assert entries == [
        types.LogEntry(datetime.datetime(2019, 8, 19, 14, 29, 24), 'ping', 1, 2, 'PING'),
        types.LogEntry(datetime.datetime(2019, 8, 19, 14, 29, 25), 'pong', 2, 1, 'PONG'),
        types.LogEntry(datetime.datetime(2019, 8, 19, 14, 30, 24), 'ping', 1, 3, 'PING'),
        types.LogEntry(datetime.datetime(2019, 8, 19, 14, 30, 25), 'pong', 3, 1, 'PONG'),
    ]


def test_save_as_json_log(mocker):
    log = [
        types.LogEntry(datetime.datetime(2019, 8, 19, 14, 29, 24), 'ping', 1, 2, 'PING'),
        types.LogEntry(datetime.datetime(2019, 8, 19, 14, 29, 25), 'pong', 2, 1, 'PONG'),
        types.LogEntry(datetime.datetime(2019, 8, 19, 14, 30, 24), 'ping', 1, 3, 'PING'),
        types.LogEntry(datetime.datetime(2019, 8, 19, 14, 30, 25), 'pong', 3, 1, 'PONG'),
    ]

    output = io.StringIO()

    logfile.save_as_json_log(log, output)

    mocker.patch('log_analyzer.logfile.open', return_value=output)

    output.seek(0)
    entries = logfile.parse('test.jsonlog')

    assert entries == log


def test_unknown_log_file_extension(mocker):
    mocker.patch('log_analyzer.logfile.open')

    with pytest.raises(RuntimeError):
        logfile.parse('log.txt')
