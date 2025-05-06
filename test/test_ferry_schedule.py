from pydantic import ValidationError
import pytest

from wsdot.api.ferries import (
    FerryAlert,
    FerryRoute,
    FerrySailing,
    FerryScheduleAdjustment,
    FerrySeason,
    WsdotFerrySchedule,
)
from wsdot.error import WsdotError


@pytest.mark.parametrize(
    ['endpoint', 'args', 'local_data', 'datatype'],
    [
        ('alerts', (), 'GetAllAlerts-valid', FerryAlert),
        ('alerts', (), 'GetAllAlerts-valid-nulls', FerryAlert),
        ('alerts', (), 'empty-list', FerryAlert),
        ('season', (), 'GetActiveScheduledSeasons-valid', FerrySeason),
        ('season', (), 'GetActiveScheduledSeasons-valid-nulls', FerrySeason),
        ('season', (), 'empty-list', FerrySeason),
        ('all_routes', (), 'GetAllSchedRoutes-valid', FerryRoute),
        ('all_routes', (), 'GetAllSchedRoutes-valid-nulls', FerryRoute),
        ('all_routes', (), 'GetAllSchedRoutes-valid-sub-nulls', FerryRoute),
        ('all_routes', (), 'empty-list', FerryRoute),
        ('all_adjustments', (), 'GetAllTimeAdj-valid-nulls', FerryScheduleAdjustment),
        (
            'all_adjustments',
            (),
            'GetAllTimeAdj-valid-sub-nulls',
            FerryScheduleAdjustment,
        ),
        ('all_adjustments', (), 'GetAllTimeAdj-valid', FerryScheduleAdjustment),
        ('all_adjustments', (), 'empty-list', FerryScheduleAdjustment),
        ('all_sailings', (1,), 'GetAllSchedSailingsBySchedRoute-valid', FerrySailing),
        (
            'all_sailings',
            (1,),
            'GetAllSchedSailingsBySchedRoute-valid-nulls',
            FerrySailing,
        ),
        (
            'all_sailings',
            (1,),
            'GetAllSchedSailingsBySchedRoute-valid-sub-nulls',
            FerrySailing,
        ),
        ('all_sailings', (1,), 'empty-list', FerrySailing),
    ],
)
@pytest.mark.asyncio
async def test_ferrry_list_data_good(endpoint, args, local_session, datatype):
    dot = WsdotFerrySchedule(api_key='dead_beef', session=local_session)
    callme = getattr(dot, endpoint)
    all_alerts = await callme(*args)

    assert isinstance(all_alerts, list)
    assert all(isinstance(entry, datatype) for entry in all_alerts)


@pytest.mark.parametrize(
    ['endpoint', 'args', 'local_data', 'errortype'],
    [
        ('alerts', (), 'GetAllAlerts-invalid', ValidationError),
        ('alerts', (), 'empty', WsdotError),
        ('season', (), 'GetActiveScheduledSeasons-invalid', ValidationError),
        ('season', (), 'empty', WsdotError),
        ('all_routes', (), 'GetAllSchedRoutes-invalid', ValidationError),
        ('all_routes', (), 'empty', WsdotError),
        ('all_adjustments', (), 'GetAllTimeAdj-invalid', ValidationError),
        ('all_adjustments', (), 'empty', WsdotError),
        (
            'all_sailings',
            (1,),
            'GetAllSchedSailingsBySchedRoute-invalid',
            ValidationError,
        ),
        ('all_sailings', (1,), 'empty', WsdotError),
    ],
)
@pytest.mark.asyncio
async def test_ferry_data_bad(endpoint, args, local_session, errortype):
    dot = WsdotFerrySchedule(api_key='dead_beef', session=local_session)
    callme = getattr(dot, endpoint)

    with pytest.raises(errortype):
        await callme(*args)
