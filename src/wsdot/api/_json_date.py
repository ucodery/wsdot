from datetime import datetime, timedelta, timezone
import re
from typing import Any


def _parse_datetime(time_updated: Any) -> datetime:
    if not isinstance(time_updated, str):
        raise ValueError('string required')
    # 13 digits of miliseconds = 10 digits of seconds which only includes dates between
    # 2001-09-08 and 2286-11-20 but that will cover the next 250 years...
    timestamp_parts = re.match(
        r'/Date\((?P<mseconds>\d{13})(?P<zhr>[+-]\d{2})(?P<zmin>\d{2})\)/', time_updated
    )
    if timestamp_parts is None:
        raise ValueError('unsupported datetime format (expected "/Date(%s%f%z)/")')
    ts = int(timestamp_parts.group('mseconds')) / 1000
    tz = timezone(
        timedelta(
            hours=int(timestamp_parts.group('zhr')),
            minutes=int(timestamp_parts.group('zmin')),
        )
    )
    return datetime.fromtimestamp(ts, tz=tz)
