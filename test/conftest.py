from contextlib import asynccontextmanager
from functools import partial
import json
import os
import unittest.mock

import aiohttp
import pytest


@asynccontextmanager
async def local_get(url, params=None, *, local_data=''):
    data_path = os.path.join(
        os.path.dirname(__file__),
        'data',
        local_data,
    )
    with open(data_path) as response:
        data = response.read()

    class response:
        status = 200
        content_type = 'application/json' if data else 'application/octet-stream'

        async def json():
            return json.loads(data)

        async def text():
            return data

    yield response


@pytest.fixture
def local_session(local_data):
    local = unittest.mock.MagicMock(spec=aiohttp.ClientResponse)
    local.get = partial(local_get, local_data=local_data)
    return local
