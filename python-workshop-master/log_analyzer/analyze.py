from __future__ import annotations

import dataclasses
import typing

from .logfile import get_parser


@dataclasses.dataclass
class LogStats:
    message_count: int
    invalid_log_entry_count: int
    message_counts_by_type: typing.Dict[str, int]


def get_stats(log_file_path: str) -> LogStats:
    parser = get_parser(log_file_path)
    log_entries = parser.get_entries()

    message_counts_by_type: typing.Dict[str, int] = {}
    for entry in log_entries:
        if entry.message_type not in message_counts_by_type:
            message_counts_by_type[entry.message_type] = 1

        else:
            message_counts_by_type[entry.message_type] += 1

    return LogStats(
        message_count=len(log_entries),
        invalid_log_entry_count=parser.invalid_log_entry_count,
        message_counts_by_type=message_counts_by_type,
    )
