from ai_review.config import settings
from ai_review.libs.asynchronous.gather import bounded_gather
from ai_review.libs.logger import get_logger
from ai_review.services.hook import hook
from ai_review.services.review.inline.schema import InlineCommentListSchema, InlineCommentSchema
from ai_review.services.review.summary.schema import SummaryCommentSchema
from ai_review.services.vcs.types import VCSClientProtocol

logger = get_logger("REVIEW_COMMENT_GATEWAY")


class ReviewCommentGateway:
    def __init__(self, vcs: VCSClientProtocol):
        self.vcs = vcs

    async def has_existing_inline_comments(self) -> bool:
        comments = await self.vcs.get_inline_comments()
        has_comments = any(
            settings.review.inline_tag in comment.body
            for comment in comments
        )
        if has_comments:
            logger.info("Skipping inline review: AI inline comments already exist")

        return has_comments

    async def has_existing_summary_comments(self) -> bool:
        comments = await self.vcs.get_general_comments()
        has_comments = any(
            settings.review.summary_tag in comment.body for comment in comments
        )
        if has_comments:
            logger.info("Skipping summary review: AI summary comment already exists")

        return has_comments

    async def process_inline_comment(self, comment: InlineCommentSchema):
        try:
            await hook.emit_inline_comment_start(comment)
            await self.vcs.create_inline_comment(
                file=comment.file,
                line=comment.line,
                message=comment.body_with_tag,
            )
            await hook.emit_inline_comment_complete(comment)
        except Exception as error:
            logger.exception(
                f"Failed to process inline comment for {comment.file}:{comment.line} — {error}"
            )
            await hook.emit_inline_comment_error(comment)

            logger.warning(f"Falling back to general comment for {comment.file}:{comment.line}")
            await self.process_summary_comment(SummaryCommentSchema(text=comment.fallback_body))

    async def process_summary_comment(self, comment: SummaryCommentSchema):
        try:
            await hook.emit_summary_comment_start(comment)
            await self.vcs.create_general_comment(comment.body_with_tag)
            await hook.emit_summary_comment_complete(comment)
        except Exception as error:
            logger.exception(f"Failed to process summary comment: {comment} — {error}")
            await hook.emit_summary_comment_error(comment)

    async def process_inline_comments(self, comments: InlineCommentListSchema) -> None:
        await bounded_gather([self.process_inline_comment(comment) for comment in comments.root])
