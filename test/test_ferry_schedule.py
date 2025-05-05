import itertools

from pydantic import ValidationError
import pytest

from wsdot.api.ferries import (
    FerryAlert,
    FerryRoute,
    FerryScheduleAdjustment,
    FerrySeason,
    WsdotFerrySchedule,
)
from wsdot.error import WsdotError


@pytest.mark.parametrize(
    ['endpoint', 'datatype', 'local_data'],
    [
        *itertools.product(
            ['alerts'],
            [FerryAlert],
            [
                'GetAllAlerts-valid',
                'GetAllAlerts-valid-nulls',
                'empty-list',
            ],
        ),
        *itertools.product(
            ['season'],
            [FerrySeason],
            [
                'GetActiveScheduledSeasons-valid',
                'GetActiveScheduledSeasons-valid-nulls',
                'empty-list',
            ],
        ),
        *itertools.product(
            ['all_routes'],
            [FerryRoute],
            [
                'GetAllSchedRoutes-valid',
                'GetAllSchedRoutes-valid-nulls',
                'GetAllSchedRoutes-valid-sub-nulls',
                'empty-list',
            ],
        ),
        *itertools.product(
            ['all_adjustments'],
            [FerryScheduleAdjustment],
            [
                'GetAllTimeAdj-valid',
                'GetAllTimeAdj-valid-nulls',
                'GetAllTimeAdj-valid-sub-nulls',
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
        ['all_adjustments', 'GetAllTimeAdj-invalid'],
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
            ['alerts', 'season', 'all_routes', 'all_adjustments'],
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
