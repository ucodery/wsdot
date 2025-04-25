from pydantic import ValidationError
import pytest

from wsdot.api.ferries import FerryAlert, WsdotFerrySchedule
from wsdot.error import WsdotError


@pytest.mark.parametrize(
    'local_data',
    [
        'GetAllAlerts-valid',
        'GetAllAlerts-valid-nulls',
        'empty-list',
    ],
)
@pytest.mark.asyncio
async def test_ferrry_alerts(local_session):
    dot = WsdotFerrySchedule(api_key='dead_beef', session=local_session)
    all_alerts = await dot.get_alerts()

    assert isinstance(all_alerts, list)
    assert all(isinstance(entry, FerryAlert) for entry in all_alerts)


@pytest.mark.parametrize('local_data', ['GetAllAlerts-invalid'])
@pytest.mark.asyncio
async def test_invalid_ferry_alerts(local_session):
    dot = WsdotFerrySchedule(api_key='dead_beef', session=local_session)

    with pytest.raises(ValidationError):
        await dot.get_alerts()


@pytest.mark.parametrize('local_data', ['empty'])
@pytest.mark.asyncio
async def test_empty_ferrry_alerts(local_session):
    dot = WsdotFerrySchedule(api_key='dead_beef', session=local_session)

    with pytest.raises(WsdotError):
        await dot.get_alerts()
