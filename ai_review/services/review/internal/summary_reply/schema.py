from ai_review.services.review.internal.summary.schema import SummaryCommentSchema
from ai_review.services.review.internal.summary_reply.tools import format_summary_reply_reference


class SummaryCommentReplySchema(SummaryCommentSchema):
    def body_for_request(self, thread_id: str | int, comment_id: str | int) -> str:
        reference = format_summary_reply_reference(thread_id, comment_id)
        return f"{self.body_with_tag}\n\n{reference}"
