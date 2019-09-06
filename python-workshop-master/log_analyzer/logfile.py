from __future__ import annotations

import datetime
import json
import logging
import os.path
import re
import typing

from .types import LogEntry

_logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


ParseResult = typing.List[LogEntry]


def parse(path: str) -> ParseResult:
    parser = get_parser(path)

    return parser.get_entries()


def get_parser(path: str) -> Parser:
    file_obj = open(path, 'rt')

    file_extension = os.path.splitext(path)[1]
    if file_extension == '.jsonlog':
        return JsonLogFileParser(file_obj)

    if file_extension == '.log':
        return TextLogFileParser(file_obj)

    raise RuntimeError(f'Unsupported log file {path}: the extension is unknown')


def save_as_json_log(
    log_entries: typing.Iterable[LogEntry],
    output: typing.IO[str],
) -> None:
    for log_entry in log_entries:
        entry_data = {
            'timestamp': log_entry.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'message_type': log_entry.message_type,
            'destination': log_entry.destination,
            'sender': log_entry.sender,
            'payload': log_entry.payload,
        }

        json.dump(entry_data, output)
        output.write('\n')


class Parser:
    def __init__(self, file_obj: typing.IO[str]):
        super().__init__()

        self.invalid_log_entry_count = 0

        self._source = file_obj

    def get_entries(self) -> ParseResult:
        pass


class TextLogFileParser(Parser):
    _ENTRY_RE = re.compile(
        r'\s*'
        r'(?P<timestamp>[^\s].*?[^s])'
        r' '
        r'(?P<message_type>[^\s]+)'
        r' '
        r'(?P<destination>\d+)'
        r' '
        r'(?P<sender>\d+)'
        r' '
        r'(?P<payload>.*)'
    )

    def get_entries(self) -> ParseResult:
        entries = []

        for line in self._source:
            line = line.rstrip('\n')

            try:
                entries.append(self._parse_log_entry(line))

            except ValueError as err:
                _logger.warning('Failed to parse line: %s: %s', line, err)
                self.invalid_log_entry_count += 1

        return entries

    def _parse_log_entry(self, entry_data: str) -> LogEntry:
        match = self._ENTRY_RE.match(entry_data)
        if not match:
            raise ValueError('Invalid structure')

        timestamp_data = match.group('timestamp')
        try:
            timestamp = datetime.datetime.strptime(
                timestamp_data,
                '%Y-%m-%d %H:%M:%S',
            )

        except ValueError as err:
            raise ValueError(f'Invalid timestamp "{timestamp_data}"') from err

        return LogEntry(
            timestamp=timestamp,
            message_type=match.group('message_type'),
            destination=int(match.group('destination')),
            sender=int(match.group('sender')),
            payload=match.group('payload'),
        )


class JsonLogFileParser(Parser):
    def get_entries(self) -> ParseResult:
        entries = []

        for line in self._source:
            try:
                entries.append(self._parse_log_entry(line))

            except ValueError as err:
                _logger.warning('Failed to parse line: %s: %s', line, err)
                self.invalid_log_entry_count += 1

        return entries

    def _parse_log_entry(self, entry_data: str) -> LogEntry:
        try:
            data = json.loads(entry_data)

        except json.decoder.JSONDecodeError as err:
            raise ValueError(str(err)) from err

        timestamp_data = data.get('timestamp', '')
        try:
            timestamp = datetime.datetime.strptime(
                timestamp_data,
                '%Y-%m-%d %H:%M:%S',
            )

        except ValueError as err:
            raise ValueError(f'Invalid timestamp "{timestamp_data}"') from err

        return LogEntry(
            timestamp=timestamp,
            message_type=data.get('message_type', ''),
            destination=data.get('destination', ''),
            sender=data.get('sender', ''),
            payload=data.get('payload', ''),
        )
