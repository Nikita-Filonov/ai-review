from pathlib import Path

import pytest

from ai_review.services.artifacts.schema.base import BaseArtifactSchema
from ai_review.services.artifacts.service import ArtifactsService
from ai_review.services.artifacts.types import ArtifactsServiceProtocol
from ai_review.services.cost.schema import CostReportSchema
from ai_review.services.review.internal.inline.schema import InlineCommentSchema
from ai_review.services.review.internal.inline_reply.schema import InlineCommentReplySchema
from ai_review.services.review.internal.summary.schema import SummaryCommentSchema
from ai_review.services.review.internal.summary_reply.schema import SummaryCommentReplySchema


class FakeArtifactsService(ArtifactsServiceProtocol):
    def __init__(self):
        self.calls: list[tuple[str, dict]] = []

    async def save(self, artifact: BaseArtifactSchema, artifacts_dir: Path, artifacts_enabled: bool) -> str | None:
        self.calls.append((
            "save",
            {
                "artifact": artifact,
                "artifacts_dir": artifacts_dir,
                "artifacts_enabled": artifacts_enabled,
            }
        ))
        return "fake-id"

    async def save_llm(
            self,
            prompt: str,
            response: str,
            prompt_system: str,
            cost_report: CostReportSchema | None = None
    ) -> str | None:
        self.calls.append((
            "save_llm",
            {
                "prompt": prompt,
                "response": response,
                "prompt_system": prompt_system,
                "cost_report": cost_report,
            }
        ))
        return "fake-llm-id"

    async def save_vcs_inline(self, comment: InlineCommentSchema) -> str | None:
        self.calls.append(("save_vcs_inline", {"comment": comment}))
        return "fake-inline-id"

    async def save_vcs_summary(self, comment: SummaryCommentSchema) -> str | None:
        self.calls.append(("save_vcs_summary", {"comment": comment}))
        return "fake-summary-id"

    async def save_vcs_inline_reply(self, thread_id: str, reply: InlineCommentReplySchema) -> str | None:
        self.calls.append(("save_vcs_inline_reply", {"thread_id": thread_id, "reply": reply}))
        return "fake-inline-reply-id"

    async def save_vcs_summary_reply(self, thread_id: str, reply: SummaryCommentReplySchema) -> str | None:
        self.calls.append(("save_vcs_summary_reply", {"thread_id": thread_id, "reply": reply}))
        return "fake-summary-reply-id"


@pytest.fixture
def fake_artifacts_service() -> FakeArtifactsService:
    return FakeArtifactsService()


@pytest.fixture
def artifacts_service() -> ArtifactsService:
    return ArtifactsService()
