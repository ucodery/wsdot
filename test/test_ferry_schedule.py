from pydantic import ValidationError
import pytest

from wsdot.api.ferries import (
    FerryAlert,
    FerryRoute,
    FerrySimpleRoute,
    FerrySailing,
    FerryScheduleAdjustment,
    FerrySimpleSchedule,
    WsdotFerrySchedule,
)
from wsdot.error import WsdotError


@pytest.mark.parametrize(
    ['endpoint', 'args', 'local_data', 'datatype'],
    [
        ('all_alerts', (), 'GetAllAlerts-valid', FerryAlert),
        ('all_alerts', (), 'GetAllAlerts-valid-nulls', FerryAlert),
        ('all_alerts', (), 'empty-list', FerryAlert),
        ('all_schedules', (), 'GetActiveScheduledSeasons-valid', FerrySimpleSchedule),
        (
            'all_schedules',
            (),
            'GetActiveScheduledSeasons-valid-nulls',
            FerrySimpleSchedule,
        ),
        ('all_schedules', (), 'empty-list', FerrySimpleSchedule),
        ('all_routes', ('today',), 'GetAllRoutes-valid', FerrySimpleRoute),
        ('all_routes', ('today',), 'GetAllRoutes-valid-nulls', FerrySimpleRoute),
        ('all_routes', ('today',), 'GetAllRoutes-valid-sub-nulls', FerrySimpleRoute),
        ('all_routes', ('today',), 'empty-list', FerrySimpleRoute),
        ('all_routes', ('today', 1, 2), 'GetAllRoutes-valid', FerrySimpleRoute),
        ('all_routes', ('today', 1, 2), 'GetAllRoutes-valid-nulls', FerrySimpleRoute),
        (
            'all_routes',
            ('today', 1, 2),
            'GetAllRoutes-valid-sub-nulls',
            FerrySimpleRoute,
        ),
        ('all_routes', ('today', 1, 2), 'empty-list', FerrySimpleRoute),
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
        ('routes', (), 'GetAllSchedRoutes-valid', FerryRoute),
        ('routes', (), 'GetAllSchedRoutes-valid-nulls', FerryRoute),
        ('routes', (), 'GetAllSchedRoutes-valid-sub-nulls', FerryRoute),
        ('routes', (), 'empty-list', FerryRoute),
        ('routes', (1,), 'GetAllSchedRoutes-valid', FerryRoute),
        ('routes', (1,), 'GetAllSchedRoutes-valid-nulls', FerryRoute),
        ('routes', (1,), 'GetAllSchedRoutes-valid-sub-nulls', FerryRoute),
        ('routes', (1,), 'empty-list', FerryRoute),
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
        ('all_alerts', (), 'GetAllAlerts-invalid', ValidationError),
        ('all_alerts', (), 'empty', WsdotError),
        ('all_schedules', (), 'GetActiveScheduledSeasons-invalid', ValidationError),
        ('all_schedules', (), 'empty', WsdotError),
        ('all_routes', ('today',), 'GetAllRoutes-invalid', ValidationError),
        ('all_routes', ('today',), 'empty', WsdotError),
        ('all_routes', ('today', 1, 2), 'GetAllRoutes-invalid', ValidationError),
        ('all_routes', ('today', 1, 2), 'empty', WsdotError),
        ('all_adjustments', (), 'GetAllTimeAdj-invalid', ValidationError),
        ('all_adjustments', (), 'empty', WsdotError),
        (
            'all_sailings',
            (1,),
            'GetAllSchedSailingsBySchedRoute-invalid',
            ValidationError,
        ),
        ('all_sailings', (1,), 'empty', WsdotError),
        ('routes', (), 'GetAllSchedRoutes-invalid', ValidationError),
        ('routes', (), 'empty', WsdotError),
        ('routes', (1,), 'GetAllSchedRoutes-invalid', ValidationError),
        ('routes', (1,), 'empty', WsdotError),
    ],
)
@pytest.mark.asyncio
async def test_ferry_data_bad(endpoint, args, local_session, errortype):
    dot = WsdotFerrySchedule(api_key='dead_beef', session=local_session)
    callme = getattr(dot, endpoint)

    with pytest.raises(errortype):
        await callme(*args)
