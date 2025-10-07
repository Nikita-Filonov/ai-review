from typing import Protocol

from ai_review.services.review.internal.summary.schema import SummaryCommentSchema


class SummaryCommentServiceProtocol(Protocol):
    def parse_model_output(self, output: str) -> SummaryCommentSchema:
        ...
