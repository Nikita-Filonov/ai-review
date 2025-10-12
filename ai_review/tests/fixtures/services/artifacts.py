from pathlib import Path

import pytest

from ai_review.services.artifacts.service import ArtifactsService
from ai_review.services.artifacts.types import ArtifactsServiceProtocol


class FakeArtifactsService(ArtifactsServiceProtocol):
    def __init__(self):
        self.calls: list[tuple[str, dict]] = []
        self.saved_artifacts: list[tuple[Path, str, str]] = []
        self.saved_llm_interactions: list[dict[str, str | None]] = []

    async def save_llm_interaction(
            self,
            prompt: str,
            prompt_system: str,
            response: str | None = None
    ) -> str:
        self.calls.append((
            "save_llm_interaction",
            {"prompt": prompt, "prompt_system": prompt_system, "response": response},
        ))

        artifact_id = f"fake-{len(self.saved_llm_interactions) + 1}"
        self.saved_llm_interactions.append({
            "id": artifact_id,
            "prompt": prompt,
            "prompt_system": prompt_system,
            "response": response,
        })
        return artifact_id

    async def save_artifact(
            self,
            file: Path,
            content: str,
            kind: str = "artifact"
    ) -> Path:
        self.calls.append((
            "save_artifact",
            {"file": str(file), "content": content, "kind": kind},
        ))

        self.saved_artifacts.append((file, content, kind))
        return file


@pytest.fixture
def fake_artifacts_service() -> FakeArtifactsService:
    return FakeArtifactsService()


@pytest.fixture
def artifacts_service() -> ArtifactsService:
    return ArtifactsService()
