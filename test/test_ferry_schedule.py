import itertools

from pydantic import ValidationError
import pytest

from wsdot.api.ferries import FerryAlert, FerryRoute, FerrySeason, WsdotFerrySchedule
from wsdot.error import WsdotError


def endpoint_expansion(endpoint: str, datatype: type, local_data: list[str]):
    return itertools.product(
        [endpoint],
        [datatype],
        local_data,
    )


@pytest.mark.parametrize(
    ['endpoint', 'datatype', 'local_data'],
    [
        *endpoint_expansion(
            'alerts',
            FerryAlert,
            [
                'GetAllAlerts-valid',
                'GetAllAlerts-valid-nulls',
                'empty-list',
            ],
        ),
        *endpoint_expansion(
            'season',
            FerrySeason,
            [
                'GetActiveScheduledSeasons-valid',
                'GetActiveScheduledSeasons-valid-nulls',
                'empty-list',
            ],
        ),
        *endpoint_expansion(
            'all_routes',
            FerryRoute,
            [
                'GetAllSchedRoutes-valid',
                'GetAllSchedRoutes-valid-nulls',
                'GetAllSchedRoutes-valid-sub-nulls',
                'empty-list',
            ],
        ),
    ],
)
@pytest.mark.asyncio
async def test_ferrry_list_data_good(local_session, datatype, endpoint):
    dot = WsdotFerrySchedule(api_key='dead_beef', session=local_session)
    callme = getattr(dot, endpoint)
    all_alerts = await callme()

    assert isinstance(all_alerts, list)
    assert all(isinstance(entry, datatype) for entry in all_alerts)


@pytest.mark.parametrize(
    ['endpoint', 'local_data'],
    [
        ['alerts', 'GetAllAlerts-invalid'],
        ['season', 'GetActiveScheduledSeasons-invalid'],
        ['all_routes', 'GetAllSchedRoutes-invalid'],
    ],
)
@pytest.mark.asyncio
async def test_ferry_data_bad(local_session, endpoint):
    dot = WsdotFerrySchedule(api_key='dead_beef', session=local_session)
    callme = getattr(dot, endpoint)

    with pytest.raises(ValidationError):
        await callme()


@pytest.mark.parametrize(
    ['endpoint', 'local_data'],
    [
        *itertools.product(
            ['alerts', 'season', 'all_routes'],
            ['empty'],
        ),
    ],
)
@pytest.mark.asyncio
async def test_ferry_data_empty(local_session, endpoint):
    dot = WsdotFerrySchedule(api_key='dead_beef', session=local_session)
    callme = getattr(dot, endpoint)

    with pytest.raises(WsdotError):
        await callme()
