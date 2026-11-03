from pydantic import ValidationError
import pytest

from wsdot import TravelTime, WsdotTravelError, WsdotTravelTimes


@pytest.mark.parametrize(
    'local_data',
    [
        'GetTravelTimesAsJson-valid',
        'GetTravelTimesAsJson-valid-nulls',
        'GetTravelTimesAsJson-valid-location-nulls',
        'empty-list',
    ],
)
@pytest.mark.asyncio
async def test_travel_times(local_session):
    dot = WsdotTravelTimes(api_key='dead_beef', session=local_session)
    all_times = await dot.get_all_travel_times()

    assert isinstance(all_times, list)
    assert all(isinstance(entry, TravelTime) for entry in all_times)


@pytest.mark.parametrize(
    'local_data', ['GetTravelTimesAsJson-invalid', 'GetTravelTimesAsJson-invalid-date']
)
@pytest.mark.asyncio
async def test_invalid_travel_times(local_session):
    dot = WsdotTravelTimes(api_key='dead_beef', session=local_session)

    with pytest.raises(ValidationError):
        await dot.get_all_travel_times()


@pytest.mark.parametrize('local_data', ['empty'])
@pytest.mark.asyncio
async def test_empty_travel_times(local_session):
    dot = WsdotTravelTimes(api_key='dead_beef', session=local_session)

    with pytest.raises(WsdotTravelError):
        await dot.get_all_travel_times()


@pytest.mark.parametrize('local_data', ['GetTravelTimeAsJson-valid'])
@pytest.mark.asyncio
async def test_travel_time(local_session):
    dot = WsdotTravelTimes(api_key='dead_beef', session=local_session)
    time = await dot.get_travel_time(1)

    assert isinstance(time, TravelTime)


@pytest.mark.parametrize('local_data', ['GetTravelTimesAsJson-valid'])
@pytest.mark.asyncio
async def test_access_code_sent_over_https(local_session):
    requests = []
    local_get = local_session.get

    def recording_get(url, params=None):
        requests.append((url, params))
        return local_get(url, params)

    local_session.get = recording_get
    dot = WsdotTravelTimes(api_key='dead_beef', session=local_session)
    await dot.get_all_travel_times()

    url, params = requests[0]
    assert params['AccessCode'] == 'dead_beef'
    assert url.startswith('https://')
