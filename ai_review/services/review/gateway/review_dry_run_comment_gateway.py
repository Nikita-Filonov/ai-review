from ai_review.libs.asynchronous.gather import bounded_gather
from ai_review.libs.logger import get_logger
from ai_review.services.hook import hook
from ai_review.services.review.gateway.review_comment_gateway import ReviewCommentGateway
from ai_review.services.review.internal.inline.schema import InlineCommentListSchema, InlineCommentSchema
from ai_review.services.review.internal.inline_reply.schema import InlineCommentReplySchema
from ai_review.services.review.internal.summary.schema import SummaryCommentSchema
from ai_review.services.review.internal.summary_reply.schema import SummaryCommentReplySchema
from ai_review.services.vcs.types import VCSClientProtocol

logger = get_logger("REVIEW_DRY_RUN_COMMENT_GATEWAY")


class ReviewDryRunCommentGateway(ReviewCommentGateway):
    def __init__(self, vcs: VCSClientProtocol):
        super().__init__(vcs)
        logger.warning("Running in DRY RUN mode — no comments will be posted to VCS")

    async def process_inline_reply(self, thread_id: str, reply: InlineCommentReplySchema) -> None:
        await hook.emit_inline_comment_reply_start(reply)
        logger.info(f"[dry-run] Would create inline reply for thread {thread_id}:\n{reply.body_with_tag}")
        await hook.emit_inline_comment_reply_complete(reply)

    async def process_summary_reply(self, thread_id: str, reply: SummaryCommentReplySchema) -> None:
        await hook.emit_summary_comment_reply_start(reply)
        logger.info(f"[dry-run] Would create summary reply for thread {thread_id}:\n{reply.body_with_tag}")
        await hook.emit_summary_comment_reply_complete(reply)

    async def process_inline_comment(self, comment: InlineCommentSchema) -> None:
        await hook.emit_inline_comment_start(comment)
        logger.info(
            f"[dry-run] Would create inline comment for {comment.file}:{comment.line}:\n{comment.body_with_tag}"
        )
        await hook.emit_inline_comment_complete(comment)

    async def process_summary_comment(self, comment: SummaryCommentSchema) -> None:
        await hook.emit_summary_comment_start(comment)
        logger.info(f"[dry-run] Would create summary comment:\n{comment.body_with_tag}")
        await hook.emit_summary_comment_complete(comment)

    async def process_inline_comments(self, comments: InlineCommentListSchema) -> None:
        await bounded_gather([self.process_inline_comment(comment) for comment in comments.root])
