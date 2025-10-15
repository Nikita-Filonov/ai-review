import json
from pathlib import Path

import aiofiles
import pytest

from ai_review.config import settings
from ai_review.libs.config.artifacts import ArtifactsConfig
from ai_review.services.artifacts.service import ArtifactsService


@pytest.mark.asyncio
async def test_save_llm_interaction_creates_file(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        artifacts_service: ArtifactsService
):
    """Checks that a JSON file is created with the correct name and content when LLM saving is enabled."""
    monkeypatch.setattr(settings, "artifacts", ArtifactsConfig(llm_dir=tmp_path, llm_enabled=True))

    artifact_id = await artifacts_service.save_llm_interaction(
        prompt="Hello world",
        prompt_system="system prompt",
        response="model answer"
    )

    assert artifact_id is not None
    artifact_path = tmp_path / f"{artifact_id}.json"
    assert artifact_path.exists(), "Artifact file was not created"

    async with aiofiles.open(artifact_path, "r", encoding="utf-8") as file:
        content = await file.read()
    data = json.loads(content)
    assert data["id"] == artifact_id
    assert data["prompt"] == "Hello world"
    assert data["response"] == "model answer"
    assert data["prompt_system"] == "system prompt"


@pytest.mark.asyncio
async def test_save_llm_interaction_disabled(
        monkeypatch: pytest.MonkeyPatch,
        artifacts_service: ArtifactsService
):
    """Checks that the method returns None and does not create a file if LLM saving is disabled."""
    monkeypatch.setattr(settings, "artifacts", ArtifactsConfig(llm_enabled=False))

    artifact_id = await artifacts_service.save_llm_interaction(
        prompt="ignored",
        prompt_system="ignored",
        response="ignored"
    )

    assert artifact_id is None


@pytest.mark.asyncio
async def test_save_artifact_writes_file(tmp_path: Path, artifacts_service: ArtifactsService):
    """Checks that save_artifact writes content to the given file path."""
    file_path = tmp_path / "test.json"
    content = '{"key": "value"}'

    result = await artifacts_service.save_artifact(file=file_path, content=content, kind="test")

    assert result == file_path
    assert file_path.exists()
    async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
        saved_content = await f.read()
    assert saved_content == content


@pytest.mark.asyncio
async def test_save_artifact_handles_exception(
        monkeypatch: pytest.MonkeyPatch,
        artifacts_service: ArtifactsService
):
    """Checks that save_artifact gracefully returns None on write error."""

    class BrokenAsyncFile:
        async def __aenter__(self):
            raise OSError("disk full")

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            return False

    monkeypatch.setattr(
        "ai_review.services.artifacts.service.aiofiles.open",
        lambda *args, **kwargs: BrokenAsyncFile()
    )

    result = await artifacts_service.save_artifact(Path("/fake/path.json"), "data")
    assert result is None
