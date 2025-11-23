import json
from pathlib import Path

import aiofiles
import pytest

from ai_review.config import settings
from ai_review.libs.config.artifacts import ArtifactsConfig
from ai_review.services.artifacts.schema.llm import LLMArtifactSchema, LLMArtifactDataSchema
from ai_review.services.artifacts.service import ArtifactsService
from ai_review.services.cost.schema import CostReportSchema
from ai_review.services.review.internal.inline.schema import InlineCommentSchema
from ai_review.services.review.internal.inline_reply.schema import InlineCommentReplySchema
from ai_review.services.review.internal.summary.schema import SummaryCommentSchema
from ai_review.services.review.internal.summary_reply.schema import SummaryCommentReplySchema


@pytest.mark.asyncio
async def test_save_creates_file(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        artifacts_service: ArtifactsService
):
    monkeypatch.setattr(
        settings,
        "artifacts",
        ArtifactsConfig(
            llm_dir=tmp_path,
            vcs_dir=tmp_path,
            llm_enabled=True,
            vcs_enabled=True,
        )
    )

    artifact = LLMArtifactSchema(
        data=LLMArtifactDataSchema(
            prompt="p",
            response="r",
            prompt_system="sys"
        )
    )

    out = await artifacts_service.save(
        artifact=artifact,
        artifacts_dir=tmp_path,
        artifacts_enabled=True,
    )

    assert out is not None
    file = tmp_path / f"{artifact.id}.json"
    assert file.exists()

    async with aiofiles.open(file, "r", encoding="utf-8") as f:
        data = json.loads(await f.read())

    assert data["id"] == str(artifact.id)
    assert data["type"] == artifact.type
    assert data["data"]["prompt"] == "p"


@pytest.mark.asyncio
async def test_save_disabled(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        artifacts_service: ArtifactsService
):
    monkeypatch.setattr(
        settings,
        "artifacts",
        ArtifactsConfig(
            llm_dir=tmp_path,
            vcs_dir=tmp_path,
            llm_enabled=False,
        )
    )

    artifact = LLMArtifactSchema(
        data=LLMArtifactDataSchema(prompt="p", response="r", prompt_system="sys")
    )

    out = await artifacts_service.save(
        artifact=artifact,
        artifacts_dir=tmp_path,
        artifacts_enabled=False,
    )

    assert out is None
    assert not list(tmp_path.iterdir())


@pytest.mark.asyncio
async def test_save_handles_write_error(monkeypatch: pytest.MonkeyPatch, artifacts_service: ArtifactsService):
    class BrokenFile:
        async def __aenter__(self): raise OSError("disk full")

        async def __aexit__(self, *a): return False

    monkeypatch.setattr(
        "ai_review.services.artifacts.service.aiofiles.open",
        lambda *a, **k: BrokenFile()
    )

    artifact = LLMArtifactSchema(
        data=LLMArtifactDataSchema(prompt="p", response="r", prompt_system="sys")
    )

    result = await artifacts_service.save(
        artifact=artifact,
        artifacts_dir=Path("/does/not/matter"),
        artifacts_enabled=True,
    )

    assert result is None


@pytest.mark.asyncio
async def test_save_llm_creates_artifact(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        artifacts_service: ArtifactsService
):
    monkeypatch.setattr(
        settings,
        "artifacts",
        ArtifactsConfig(llm_enabled=True, llm_dir=tmp_path)
    )

    aid = await artifacts_service.save_llm(
        prompt="hello",
        response="world",
        prompt_system="sys",
        cost_report=CostReportSchema(
            model="x",
            prompt_tokens=1,
            completion_tokens=1,
            input_cost=0.1,
            output_cost=0.2,
            total_cost=0.3,
        )
    )

    assert aid is not None
    file = tmp_path / f"{aid}.json"
    assert file.exists()

    async with aiofiles.open(file, "r", encoding="utf-8") as f:
        data = json.loads(await f.read())

    assert data["data"]["prompt"] == "hello"
    assert data["data"]["response"] == "world"
    assert data["data"]["prompt_system"] == "sys"
    assert data["data"]["cost_report"]["total_cost"] == 0.3


@pytest.mark.asyncio
async def test_save_llm_disabled(monkeypatch: pytest.MonkeyPatch, artifacts_service: ArtifactsService):
    monkeypatch.setattr(settings, "artifacts", ArtifactsConfig(llm_enabled=False))

    out = await artifacts_service.save_llm(prompt="x", response="y", prompt_system="sys")
    assert out is None


@pytest.mark.asyncio
async def test_save_vcs_inline(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        artifacts_service: ArtifactsService
):
    monkeypatch.setattr(
        settings,
        "artifacts",
        ArtifactsConfig(vcs_enabled=True, vcs_dir=tmp_path)
    )

    comment = InlineCommentSchema(file="a.py", line=10, message="x")

    aid = await artifacts_service.save_vcs_inline(comment)
    assert aid is not None

    file = tmp_path / f"{aid}.json"
    assert file.exists()

    async with aiofiles.open(file, "r", encoding="utf-8") as f:
        data = json.loads(await f.read())

    assert data["type"] == "VCS_INLINE"
    assert data["data"]["inline_comment"]["file"] == "a.py"


@pytest.mark.asyncio
async def test_save_vcs_summary(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        artifacts_service: ArtifactsService
):
    monkeypatch.setattr(
        settings,
        "artifacts",
        ArtifactsConfig(vcs_enabled=True, vcs_dir=tmp_path),
    )

    summary_comment = SummaryCommentSchema(text="hello")
    artifact_id = await artifacts_service.save_vcs_summary(summary_comment)

    assert artifact_id is not None

    artifact_path = tmp_path / f"{artifact_id}.json"
    assert artifact_path.exists()

    async with aiofiles.open(artifact_path, "r", encoding="utf-8") as file:
        json_data = json.loads(await file.read())

    assert json_data["type"] == "VCS_SUMMARY"
    assert json_data["data"]["summary_comment"]["text"] == "hello"


@pytest.mark.asyncio
async def test_save_vcs_inline_reply(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        artifacts_service: ArtifactsService
):
    monkeypatch.setattr(
        settings,
        "artifacts",
        ArtifactsConfig(vcs_enabled=True, vcs_dir=tmp_path),
    )

    reply = InlineCommentReplySchema(message="ok")
    thread_id = "123"

    artifact_id = await artifacts_service.save_vcs_inline_reply(thread_id, reply)

    artifact_path = tmp_path / f"{artifact_id}.json"
    assert artifact_path.exists()

    async with aiofiles.open(artifact_path, "r", encoding="utf-8") as file:
        json_data = json.loads(await file.read())

    assert json_data["type"] == "VCS_INLINE_REPLY"
    assert json_data["data"]["thread_id"] == "123"
    assert json_data["data"]["inline_comment_reply"]["message"] == "ok"


@pytest.mark.asyncio
async def test_save_vcs_summary_reply(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        artifacts_service: ArtifactsService
):
    monkeypatch.setattr(
        settings,
        "artifacts",
        ArtifactsConfig(vcs_enabled=True, vcs_dir=tmp_path),
    )

    reply = SummaryCommentReplySchema(text="ok")
    thread_id = "xyz"

    artifact_id = await artifacts_service.save_vcs_summary_reply(thread_id, reply)

    artifact_path = tmp_path / f"{artifact_id}.json"
    assert artifact_path.exists()

    async with aiofiles.open(artifact_path, "r", encoding="utf-8") as file:
        json_data = json.loads(await file.read())

    assert json_data["type"] == "VCS_SUMMARY_REPLY"
    assert json_data["data"]["thread_id"] == "xyz"
    assert json_data["data"]["summary_comment_reply"]["text"] == "ok"
