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


class Load(Enum):
    PASSENGER = 0
    VEHICLE = 1
    BOTH = 2


class FerrySimpleSchedule(BaseModel):
    ScheduleID: int
    ScheduleName: str | None
    ScheduleSeason: Season
    SchedulePDFUrl: str | None
    ScheduleStart: RestDate
    ScheduleEnd: RestDate


class FerryTerminalPairTime(BaseModel):
    DepartingTime: RestDate
    ArrivingTime: RestDate | None
    LoadingRule: Load
    VesselID: int
    VesselName: str | None
    VesselHandicapAccessible: bool
    VesselPositionNum: int
    Routes: list[int] | None
    AnnotationIndexes: list[int] | None


class FerrySimpleTerminal(BaseModel):
    TerminalID: int
    Description: str | None


class FerrySimpleTerminalPair(BaseModel):
    DepartingTerminalID: int
    DepartingTerminalName: str | None
    ArrivingTerminalID: int
    ArrivingTerminalName: str | None


class FerryTerminalPair(FerrySimpleTerminalPair):
    SailingNote: str | None
    Annotations: list[str | None] | None
    Times: list[FerryTerminalPairTime] | None
    AnnotationsIVR: list[str | None] | None


class FerrySchedule(FerrySimpleSchedule):
    AllRoutes: list[int] | None
    TerminalCompos: list[FerryTerminalPair]


class FerrySimpleAlert(BaseModel):
    BulletinID: int
    BulletinFlag: bool
    PublishDate: RestDate
    DisruptionDescription: str | None


class FerryAlertD(FerrySimpleAlert):
    CommunicationFlag: bool
    AlertDescription: str | None
    AlertFullTitle: str | None
    AlertFullText: str | None
    IVRText: str | None


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


class BasicRoute(BaseModel):
    RouteID: int
    RouteAbbrev: str | None
    Description: str | None
    RegionID: int


class FerrySimpleRoute(BasicRoute):
    ServiceDisruptions: list[FerrySimpleAlert] | None


class FerryRoute(FerrySimpleRoute):
    ScheduleID: int
    SchedRouteID: int
    ContingencyOnly: bool
    SeasonalRouteNotes: str | None
    ContingencyAdj: list[FerryRouteAdjustment] | None


class FerryRouteD(BasicRoute):
    VesselWatchID: int
    ReservationFlag: bool
    InternationalFlag: bool
    PassengerOnlyFlag: bool
    CrossingTime: str | None
    AdaNotes: str | None
    GeneralRouteNotes: str | None
    SeasonalRouteNotes: str | None
    Alerts: list[FerryAlertD] | None


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


class FerryScheduleTimes(BaseModel):
    JourneyTerminalID: int
    TerminalID: int
    TerminalDescription: str | None
    TerminalBriefDescription: str | None
    Time: RestDate
    DepArrIndicator: Journey
    IsNA: bool
    Annotations: list[FerryAnnotation] | None


class FerryJourney(BaseModel):
    JourneyID: int
    ReservationInd: bool
    InternationalInd: bool
    InterislandInd: bool
    VesselID: int
    VesselName: str | None
    VesselHandicapAccessible: bool
    VesselPositionNum: int
    TerminalTimes: list[FerryScheduleTimes] | None


class FerrySailing(BaseModel):
    ScheduleID: int
    SchedRouteID: int
    RouteID: int
    SailingID: int
    SailingDescription: str | None
    SailingNotes: str | None
    DisplayColNum: int
    SailingDir: Cardinal
    DayOpDescription: str | None
    DayOpUseForHoliday: bool
    ActiveDateRanges: list[FerryDateRange] | None
    Journs: list[FerryJourney] | None


class WsdotFerrySchedule(Wsdot):
    api_url = 'http://wsdot.wa.gov/Ferries/API/Schedule/rest/'

    def auth_header(self) -> dict[str, str]:
        return {'apiaccesscode': self.api_key}

    async def all_alerts(self) -> list[FerryAlert]:
        return [
            FerryAlert(**ferry_alert)
            for ferry_alert in await self.get_json(subpath='alerts')
        ]

    async def all_adjustments(
        self, *, route_id: int | None = None, schedule_id: int | None = None
    ) -> list[FerryScheduleAdjustment]:
        if route_id is not None and schedule_id is not None:
            raise ValueError(
                'all_adjustments must be called with one of route_id or schedule_id or neither'
            )
        if route_id is not None:
            subpath = f'timeadjbyroute/{route_id}'
        if schedule_id is not None:
            subpath = f'timeadjbyschedroute/{schedule_id}'
        else:
            subpath = 'timeadj'
        return [
            FerryScheduleAdjustment(**ferry_adjustment)
            for ferry_adjustment in await self.get_json(subpath=subpath)
        ]

    async def all_schedules(self) -> list[FerrySimpleSchedule]:
        """
        FerrySimpleSchedule is a subset of the information returned by FerrySchedule. Consider calling
        schedule() if you already know the route ID or terminal IDs for a more complete type
        """
        return [
            FerrySimpleSchedule(**ferry_season)
            for ferry_season in await self.get_json(subpath='activeseasons')
        ]

    async def schedule(
        self,
        trip_date: str,
        *,
        route_id: int | None = None,
        departing_terminal_id: int | None = None,
        arriving_terminal_id: int | None = None,
    ) -> FerrySchedule:
        # Note: there is also /scheduletoday/{route_id_or_two_terminals}, probably not necessary?
        # could make trip_date default to today
        if route_id is not None:
            if departing_terminal_id is not None or arriving_terminal_id is not None:
                raise ValueError(
                    'schedule must be called with either route_id or departing_terminal_id and arriving_terminal_id'
                )
            subpath = f'schedule/{trip_date}/{route_id}'
        elif departing_terminal_id is None or arriving_terminal_id is None:
            raise ValueError(
                'schedule must be called with both departing_terminal_id and arriving_terminal_id'
            )
        else:
            subpath = (
                f'schedule/{trip_date}/{departing_terminal_id}/{arriving_terminal_id}'
            )

        return FerrySchedule(**(await self.get_json(subpath=subpath)))

    async def all_routes(
        self,
        trip_date: str,
        departing_terminal_id: int | None = None,
        arriving_terminal_id: int | None = None,
    ) -> list[FerrySimpleRoute]:
        # Note: there is also /routeshavingservicedisruptions/{trip_date} which is just the simple
        # form of /routes/{trip_date} joined with /timeadjbyroute/{route_id}
        if (departing_terminal_id is None and arriving_terminal_id is not None) or (
            departing_terminal_id is not None and arriving_terminal_id is None
        ):
            raise ValueError(
                'all_routes must be called with either both departing_terminal_id and arriving_terminal_id or neither'
            )
        subpath = f'routes/{trip_date}'
        if departing_terminal_id is not None:
            subpath = f'{subpath}/{departing_terminal_id}/{arriving_terminal_id}'
        return [
            FerrySimpleRoute(**ferry_route)
            for ferry_route in await self.get_json(subpath=subpath)
        ]

    async def routes(self, schedule_id: int | None = None) -> list[FerryRoute]:
        subpath = 'schedroutes'
        if schedule_id is not None:
            subpath = f'{subpath}/{schedule_id}'
        return [
            FerryRoute(**ferry_route)
            for ferry_route in await self.get_json(subpath=subpath)
        ]

    async def route_ds(
        self,
        trip_date=str,
        *,
        route_id: int | None = None,
        departing_terminal_id: int | None = None,
        arriving_terminal_id: int | None = None,
    ) -> list[FerryRouteD]:
        if route_id is not None:
            if departing_terminal_id is not None or arriving_terminal_id is not None:
                raise ValueError(
                    'route_ds must be called with either route_id or departing_terminal_id and arriving_terminal_id'
                )
            subpath = f'routedetails/{trip_date}/{route_id}'
        else:
            if (departing_terminal_id is None and arriving_terminal_id is not None) or (
                departing_terminal_id is not None and arriving_terminal_id is None
            ):
                raise ValueError(
                    'route_ds must be called with both departing_terminal_id and arriving_terminal_id'
                )
            elif departing_terminal_id is not None:
                subpath = f'routedetails/{trip_date}/{departing_terminal_id}/{arriving_terminal_id}'
            else:
                subpath = f'routedetails/{trip_date}'

        return [
            FerryRouteD(**ferry_route)
            for ferry_route in await self.get_json(subpath=subpath)
        ]

    async def all_sailings(self, schedule_route_id: int) -> list[FerrySailing]:
        # Note: there is also /sailings/{schedule_route_id} which returns list[FerrySailing]. How is this different?
        return [
            FerrySailing(**ferry_sailing)
            for ferry_sailing in await self.get_json(
                subpath=f'allsailings/{schedule_route_id}'
            )
        ]

    async def all_terminal_pairs(
        self, trip_date: str, route_id: int | None = None
    ) -> list[FerrySimpleTerminalPair]:
        # Note: /terminals{trip_date} can return a list[FerrySimpleTerminal]
        # Note: /terminalmates{trip_date}/{terminal_id} can return a list[FerrySimpleTerminal]
        if route_id is None:
            subpath = f'terminalsandmates/{trip_date}'
        else:
            subpath = f'terminalsandmatesbyroute/{trip_date}/{route_id}'

        return [
            FerrySimpleTerminalPair(**linked_terminals)
            for linked_terminals in await self.get_json(subpath=subpath)
        ]


# /alternativeformats/{SubjectName}
# /cacheflushdate
# /validdaterange
