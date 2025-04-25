from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, PlainValidator

from ._json_date import _parse_datetime
from .base import Wsdot


class Season(Enum):
    SPRING = 0
    SUMMER = 1
    FALL = 2
    WINTER = 3


class FerrySeason(BaseModel):
    ScheduleID: int
    ScheduleName: str | None
    ScheduleSeason: Season
    SchedulePDFUrl: str | None
    ScheduleStart: Annotated[datetime, PlainValidator(_parse_datetime)]
    ScheduleEnd: Annotated[datetime, PlainValidator(_parse_datetime)]


class FerrySimpleAlert(BaseModel):
    BulletinID: int
    BulletinFlag: bool
    PublishDate: Annotated[datetime, PlainValidator(_parse_datetime)]
    DisruptionDescription: str | None


class FerryAlert(FerrySimpleAlert):
    BulletinText: str | None
    CommunicationFlag: bool
    CommunicationText: str | None
    RouteAlertFlag: bool
    RouteAlertText: str | None
    HomepageAlertText: str | None
    AllRoutesFlag: bool
    SortSeq: int
    AlertTypeID: int
    AlertType: str | None
    AlertFullTitle: str | None
    AffectedRouteIDs: list[int] | None
    IVRText: str | None


class Adjustement(Enum):
    ADDITION = 0
    CANDELLATION = 1


class FerryRouteAdjustment(BaseModel):
    DateFrom: Annotated[datetime, PlainValidator(_parse_datetime)]
    DateThru: Annotated[datetime, PlainValidator(_parse_datetime)]
    EventID: int | None
    EventDescription: str | None
    AdjType: Adjustement
    ReplacedBySchedRouteID: int | None


class FerryRoute(BaseModel):
    ScheduleID: int
    SchedRouteID: int
    ContingencyOnly: bool
    RouteID: int
    RouteAbbrev: str | None
    Description: str | None
    SeasonalRouteNotes: str | None
    RegionID: int
    ServiceDisruptions: list[FerrySimpleAlert] | None
    ContingencyAdj: list[FerryRouteAdjustment] | None


class WsdotFerrySchedule(Wsdot):
    api_url = 'http://wsdot.wa.gov/Ferries/API/Schedule/rest/'

    def auth_header(self) -> dict[str, str]:
        return {'apiaccesscode': self.api_key}

    # /activeseasons is abbreviated /schedule

    async def season(self) -> list[FerrySeason]:
        """
        FerrySeason is a subset of the information returned by FerrySchedule. Consider calling
        season() if you already know the terminal or route IDs for a more complete type
        """
        return [
            FerrySeason(**ferry_season)
            for ferry_season in await self.get_json(subpath='activeseasons')
        ]

    async def alerts(self) -> list[FerryAlert]:
        return [
            FerryAlert(**ferry_alert)
            for ferry_alert in await self.get_json(subpath='alerts')
        ]

    async def all_routes(self) -> list[FerryRoute]:
        return [
            FerryRoute(**ferry_route)
            for ferry_route in await self.get_json(subpath='schedroutes')
        ]
