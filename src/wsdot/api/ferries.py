from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, PlainValidator

from ._json_date import _parse_datetime
from .base import Wsdot


class FerryAlert(BaseModel):
    BulletinID: int
    BulletinFlag: bool
    BulletinText: str | None
    CommunicationFlag: bool
    CommunicationText: str | None
    RouteAlertFlag: bool
    RouteAlertText: str | None
    HomepageAlertText: str | None
    PublishDate: Annotated[datetime, PlainValidator(_parse_datetime)]
    DisruptionDescription: str | None
    AllRoutesFlag: bool
    SortSeq: int
    AlertTypeID: int
    AlertType: str | None
    AlertFullTitle: str | None
    AffectedRouteIDs: list[int] | None
    IVRText: str | None


class WsdotFerrySchedule(Wsdot):
    api_url = 'http://wsdot.wa.gov/Ferries/API/Schedule/rest/'

    def auth_header(self) -> dict[str, str]:
        return {'apiaccesscode': self.api_key}

    async def get_alerts(self) -> list[FerryAlert]:
        return [
            FerryAlert(**ferry_alert)
            for ferry_alert in await self.get_json(subpath='alerts')
        ]
