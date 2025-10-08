import pytest

from ai_review.services.review.internal.summary_reply.schema import SummaryCommentReplySchema
from ai_review.services.review.internal.summary_reply.types import SummaryCommentReplyServiceProtocol


class FakeSummaryCommentReplyService(SummaryCommentReplyServiceProtocol):
    def __init__(self, reply: SummaryCommentReplySchema | None = None):
        self.calls: list[tuple[str, dict]] = []
        self.reply = reply or SummaryCommentReplySchema(text="Overall, the code looks clean and efficient.")

    def parse_model_output(self, output: str) -> SummaryCommentReplySchema:
        self.calls.append(("parse_model_output", {"output": output}))
        return self.reply


@pytest.fixture
def fake_summary_comment_reply_service() -> FakeSummaryCommentReplyService:
    return FakeSummaryCommentReplyService()
