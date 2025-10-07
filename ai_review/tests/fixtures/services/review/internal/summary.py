from typing import Any

import pytest

from ai_review.services.review.internal.summary.schema import SummaryCommentSchema
from ai_review.services.review.internal.summary.types import SummaryCommentServiceProtocol


class FakeSummaryCommentService(SummaryCommentServiceProtocol):
    def __init__(self, responses: dict[str, Any] | None = None):
        self.calls: list[tuple[str, dict]] = []
        self.responses = responses or {}

    def parse_model_output(self, output: str) -> SummaryCommentSchema:
        self.calls.append(("parse_model_output", {"output": output}))
        return self.responses.get("parse_model_output", SummaryCommentSchema(text="This is a summary comment"))


@pytest.fixture
def fake_summary_comment_service() -> FakeSummaryCommentService:
    return FakeSummaryCommentService()
