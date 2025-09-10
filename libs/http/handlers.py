from functools import wraps
from typing import Callable, Coroutine, Any

from httpx import Response, HTTPStatusError

APIFunc = Callable[..., Coroutine[Any, Any, Response]]


class HTTPClientError(Exception):
    def __init__(self, client: str, details: str, status_code: int):
        self.details = f'[{client}]: {details}'
        self.status_code = status_code

        super().__init__(f"[{client}] {status_code}: {details}")


def handle_http_error(client: str, exception: type[HTTPClientError]):
    def wrapper(func: APIFunc):
        @wraps(func)
        async def inner(*args, **kwargs):
            response = await func(*args, **kwargs)

            try:
                return response.raise_for_status()
            except HTTPStatusError as error:
                raise exception(
                    client=client,
                    details=error.response.text or f'{client} returned error',
                    status_code=error.response.status_code
                ) from error

        return inner

    return wrapper
