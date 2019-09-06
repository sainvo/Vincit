from __future__ import annotations

import datetime
import typing

from .. import types


class LogEntryFactory:
    def __init__(self):
        super().__init__()

        self.current_timestamp = datetime.datetime(
            2019, 8, 21,
            10, 0, 0,
        )

    def __call__(
        self,
        *,
        message_type: str = 'dummy',
        destination: int = 100,
        sender: int = 200,
        payload: typing.Optional[str] = None,
    ):
        self.current_timestamp += datetime.timedelta(seconds=60)

        return types.LogEntry(
            timestamp=self.current_timestamp,
            message_type=message_type,
            destination=destination,
            sender=sender,
            payload=payload or 'Dummy message sent at {}'.format(self.current_timestamp.strftime('%Y-%m-%d %H:%M:%S')),
        )
