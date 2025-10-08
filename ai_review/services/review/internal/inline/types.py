from typing import Protocol

from ai_review.services.review.internal.inline.schema import InlineCommentListSchema


class InlineCommentServiceProtocol(Protocol):
    def parse_model_output(self, output: str) -> InlineCommentListSchema:
        ...
