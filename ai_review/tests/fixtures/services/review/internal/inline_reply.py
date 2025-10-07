import pytest

from ai_review.services.review.internal.inline_reply.schema import InlineCommentReplySchema
from ai_review.services.review.internal.inline_reply.service import InlineCommentReplyService
from ai_review.services.review.internal.inline_reply.types import InlineCommentReplyServiceProtocol


class FakeInlineCommentReplyService(InlineCommentReplyServiceProtocol):
    def __init__(self, reply: InlineCommentReplySchema | None = None):
        self.calls: list[tuple[str, dict]] = []
        self.reply = reply or InlineCommentReplySchema(message="Looks good!", suggestion="use const instead of var")

    def parse_model_output(self, output: str) -> InlineCommentReplySchema | None:
        self.calls.append(("parse_model_output", {"output": output}))
        return self.reply


@pytest.fixture
def fake_inline_comment_reply_service() -> FakeInlineCommentReplyService:
    return FakeInlineCommentReplyService()


@pytest.fixture
def inline_comment_reply_service() -> InlineCommentReplyService:
    return InlineCommentReplyService()
