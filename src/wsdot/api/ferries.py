"""
# Alerts
An informational message targeted as on of a: communication, bulletin, or `Route` disruption

# Adjustment
Deviations from a pre-planned `Sailings`, both additions and cancellations

# Route
A planned trip along a predetermined path at a scheduled time

# Sailing
The travel of a `Vessel` along a `Route`

## Journey
The travel of a `Vessel` between two `Terminal`.

A Sailing may be made up of multiple journeys when the `Vessel` stops at more than two `Terminal`s
following a `Route`.

# Schedule
Planned travel times along a `Route` between a `TerminalPair`

# TerminalPair
Two `Terminal`s connected by a `Route`
"""
from enum import Enum

from pydantic import BaseModel

from ._json_date import RestDate
from .base import Wsdot

type AlertTypeID = int
type AnnotationID = int
type BulletinID = int
type EventID = int
type JourneyID = int
type JourneyTerminalID = int
type RegionID = int
type ReplacedBySchedRouteID = int
type RouteID = int
type SailingID = int
type ScheduleID = int
type SchedRouteID = int
type TerminalID = int
type VesselID = int
type VesselWatchID = int


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


# NOTE: https://www.wsdot.wa.gov/ferries/api/schedule/documentation/rest.html and
# https://www.wsdot.wa.gov/ferries/api/schedule/rest/help seem to disagree about which fields are nullable

class FerrySimpleSchedule(BaseModel):
    """
    Identifies a planned schedule and for when it is valid
    """
    ScheduleID: ScheduleID
    ScheduleName: str
    ScheduleSeason: Season
    SchedulePDFUrl: str
    ScheduleStart: RestDate
    ScheduleEnd: RestDate

class FerryVessel(BaseModel):
    VesselID: VesselID
    VesselName: str
    VesselHandicapAccessible: bool
    VesselPositionNum: int

class FerryTerminalPairTime(FerryVessel):
    DepartingTime: RestDate
    ArrivingTime: RestDate | None
    LoadingRule: Load
    Routes: list[RouteID]
    AnnotationIndexes: list[AnnotationID]


class FerrySimpleTerminal(BaseModel):
    TerminalID: TerminalID
    Description: str | None


class FerrySimpleTerminalPair(BaseModel):
    DepartingTerminalID: TerminalID
    DepartingTerminalName: str
    ArrivingTerminalID: TerminalID
    ArrivingTerminalName: str


class FerryTerminalPair(FerrySimpleTerminalPair):
    SailingNote: str
    Annotations: list[str]
    Times: list[FerryTerminalPairTime]
    AnnotationsIVR: list[str]


class FerrySchedule(FerrySimpleSchedule):
    AllRoutes: list[RouteID]
    TerminalCompos: list[FerryTerminalPair]


class FerrySimpleAlert(BaseModel):
    BulletinID: BulletinID
    BulletinFlag: bool
    PublishDate: RestDate | None
    DisruptionDescription: str


class FerryRouteAlert(FerrySimpleAlert):
    CommunicationFlag: bool
    AlertDescription: str | None
    AlertFullTitle: str | None
    AlertFullText: str | None
    IVRText: str | None


class FerryAlert(FerrySimpleAlert):
    """
    A communication about Washington State Ferries Services
    """
    BulletinText: str | None
    CommunicationFlag: bool
    CommunicationText: str | None
    RouteAlertFlag: bool
    RouteAlertText: str | None
    HomepageAlertText: str | None
    AllRoutesFlag: bool
    SortSeq: int
    AlertTypeID: AlertTypeID
    AlertType: str
    AlertFullTitle: str
    AffectedRouteIDs: list[RouteID] | None
    IVRText: str | None


class FerryRouteAdjustment(BaseModel):
    DateFrom: RestDate
    DateThru: RestDate
    EventID: EventID | None
    EventDescription: str | None
    AdjType: Adjustement
    ReplacedBySchedRouteID: ReplacedBySchedRouteID | None


class BasicRoute(BaseModel):
    RouteID: RouteID
    RouteAbbrev: str
    Description: str
    RegionID: RegionID


class FerrySimpleRoute(BasicRoute):
    """
    Identifies a planned route and any interruptions
    """
    ServiceDisruptions: list[FerrySimpleAlert] | None


class FerryActiveRoute(FerrySimpleRoute):
    """
    Identifies a planned route that is scheduled to run as well as any interruptions or alterations
    """
    ScheduleID: ScheduleID
    SchedRouteID: SchedRouteID
    ContingencyOnly: bool
    SeasonalRouteNotes: str | None
    ContingencyAdj: list[FerryRouteAdjustment] | None


class FerryRoute(BasicRoute):
    VesselWatchID: VesselWatchID
    ReservationFlag: bool
    InternationalFlag: bool
    PassengerOnlyFlag: bool
    CrossingTime: str | None
    AdaNotes: str | None
    GeneralRouteNotes: str | None
    SeasonalRouteNotes: str | None
    Alerts: list[FerryRouteAlert] | None


class FerryDateRange(BaseModel):
    DateFrom: RestDate
    DateThru: RestDate
    EventID: EventID | None
    EventDescription: str | None


class FerryAnnotation(BaseModel):
    AnnotationID: AnnotationID
    AnnotationText: str
    AnnotationIVRText: str
    AdjustedCrossingTime: int | None
    AnnotationImg: str
    TypeDescription: str
    SortSeq: int


class FerrySimpleSailing(BaseModel):
    ScheduleID: ScheduleID
    SchedRouteID: SchedRouteID
    RouteID: RouteID
    SailingID: SailingID
    SailingDescription: str
    SailingDir: Cardinal


class FerryScheduleAdjustment(FerrySimpleSailing, FerryVessel):
    """
    Represents either an addition or a cancellation to an active route
    """
    RouteDescription: str
    RouteSortSeq: int
    ActiveSailingDateRange: FerryDateRange | None
    JourneyID: JourneyID
    JourneyTerminalID: JourneyTerminalID
    TerminalID: TerminalID
    TerminalDescription: str
    TerminalBriefDescription: str
    TimeToAdj: RestDate
    AdjDateFrom: RestDate
    AdjDateThru: RestDate
    TidalAdj: bool
    EventID: EventID | None
    EventDescription: str | None
    DepArrIndicator: Journey
    AdjType: Adjustement
    Annotations: list[FerryAnnotation] | None


class FerryScheduleTimes(BaseModel):
    JourneyTerminalID: JourneyTerminalID
    TerminalID: TerminalID
    TerminalDescription: str | None
    TerminalBriefDescription: str | None
    Time: RestDate
    DepArrIndicator: Journey
    IsNA: bool
    Annotations: list[FerryAnnotation] | None


class FerryJourney(FerryVessel):
    JourneyID: JourneyID
    ReservationInd: bool
    InternationalInd: bool
    InterislandInd: bool
    TerminalTimes: list[FerryScheduleTimes] | None


class FerrySailing(FerrySimpleSailing):
    SailingNotes: str | None
    DisplayColNum: int
    DayOpDescription: str | None
    DayOpUseForHoliday: bool
    ActiveDateRanges: list[FerryDateRange] | None
    Journs: list[FerryJourney] | None


class WsdotFerrySchedule(Wsdot):
    api_url = 'http://wsdot.wa.gov/Ferries/API/Schedule/rest/'

    def auth_header(self) -> dict[str, str]:
        return {'apiaccesscode': self.api_key}

    async def all_alerts(self) -> list[FerryAlert]:
        """Return all current alerts."""
        return [
            FerryAlert(**ferry_alert)
            for ferry_alert in await self.get_json(subpath='alerts')
        ]

    async def all_adjustments(
        self, *, route_id: RouteID | None = None, schedule_id: ScheduleID | None = None
    ) -> list[FerryScheduleAdjustment]:
        """Return all additions and cancellations for either a specific Route or Schedule

        Exactly one of either `route_id` or `schedule_id` must be provided. These IDs can
        be discovered by calling either `all_routes()` or `all_schedules()`.
        """
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
        Return all active schedules

        FerrySimpleSchedule is a subset of the information returned by FerrySchedule. Consider calling
        schedule() if you already know the RouteID or TerminalIDs for a more complete type
        """
        return [
            FerrySimpleSchedule(**ferry_season)
            for ferry_season in await self.get_json(subpath='activeseasons')
        ]

    async def schedule(
        self,
        trip_date: str,
        *,
        route_id: RouteID | None = None,
        departing_terminal_id: TerminalID | None = None,
        arriving_terminal_id: TerminalID | None = None,
    ) -> FerrySchedule:
        """
        Return the schedule for either a specific Route or a pair of Terminals.

        Exactly one of either `route_id` or `departing_terminal_id` and `arriving_terminal_id` must
        be provided. These IDs can be discovered by calling either `all_routes()` or
        `all_terminal_pairs()`.
        """
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
        departing_terminal_id: TerminalID | None = None,
        arriving_terminal_id: TerminalID | None = None,
    ) -> list[FerrySimpleRoute]:
        """
        Return all routes

        FerrySimpleRoute is a subset of the information returned by FerryActiveRoute and FerryRoute.
        Consider calling active_routes() if you already know the ScheduleID, or routes() if you
        already know the RouteID or TerminalIDs for a more complete type.
        """
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

    async def active_routes(self, schedule_id: ScheduleID | None = None) -> list[FerryActiveRoute]:
        """
        Return all routes for a schedule or season
        """
        subpath = 'schedroutes'
        if schedule_id is not None:
            subpath = f'{subpath}/{schedule_id}'
        return [
            FerryActiveRoute(**ferry_route)
            for ferry_route in await self.get_json(subpath=subpath)
        ]


    async def route(self, trip_date, route_id) => FerryRoute:


    async def routes(
        self,
        trip_date=str,
        *,
        route_id: RouteID | None = None,
        departing_terminal_id: TerminalID | None = None,
        arriving_terminal_id: TerminalID | None = None,
    ) -> list[FerryRoute]:
        """
        Return all routes active for a particular date
        """
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
            FerryRoute(**ferry_route)
            for ferry_route in await self.get_json(subpath=subpath)
        ]

    async def all_sailings(self, schedule_route_id: SchedRouteID) -> list[FerrySailing]:
        # Note: there is also /sailings/{schedule_route_id} which returns list[FerrySailing]. How is this different?
        return [
            FerrySailing(**ferry_sailing)
            for ferry_sailing in await self.get_json(
                subpath=f'allsailings/{schedule_route_id}'
            )
        ]

    async def all_terminal_pairs(
        self, trip_date: str, route_id: RouteID | None = None
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
