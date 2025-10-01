import pytest

from ai_review.services.review.inline.schema import InlineCommentListSchema, InlineCommentSchema
from ai_review.services.review.inline.types import InlineCommentServiceProtocol


class FakeInlineCommentService(InlineCommentServiceProtocol):
    def __init__(self, comments: list[InlineCommentSchema] | None = None):
        self.calls: list[tuple[str, dict]] = []
        self.comments = comments or [
            InlineCommentSchema(file="main.py", line=1, message="Test comment"),
        ]

    def parse_model_output(self, output: str) -> InlineCommentListSchema:
        self.calls.append(("parse_model_output", {"output": output}))
        return InlineCommentListSchema(root=self.comments)

    def try_parse_model_output(self, raw: str) -> InlineCommentListSchema | None:
        self.calls.append(("try_parse_model_output", {"raw": raw}))
        return InlineCommentListSchema(root=self.comments)


@pytest.fixture
def fake_inline_comment_service() -> FakeInlineCommentService:
    return FakeInlineCommentService()
