from typing import Protocol


class AgentToolServiceProtocol(Protocol):
    async def execute(self, command: str) -> str:
        ...
