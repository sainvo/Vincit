from __future__ import annotations

import dataclasses
import datetime


@dataclasses.dataclass
class LogEntry:
    timestamp: datetime.datetime
    message_type: str
    destination: int
    sender: int
    payload: str
