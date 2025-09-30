from pathlib import Path
from typing import Protocol


class ArtifactsServiceProtocol(Protocol):
    async def save_llm_interaction(
            self,
            prompt: str,
            prompt_system: str,
            response: str | None = None
    ) -> str | None:
        ...

    async def save_artifact(
            self,
            file: Path,
            content: str,
            kind: str = "artifact"
    ) -> Path | None:
        ...
