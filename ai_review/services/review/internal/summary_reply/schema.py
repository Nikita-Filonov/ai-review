from ai_review.config import settings
from ai_review.services.review.internal.summary.schema import SummaryCommentSchema


class SummaryCommentReplySchema(SummaryCommentSchema):
    @property
    def body_with_tag(self):
        return f"{self.text}\n\n{settings.review.summary_reply_tag}"
