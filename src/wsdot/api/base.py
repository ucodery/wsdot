import abc
import asyncio
import atexit
from typing import Any

import aiohttp

from ..error import WsdotError

__session: aiohttp.ClientSession | None = None


def get_long_lived_session() -> aiohttp.ClientSession:
    global __session
    if __session is None:
        session = aiohttp.ClientSession()

        def close_long_lived_session(ses=session, aio=asyncio):
            try:
                loop = aio.get_event_loop()
                if loop.is_running():
                    loop.create_task(ses.close())
                else:
                    loop.run_until_complete(ses.close())
            except Exception:
                pass

        atexit.register(close_long_lived_session)

        __session = session
    return __session


class Wsdot(abc.ABC):
    def __init__(
        self, api_key: str, *, session: aiohttp.ClientSession | None = None
    ) -> None:
        self.api_key = api_key
        self.session = session if session is not None else get_long_lived_session()

    @property
    @abc.abstractmethod
    def api_url(self) -> str: ...

    @abc.abstractmethod
    def auth_header(self) -> dict[str, str]: ...

    async def get_json(
        self, subpath: str = '', params: dict[Any, Any] | None = None
    ) -> dict[Any, Any]:
        full_params = self.auth_header() | (params if params else {})

        get_url = self.api_url + subpath
        async with self.session.get(get_url, params=full_params) as response:
            if response.status != 200:
                raise WsdotError(
                    'unexpected status', url=get_url, status=response.status
                )
            if not response.content_type == 'application/json':
                raise WsdotError(
                    'unexpected data type', url=get_url, status=response.status
                )
            if not await response.text():
                raise WsdotError('received no data', url=get_url)
            return await response.json()
