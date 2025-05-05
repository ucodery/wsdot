from enum import Enum

from pydantic import BaseModel

from ._json_date import RestDate
from .base import Wsdot


class Adjustement(Enum):
    ADDITION = 0
    CANDELLATION = 1


class Cardinal(Enum):
    WEST = 0
    EAST = 1


class Journey(Enum):
    DEPARTURE = 0
    ARRIVAL = 1


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
    ScheduleStart: RestDate
    ScheduleEnd: RestDate


class FerrySimpleAlert(BaseModel):
    BulletinID: int
    BulletinFlag: bool
    PublishDate: RestDate
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


class FerryRouteAdjustment(BaseModel):
    DateFrom: RestDate
    DateThru: RestDate
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


class FerryDateRange(BaseModel):
    DateFrom: RestDate
    DateThru: RestDate
    EventID: int | None
    EventDescription: str | None


class FerryAnnotation(BaseModel):
    AnnotationID: int
    AnnotationText: str | None
    AnnotationIVRText: str | None
    AdjustedCrossingTime: int | None
    AnnotationImg: str | None
    TypeDescription: str | None
    SortSeq: int


class FerryScheduleAdjustment(BaseModel):
    ScheduleID: int
    SchedRouteID: int
    RouteID: int
    RouteDescription: str | None
    RouteSortSeq: int
    SailingID: int
    SailingDescription: str | None
    ActiveSailingDateRange: FerryDateRange | None
    SailingDir: Cardinal
    JourneyID: int
    VesselID: int
    VesselName: str | None
    VesselHandicapAccessible: bool
    VesselPositionNum: int
    JourneyTerminalID: int
    TerminalID: int
    TerminalDescription: str | None
    TerminalBriefDescription: str | None
    TimeToAdj: RestDate
    AdjDateFrom: RestDate
    AdjDateThru: RestDate
    TidalAdj: bool
    EventID: int | None
    EventDescription: str | None
    DepArrIndicator: Journey
    AdjType: Adjustement
    Annotations: list[FerryAnnotation] | None


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

    async def all_adjustments(self) -> list[FerryScheduleAdjustment]:
        return [
            FerryScheduleAdjustment(**ferry_adjustment)
            for ferry_adjustment in await self.get_json(subpath='timeadj')
        ]

    async def all_routes(self) -> list[FerryRoute]:
        return [
            FerryRoute(**ferry_route)
            for ferry_route in await self.get_json(subpath='schedroutes')
        ]
