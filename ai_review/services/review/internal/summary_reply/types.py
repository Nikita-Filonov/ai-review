from typing import Protocol

from ai_review.services.review.internal.summary_reply.schema import SummaryCommentReplySchema


class SummaryCommentReplyServiceProtocol(Protocol):
    def parse_model_output(self, output: str) -> SummaryCommentReplySchema:
        ...
