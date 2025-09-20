from abc import ABC, abstractmethod

from httpx import Request, Response


class BaseEventHook(ABC):
    @abstractmethod
    async def request(self, request: Request) -> None:
        ...

    @abstractmethod
    async def response(self, response: Response) -> None:
        ...
