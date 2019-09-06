from __future__ import annotations

import logging
import re
import typing

from . import types

_logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def extract_container_messages(
    source_entries: typing.List[types.LogEntry],
    **expand_kwargs,
) -> typing.List[types.LogEntry]:
    entries = []

    for source_entry in source_entries:
        if source_entry.message_type == 'container':
            entries.extend(expand_container_messages(source_entry, **expand_kwargs))

        else:
            entries.append(source_entry)

    return entries


def expand_container_messages(
    container: types.LogEntry,
    *,
    preserve_container=False,
    annotate_extracted=False,
) -> typing.List[types.LogEntry]:
    entries = []

    if preserve_container:
        entries.append(container)

    if annotate_extracted:
        entries.append(types.LogEntry(
            timestamp=container.timestamp,
            message_type='START_OF_CONTAINER',
            destination=container.destination,
            sender=container.sender,
            payload='Messages from container start here',
        ))

    entries.extend(
        extract_inner_messages(container),
    )

    if annotate_extracted:
        entries.append(types.LogEntry(
            timestamp=container.timestamp,
            message_type='END_OF_CONTAINER',
            destination=container.destination,
            sender=container.sender,
            payload='Messages from container ends here',
        ))

    return entries


def extract_inner_messages(
    container: types.LogEntry,
) -> typing.List[types.LogEntry]:
    assert container.message_type == 'container', container

    inner_message_data_re = re.compile(
        r'(?P<message_type>[^\s]+)'
        r' '
        r'(?P<destination>\d+)'
        r' '
        r'(?P<sender>\d+)'
        r' '
        r'(?P<payload>.*)'
    )

    entries = []
    for message_data in container.payload.split('|||'):
        match = inner_message_data_re.match(message_data)
        if not match:
            _logger.warning(
                'Container message sent at %s from %d to %d contains invalid message "%s"',
                container.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                container.sender,
                container.destination,
                message_data,
            )
            continue

        entries.append(types.LogEntry(
            timestamp=container.timestamp,
            message_type=match.group('message_type'),
            destination=int(match.group('destination')),
            sender=int(match.group('sender')),
            payload=match.group('payload'),
        ))

    return entries


def filter_by_messages(
    log_entries: typing.List[types.LogEntry],
    message_types: typing.Set[str],
) -> typing.List[types.LogEntry]:
    filtered_log_entries = []

    for log_entry in log_entries:
        if log_entry.message_type in message_types:
            filtered_log_entries.append(log_entry)

    return filtered_log_entries


def filter_by_messagers(
    log_entries: typing.List[types.LogEntry],
    messagers: typing.Set[int],
) -> typing.List[types.LogEntry]:
    filtered_log_entries = []

    for log_entry in log_entries:
        if log_entry.sender in messagers or log_entry.destination in messagers:
            filtered_log_entries.append(log_entry)

    return filtered_log_entries
