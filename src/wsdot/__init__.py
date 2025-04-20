import asyncio
import atexit
from datetime import datetime, timedelta, timezone
import re
from typing import Annotated, Any

import aiohttp
from pydantic import BaseModel, PlainValidator

__session: aiohttp.ClientSession | None = None


def get_long_lived_session() -> aiohttp.ClientSession:
    global __session
    if __session is None:
        session = aiohttp.ClientSession()

        def close_long_lived_session(ses=session, aio=asyncio):
            try:
                loop = aio.get_event_loop()
                if loop.is_running():
                    loop.create_task(ses.close())
                else:
                    loop.run_until_complete(ses.close())
            except Exception:
                pass

        atexit.register(close_long_lived_session)

        __session = session
    return __session


class WsdotTravelError(Exception):
    def __init__(
        self, msg: str = '', url: str | None = None, status: int | None = None
    ) -> None:
        self.msg = msg
        self.url = url
        self.status = status

    def __str__(self) -> str:
        message = self.msg
        if self.url:
            message = f'{message}{" " if message else ""}calling {self.url}'
            if self.status is not None:
                message = f'{message} got {self.status}'
        return message


class WsdotTravel:
    def __init__(
        self, api_key: str, *, session: aiohttp.ClientSession | None = None
    ) -> None:
        self.api_key = api_key
        self.url = 'http://www.wsdot.wa.gov/traffic/api/'
        self.data_path = ''
        self.session = session if session is not None else get_long_lived_session()

    async def get_json(
        self, subpath: str = '', params: dict[Any, Any] | None = None
    ) -> dict[Any, Any]:
        auth_params = {'AccessCode': self.api_key}
        if params:
            auth_params |= params

        travel_url = self.url + self.data_path + subpath
        async with self.session.get(travel_url, params=auth_params) as response:
            if response.status != 200:
                raise WsdotTravelError(
                    'unexpected status', url=travel_url, status=response.status
                )
            if not response.content_type == 'application/json':
                raise WsdotTravelError(
                    'unexpected data type', url=travel_url, status=response.status
                )
            if not await response.text():
                raise WsdotTravelError('received no data', url=travel_url)
            return await response.json()


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


class WsdotTravelTimes(WsdotTravel):
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
