class WsdotError(Exception):
    def __init__(
        self, msg: str = '', url: str | None = None, status: int | None = None
    ) -> None:
        self.msg = msg
        self.url = url
        self.status = status

    def __str__(self) -> str:
        message = self.msg
        if self.url:
            message = f'{message}{" " if message else ""}calling {self.url}'
            if self.status is not None:
                message = f'{message} got {self.status}'
        return message
