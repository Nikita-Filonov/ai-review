from typing import Protocol


class ReviewRunnerProtocol(Protocol):
    async def run(self) -> None:
        ...
