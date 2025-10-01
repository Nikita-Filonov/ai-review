from typing import Protocol

from ai_review.services.review.inline.schema import InlineCommentListSchema


class InlineCommentServiceProtocol(Protocol):
    def parse_model_output(self, output: str) -> InlineCommentListSchema:
        ...

    def try_parse_model_output(self, raw: str) -> InlineCommentListSchema | None:
        ...
