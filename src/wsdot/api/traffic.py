from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, PlainValidator

from ._json_date import _parse_datetime
from .base import Wsdot


class TravelLocation(BaseModel):
    Description: str | None
    Direction: str | None
    Latitude: float
    Longitude: float
    MilePost: float
    RoadName: str | None


class TravelTime(BaseModel):
    AverageTime: int
    CurrentTime: int
    Description: str | None
    Distance: float
    EndPoint: TravelLocation | None
    Name: str | None
    StartPoint: TravelLocation | None
    TimeUpdated: Annotated[datetime, PlainValidator(_parse_datetime)]
    TravelTimeID: int


class WsdotTravelTimes(Wsdot):
    api_url = 'http://www.wsdot.wa.gov/traffic/api/TravelTimes/TravelTimesREST.svc/'

    def auth_header(self) -> dict[str, str]:
        return {'AccessCode': self.api_key}

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
