import pytest

from ai_review.services.review.summary.schema import SummaryCommentSchema
from ai_review.services.review.summary.types import SummaryCommentServiceProtocol


class FakeSummaryCommentService(SummaryCommentServiceProtocol):
    def __init__(self, text: str = "This is a summary comment"):
        self.text = text
        self.calls: list[tuple[str, dict]] = []

    def parse_model_output(self, output: str) -> SummaryCommentSchema:
        self.calls.append(("parse_model_output", {"output": output}))
        return SummaryCommentSchema(text=self.text)


@pytest.fixture
def fake_summary_comment_service() -> FakeSummaryCommentService:
    return FakeSummaryCommentService()
