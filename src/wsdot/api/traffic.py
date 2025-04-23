from datetime import datetime, timedelta, timezone
import re
from typing import Annotated, Any

import aiohttp
from pydantic import BaseModel, PlainValidator

from .base import Wsdot


class TravelLocation(BaseModel):
    Description: str | None
    Direction: str | None
    Latitude: float
    Longitude: float
    MilePost: float
    RoadName: str | None


def _updated_datetime(time_updated: Any) -> datetime:
    if not isinstance(time_updated, str):
        raise ValueError('string required')
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


class TravelTime(BaseModel):
    AverageTime: int
    CurrentTime: int
    Description: str | None
    Distance: float
    EndPoint: TravelLocation | None
    Name: str | None
    StartPoint: TravelLocation | None
    TimeUpdated: Annotated[datetime, PlainValidator(_updated_datetime)]
    TravelTimeID: int


class WsdotTravelTimes(Wsdot):
    def __init__(
        self, api_key: str, *, session: aiohttp.ClientSession | None = None
    ) -> None:
        super().__init__(api_key=api_key, session=session)
        self.data_path = 'TravelTimes/TravelTimesREST.svc/'

    async def get_all_travel_times(self) -> list[TravelTime]:
        return [
            TravelTime(**travel_time)
            for travel_time in await self.get_json(subpath='GetTravelTimesAsJson')
        ]

    async def get_travel_time(self, travel_time_id: int) -> TravelTime:
        return TravelTime(
            **await self.get_json(
                subpath='GetTravelTimeAsJson', params={'TravelTimeID': travel_time_id}
            )
        )
