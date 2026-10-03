from pathlib import Path

import pytest
from pydantic import BaseModel

from ai_review.services.artifacts.schema.base import ArtifactType, BaseArtifactSchema
from ai_review.tests.fixtures.services.artifacts import FakeArtifactsService


@pytest.mark.asyncio
async def test_artifact_fake_records_raw_save(tmp_path: Path) -> None:
    fake = FakeArtifactsService()

    class EmptyData(BaseModel):
        pass

    artifact = BaseArtifactSchema(type=ArtifactType.LLM, data=EmptyData())
    assert await fake.save(artifact, tmp_path, True) == "fake-id"
    assert fake.calls[-1][1] == {
        "artifact": artifact,
        "artifacts_dir": tmp_path,
        "artifacts_enabled": True,
    }
